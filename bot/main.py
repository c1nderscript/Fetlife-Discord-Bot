import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
import logging
import random
import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable, Awaitable, cast

import discord
import discord.abc
from aiohttp import web, ClientError, ClientSession
from urllib.parse import urlencode
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Summary,
    generate_latest,
)

from . import (
    storage,
    adapter_client,
    models,
    tasks,
    birthday,
    polling,
    moderation,
    welcome,
)
from .audit import log_action
from .config import get_channel_config, get_guild_config, load_config, save_config
from .rate_limit import TokenBucket
from .telegram_bridge import TelegramBridge


TOKEN = ""
ADAPTER_BASE_URL = "https://adapter:8000"
TELEGRAM_API_ID: Optional[str] = None
TELEGRAM_API_HASH: Optional[str] = None
bot: Optional["FLBot"] = None
MGMT_PORT = 8000
SESSION_SECRET = ""
ADMIN_IDS: set[str] = set()
DISCORD_CLIENT_ID = ""
DISCORD_CLIENT_SECRET = ""
OAUTH_REDIRECT_URI = ""


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - formatting
        base = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(base)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("flbot")


# Session helpers
def sign_session(data: Dict[str, Any], secret: str | None = None) -> str:
    key = (secret or SESSION_SECRET).encode()
    payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    sig = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def verify_session(cookie: str, secret: str | None = None) -> Optional[Dict[str, Any]]:
    key = (secret or SESSION_SECRET).encode()
    try:
        payload, sig = cookie.split(".", 1)
        expected = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return None
        data = json.loads(base64.urlsafe_b64decode(payload.encode()).decode())
        return cast(Dict[str, Any], data)
    except Exception:
        return None


@web.middleware
async def auth_middleware(
    request: web.Request,
    handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    request["user"] = None
    cookie = request.cookies.get("session")
    if cookie:
        data = verify_session(cookie)
        if data and str(data.get("id")) in ADMIN_IDS:
            request["user"] = data
    if request.path in {"/login", "/oauth/callback", "/metrics", "/ready"}:
        return await handler(request)
    if not request["user"]:
        raise web.HTTPFound("/login")
    return await handler(request)


# Metrics
messages_sent = Counter("discord_messages_sent_total", "Messages sent by bot")
fetlife_requests = Counter("fetlife_requests_total", "Requests made to FetLife")
poll_cycle = Summary("poll_cycle_seconds", "Duration of poll cycles")
duplicates_suppressed = Counter(
    "duplicates_suppressed_total", "Duplicate messages not relayed"
)
adapter_tokens = Gauge(
    "adapter_rate_limit_tokens", "Tokens currently available for adapter"
)
bot_tokens = Gauge("bot_rate_limit_tokens", "Tokens currently available for bot")
messages_scheduled = Counter(
    "timed_messages_scheduled_total", "Timed messages scheduled"
)

adapter_bucket = TokenBucket(5, 1)
bot_bucket = TokenBucket(5, 1)

MAX_FAILURES = 3
PAUSE_COOLDOWN = 300

fl_group = app_commands.Group(name="fl", description="FetLife commands")
account_group = app_commands.Group(
    name="account", description="Manage FetLife accounts", parent=fl_group
)
telegram_group = app_commands.Group(
    name="telegram", description="Manage Telegram relays", parent=fl_group
)
admin_group = app_commands.Group(name="role", description="Manage guild roles")
channel_group = app_commands.Group(name="channel", description="Manage guild channels")
reactionrole_group = app_commands.Group(
    name="reactionrole", description="Manage reaction roles"
)
audit_group = app_commands.Group(name="audit", description="Audit log")
poll_group = app_commands.Group(name="poll", description="Poll commands")
mod_group = app_commands.Group(name="mod", description="Moderation commands")
welcome_group = app_commands.Group(
    name="welcome", description="Welcome message commands"
)


async def admin_rate_limit(interaction: discord.Interaction) -> bool:
    cfg = get_guild_config(bot.config, interaction.guild_id)
    rate = int(cfg.get("admin_command_rate", 5))
    per = float(cfg.get("admin_command_per", 60))
    command_name = interaction.command.qualified_name if interaction.command else ""
    key = (interaction.guild_id or 0, command_name)
    mapping = bot.admin_cooldowns.get(key)
    if not mapping or mapping._cooldown.rate != rate or mapping._cooldown.per != per:
        mapping = commands.CooldownMapping.from_cooldown(
            rate, per, commands.BucketType.guild
        )
        bot.admin_cooldowns[key] = mapping
    bucket = mapping.get_bucket(interaction)
    retry_after = bucket.update_rate_limit()
    if retry_after:
        raise app_commands.CommandOnCooldown(mapping._cooldown, retry_after)
    return True


def admin_cooldown() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    return app_commands.check(admin_rate_limit)


async def poll_adapter(db, sub_id: int, data: Dict[str, Any]):
    """Poll adapter with jitter and backoff, caching cursor and deduping."""
    cycle_start = time.perf_counter()
    await adapter_bucket.acquire()
    adapter_tokens.set(adapter_bucket.get_tokens())
    success = True
    channel = None
    try:
        sub = db.get(models.Subscription, sub_id)
        if not sub:
            raise RuntimeError("subscription missing")
        channel = bot.get_channel(sub.channel_id)
        last_seen, last_ids = storage.get_cursor(db, sub_id)
        items: list[dict[str, Any]] = []
        if sub.type == "events":
            items = await adapter_client.fetch_events(
                ADAPTER_BASE_URL, sub.target_id, account_id=sub.account_id
            )
        elif sub.type == "writings":
            items = await adapter_client.fetch_writings(
                ADAPTER_BASE_URL, sub.target_id, account_id=sub.account_id
            )
        elif sub.type == "group_posts":
            items = await adapter_client.fetch_group_posts(
                ADAPTER_BASE_URL, sub.target_id, account_id=sub.account_id
            )
        elif sub.type == "attendees":
            items = await adapter_client.fetch_attendees(
                ADAPTER_BASE_URL, sub.target_id, account_id=sub.account_id
            )
        elif sub.type == "messages":
            items = await adapter_client.fetch_messages(
                ADAPTER_BASE_URL, account_id=sub.account_id
            )
        fetlife_requests.inc()
        new_ids: list[str] = []
        for item in items:
            item_id = str(item.get("id"))
            if not item_id:
                continue
            if storage.has_relayed(db, sub_id, item_id):
                duplicates_suppressed.inc()
                logger.info("duplicate", extra={"sub_id": sub_id, "item": item_id})
                continue
            if sub.type == "events":
                start_dt = None
                if item.get("time"):
                    try:
                        start_dt = datetime.fromisoformat(item["time"])
                    except ValueError:
                        start_dt = None
                storage.upsert_event(
                    db,
                    item_id,
                    item.get("title", ""),
                    start_at=start_dt,
                    permalink=item.get("link"),
                )
            elif sub.type == "attendees":
                storage.upsert_profile(db, item_id, item.get("nickname", ""))
                storage.upsert_rsvp(
                    db,
                    sub.target_id,
                    item_id,
                    item.get("status", ""),
                )
            storage.record_relay(db, sub_id, item_id)
            if isinstance(channel, discord.abc.Messageable) or hasattr(channel, "send"):
                if sub.type == "attendees":
                    embed = discord.Embed(
                        title=item.get("nickname", ""),
                        description=item.get("comment") or "",
                    )
                    if item.get("status"):
                        embed.add_field(name="Status", value=item["status"])
                else:
                    if sub.type == "messages":
                        embed = discord.Embed(description=item.get("text", ""))
                        if item.get("sender"):
                            embed.set_author(name=item["sender"])
                        if item.get("sent"):
                            embed.add_field(name="Sent", value=item["sent"])
                    else:
                        embed = discord.Embed(
                            title=item.get("title", ""), url=item.get("link")
                        )
                        if sub.type == "events" and item.get("time"):
                            embed.add_field(name="Start", value=item["time"])
                        if sub.type in ("writings", "group_posts") and item.get(
                            "published"
                        ):
                            embed.add_field(name="Published", value=item["published"])
                await bot_bucket.acquire()
                bot_tokens.set(bot_bucket.get_tokens())
                await cast(discord.abc.Messageable, channel).send(embed=embed)
                messages_sent.inc()
                if sub.type == "messages" and bot.bridge:
                    try:
                        await bot.bridge.send_to_telegram(
                            sub.channel_id, item.get("text", "")
                        )
                    except Exception:  # pragma: no cover - bridge errors
                        logger.exception("telegram forward failed")
            new_ids.append(item_id)
        if new_ids:
            storage.update_cursor(db, sub_id, datetime.utcnow(), new_ids)
    except ClientError as exc:  # pragma: no cover - network error path
        logger.error("poll_http_error", extra={"sub_id": sub_id, "error": str(exc)})
        success = False
    except Exception as exc:  # pragma: no cover - error path
        logger.error("poll_error", extra={"sub_id": sub_id, "error": str(exc)})
        success = False
    finally:
        poll_cycle.observe(time.perf_counter() - cycle_start)
        adapter_tokens.set(adapter_bucket.get_tokens())
        bot.last_poll = time.time()
    failures = data.get("failures", 0)
    paused_until = data.get("paused_until")
    notified = data.get("notified", False)
    if success:
        failures = 0
        paused_until = None
        notified = False
    else:
        failures += 1

    data["failures"] = failures

    if failures >= MAX_FAILURES:
        if not paused_until:
            paused_until = time.time() + PAUSE_COOLDOWN
        data["paused_until"] = paused_until
        if (
            not notified
            and channel
            and (
                isinstance(channel, discord.abc.Messageable) or hasattr(channel, "send")
            )
        ):
            await bot_bucket.acquire()
            bot_tokens.set(bot_bucket.get_tokens())
            await channel.send("Subscription paused after repeated failures")
            notified = True
        data["notified"] = notified
        bot.sub_status[sub_id] = {
            "failures": failures,
            "paused_until": paused_until,
        }
        run_date = datetime.utcfromtimestamp(paused_until)
    else:
        data.pop("paused_until", None)
        data["notified"] = False
        bot.sub_status[sub_id] = {"failures": failures}
        interval = data.get("interval", 60)
        backoff = data.get("backoff", interval)
        if success:
            backoff = interval
        else:
            backoff = min(backoff * 2, interval * 60)
        jitter = random.uniform(0, interval * 0.1)
        run_in = backoff + jitter
        data["backoff"] = backoff
        run_date = datetime.utcnow() + timedelta(seconds=run_in)

    bot.scheduler.add_job(
        poll_adapter,
        args=[db, sub_id, data],
        id=str(sub_id),
        replace_existing=True,
        run_date=run_date,
    )


class FLBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="/", intents=intents)
        self.db = storage.init_db()
        self.scheduler = AsyncIOScheduler()
        self.config = load_config()
        self.bridge: Optional[TelegramBridge] = None
        if TELEGRAM_API_ID and TELEGRAM_API_HASH:
            self.bridge = TelegramBridge(
                self,
                api_id=int(TELEGRAM_API_ID),
                api_hash=TELEGRAM_API_HASH,
                config=self.config,
            )
        self.last_poll = 0.0
        self.sub_status: Dict[int, Dict[str, Any]] = {}
        self.admin_cooldowns: Dict[tuple[int, str], commands.CooldownMapping] = {}

    async def setup_hook(self) -> None:
        channels = [c.id for c in self.db.query(models.Channel.id).all()]
        for channel_id in channels:
            for sub_id, sub_type, _target, _acct in storage.list_subscriptions(
                self.db, channel_id
            ):
                self.scheduler.add_job(
                    poll_adapter,
                    args=[
                        self.db,
                        sub_id,
                        {"interval": 60, "type": sub_type},
                    ],
                    id=str(sub_id),
                    replace_existing=True,
                    run_date=datetime.utcnow() + timedelta(seconds=1),
                )
        self.tree.add_command(birthday.birthday_group)
        self.tree.add_command(poll_group)
        self.tree.add_command(mod_group)
        self.tree.add_command(welcome_group)
        birthday.schedule(self)
        self.scheduler.start()
        self.loop.create_task(tasks.delete_expired_messages(self))


bot = FLBot()


def main(require_env: bool = True) -> FLBot:
    load_dotenv()
    missing = []
    if not os.getenv("DISCORD_TOKEN"):
        missing.append("DISCORD_TOKEN")
    if not os.getenv("ADAPTER_AUTH_TOKEN"):
        missing.append("ADAPTER_AUTH_TOKEN")
    if not os.getenv("DATABASE_URL"):
        if not (os.getenv("DB_HOST") and os.getenv("DB_NAME")):
            missing.append("database settings (DATABASE_URL or DB_HOST/DB_NAME)")
    if require_env and missing:
        raise SystemExit(
            f"Missing required environment variables: {', '.join(missing)}"
        )
    global TOKEN, ADAPTER_BASE_URL, TELEGRAM_API_ID, TELEGRAM_API_HASH, MGMT_PORT, SESSION_SECRET, ADMIN_IDS, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, OAUTH_REDIRECT_URI
    TOKEN = os.getenv("DISCORD_TOKEN", "")
    ADAPTER_BASE_URL = os.getenv("ADAPTER_BASE_URL", ADAPTER_BASE_URL)
    if not os.getenv("MOCK_ADAPTER") and not ADAPTER_BASE_URL.startswith("https://"):
        raise SystemExit("ADAPTER_BASE_URL must start with https://")
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    MGMT_PORT = int(os.getenv("MGMT_PORT", str(MGMT_PORT)))
    SESSION_SECRET = os.getenv("SESSION_SECRET", SESSION_SECRET)
    ADMIN_IDS = {x for x in os.getenv("ADMIN_IDS", "").split(",") if x}
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
    DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
    OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "")
    return bot


ready_flag = False


@bot.event
async def on_ready() -> None:
    global ready_flag
    ready_flag = True
    logger.info("bot_ready", extra={"user": str(bot.user)})


@bot.event
async def on_member_join(member: discord.Member) -> None:
    logger.info(
        "member_join",
        extra={"guild_id": member.guild.id, "user_id": member.id},
    )
    cfg = welcome.get_config(bot.db, member.guild.id)
    if not cfg:
        return
    channel = member.guild.get_channel(cfg.channel_id)
    if not isinstance(channel, discord.TextChannel):
        return
    msg = cfg.message.replace("{user}", member.mention)
    view = welcome.VerifyView(cfg.verify_role_id) if cfg.verify_role_id else None
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await channel.send(msg, view=view)


@bot.event
async def on_member_remove(member: discord.Member) -> None:
    logger.info(
        "member_leave",
        extra={"guild_id": member.guild.id, "user_id": member.id},
    )


@bot.tree.command(name="timer", description="Send a self-deleting message")
@app_commands.describe(message="Message to send", seconds="Seconds before deletion")
async def timer(
    interaction: discord.Interaction, message: str, seconds: int | None = None
) -> None:
    if interaction.channel_id is None or interaction.channel is None:
        await interaction.response.send_message("Channel only", ephemeral=True)
        return
    if seconds is None:
        settings = storage.get_channel_settings(bot.db, interaction.channel_id)
        seconds = int(settings.get("autodelete", 0))
    if seconds <= 0:
        await interaction.response.send_message(
            "Timer must be positive", ephemeral=True
        )
        return
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(message)
    sent = await interaction.original_response()
    delete_at = datetime.utcnow() + timedelta(seconds=seconds)
    bot.db.add(
        models.TimedMessage(
            message_id=sent.id, channel_id=sent.channel.id, delete_at=delete_at
        )
    )
    bot.db.commit()
    messages_scheduled.inc()


@app_commands.default_permissions(administrator=True)
@log_action("autodelete")
@bot.tree.command(name="autodelete", description="Set channel auto-delete timer")
@app_commands.describe(seconds="Seconds before deletion (0 to disable)")
async def autodelete(interaction: discord.Interaction, seconds: int) -> None:
    if interaction.channel_id is None:
        await interaction.response.send_message("Channel only", ephemeral=True)
        return
    storage.set_channel_settings(bot.db, interaction.channel_id, autodelete=seconds)
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message("Auto-delete updated")


@app_commands.default_permissions(administrator=True)
@log_action("welcome_setup")
@welcome_group.command(name="setup", description="Configure welcome message")
@app_commands.describe(
    channel="Channel for welcome messages",
    message="Welcome message (use {user} to mention)",
    verify_role="Role granted after verification",
    preview="Send a preview to the channel",
)
async def welcome_setup(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str,
    verify_role: discord.Role | None = None,
    preview: bool = False,
) -> None:
    if interaction.guild_id is None:
        await interaction.response.send_message("Guild only", ephemeral=True)
        return
    welcome.set_config(
        bot.db,
        interaction.guild_id,
        channel.id,
        message,
        verify_role.id if verify_role else None,
    )
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message("Welcome configuration saved")
    if preview:
        view = welcome.VerifyView(verify_role.id) if verify_role else None
        msg = message.replace("{user}", interaction.user.mention)
        await channel.send(msg, view=view)


@fl_group.command(name="login", description="Validate adapter service connectivity")
@log_action("login")
async def fl_login(interaction: discord.Interaction) -> None:
    try:
        ok = await adapter_client.login_adapter(ADAPTER_BASE_URL)
        msg = "Adapter login successful" if ok else "Adapter login failed"
    except ClientError as exc:  # pragma: no cover - network error path
        msg = f"Adapter login failed: {exc}"
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(msg)


@account_group.command(name="add", description="Add a FetLife account")
@app_commands.default_permissions(administrator=True)
@log_action("account_add", target_param="username")
async def fl_account_add(
    interaction: discord.Interaction, username: str, password: str
) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "administrator", False
        ):
            raise PermissionError("Administrator permissions required")
        acct_id = storage.add_account(bot.db, username, password)
        await adapter_client.login(
            ADAPTER_BASE_URL, username, password, account_id=acct_id
        )
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(f"Account {acct_id} added")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@account_group.command(name="list", description="List stored accounts")
@log_action("account_list")
async def fl_account_list(interaction: discord.Interaction) -> None:
    accounts = storage.list_accounts(bot.db)
    if not accounts:
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("No accounts")
        return
    desc = "\n".join(f"`{aid}` {name}" for aid, name in accounts)
    embed = discord.Embed(title="Accounts", description=desc)
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(embed=embed)


@account_group.command(name="remove", description="Remove an account")
@app_commands.default_permissions(administrator=True)
@log_action("account_remove", target_param="account_id")
async def fl_account_remove(interaction: discord.Interaction, account_id: int) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "administrator", False
        ):
            raise PermissionError("Administrator permissions required")
        storage.remove_account(bot.db, account_id)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(f"Removed account {account_id}")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@telegram_group.command(name="add", description="Relay a Telegram chat to a channel")
@app_commands.default_permissions(administrator=True)
@log_action("telegram_add", target_param="chat_id")
async def fl_telegram_add(
    interaction: discord.Interaction, chat_id: str, channel: discord.TextChannel
) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "administrator", False
        ):
            raise PermissionError("Administrator permissions required")
        if not bot.bridge:
            raise RuntimeError("Telegram bridge not configured")
        bot.bridge.add_mapping(int(chat_id), channel.id)
        bot.config.setdefault("telegram_bridge", {}).setdefault("mappings", {})[
            str(chat_id)
        ] = str(channel.id)
        save_config(bot.config)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Added Telegram relay")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@telegram_group.command(name="remove", description="Stop relaying a Telegram chat")
@app_commands.default_permissions(administrator=True)
@log_action("telegram_remove", target_param="chat_id")
async def fl_telegram_remove(interaction: discord.Interaction, chat_id: str) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "administrator", False
        ):
            raise PermissionError("Administrator permissions required")
        if not bot.bridge:
            raise RuntimeError("Telegram bridge not configured")
        bot.bridge.remove_mapping(int(chat_id))
        bot.config.get("telegram_bridge", {}).get("mappings", {}).pop(
            str(chat_id), None
        )
        save_config(bot.config)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Removed Telegram relay")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@telegram_group.command(name="list", description="Show active Telegram relays")
@log_action("telegram_list")
async def fl_telegram_list(interaction: discord.Interaction) -> None:
    mappings = bot.bridge.mappings if bot.bridge else {}
    if mappings:
        desc = "\n".join(f"{cid} -> <#{chan}>" for cid, chan in mappings.items())
    else:
        desc = "No Telegram relays configured"
    embed = discord.Embed(title="Telegram Relays", description=desc)
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(embed=embed)


@fl_group.command(name="subscribe", description="Create a new subscription")
@app_commands.describe(
    sub_type="Type of content to subscribe to",
    target="Target identifier: user:<nickname> for writings, location:<...> for events, group:<id> for group posts, event:<id> for attendees, inbox for messages",
    filters="Optional JSON filters",
    account="ID of stored account to use",
)
@app_commands.choices(
    sub_type=[
        app_commands.Choice(name="events", value="events"),
        app_commands.Choice(name="writings", value="writings"),
        app_commands.Choice(name="group_posts", value="group_posts"),
        app_commands.Choice(name="attendees", value="attendees"),
        app_commands.Choice(name="messages", value="messages"),
    ]
)
@log_action("subscribe", target_param="target")
async def fl_subscribe(
    interaction: discord.Interaction,
    sub_type: str,
    target: str,
    filters: str | None = None,
    account: int | None = None,
) -> None:
    """Subscribe channel to FetLife events, writings, group posts, attendees, or messages.

    target formats: `user:<nickname>` for writings, `location:<...>` for events,
    `group:<id>` for group posts, `event:<id>` for attendees, `inbox` for messages.
    """
    if filters:
        try:
            filters_json = json.loads(filters)
        except json.JSONDecodeError:
            await bot_bucket.acquire()
            bot_tokens.set(bot_bucket.get_tokens())
            await interaction.response.send_message("Invalid JSON for filters")
            return
    else:
        filters_json = {}
    if sub_type == "group_posts" and not re.fullmatch(r"group:\d+", target):
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Target must be group:<id>")
        return
    channel_id = interaction.channel_id
    if channel_id is None:
        await interaction.response.send_message("Channel not found")
        return
    sub_id = storage.add_subscription(
        bot.db,
        channel_id,
        sub_type,
        target,
        filters_json,
        account_id=account,
    )
    sub = bot.db.get(models.Subscription, sub_id)
    bot.scheduler.add_job(
        poll_adapter,
        args=[bot.db, sub_id, {"interval": 60, "type": sub.type if sub else sub_type}],
        id=str(sub_id),
    )
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(f"Subscribed with id {sub_id}")


@fl_group.command(name="list", description="List channel subscriptions")
@log_action("subscription_list")
async def fl_list(interaction: discord.Interaction) -> None:
    channel_id = interaction.channel_id
    if channel_id is None:
        await interaction.response.send_message("Channel not found")
        return
    subs = storage.list_subscriptions(bot.db, channel_id)
    if not subs:
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("No subscriptions")
        return
    desc = "\n".join(f"`{sid}` {typ} {tgt} (acct {aid})" for sid, typ, tgt, aid in subs)
    embed = discord.Embed(title="Subscriptions", description=desc)
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(embed=embed)


@fl_group.command(name="unsubscribe", description="Remove a subscription")
@log_action("unsubscribe", target_param="sub_id")
async def fl_unsubscribe(interaction: discord.Interaction, sub_id: int) -> None:
    channel_id = interaction.channel_id
    if channel_id is None:
        await interaction.response.send_message("Channel not found")
        return
    storage.remove_subscription(bot.db, sub_id, channel_id)
    try:
        bot.scheduler.remove_job(str(sub_id))
    except Exception:
        pass
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(f"Unsubscribed {sub_id}")


@fl_group.command(name="test", description="Preview an embed")
@log_action("test", target_param="sub_id")
async def fl_test(interaction: discord.Interaction, sub_id: int) -> None:
    embed = discord.Embed(title="Test Notification", description=f"sub {sub_id}")
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(embed=embed)
    messages_sent.inc()
    channel_id = interaction.channel_id
    if channel_id is None:
        return
    db_settings = storage.get_channel_settings(bot.db, channel_id)
    cfg = get_channel_config(bot.config, interaction.guild_id, channel_id)
    settings = {**db_settings, **cfg}
    if settings.get("thread_per_event"):
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.followup.send("Thread created", ephemeral=True)


@fl_group.command(name="settings", description="Per-channel configuration")
@log_action("settings")
async def fl_settings(
    interaction: discord.Interaction, key: str | None = None, value: str | None = None
) -> None:
    channel_id = interaction.channel_id
    if channel_id is None:
        await interaction.response.send_message("Channel not found")
        return
    if key and value:
        storage.set_channel_settings(bot.db, channel_id, **{key: value})
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Updated settings")
    else:
        db_settings = storage.get_channel_settings(bot.db, channel_id)
        cfg = get_channel_config(bot.config, interaction.guild_id, channel_id)
        settings = {**db_settings, **cfg}
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(json.dumps(settings or {}))


@fl_group.command(name="health", description="Show adapter health")
@log_action("health", target_param="resume")
async def fl_health(
    interaction: discord.Interaction, resume: int | None = None
) -> None:
    if resume is not None:
        job = bot.scheduler.get_job(str(resume))
        if job:
            data = job.args[2]
            data["failures"] = 0
            data.pop("paused_until", None)
            data["notified"] = False
            bot.sub_status[resume] = {"failures": 0}
            bot.scheduler.add_job(
                poll_adapter,
                args=[bot.db, resume, data],
                id=str(resume),
                replace_existing=True,
                run_date=datetime.utcnow() + timedelta(seconds=1),
            )
            msg = f"Resumed subscription {resume}"
        else:
            msg = f"Subscription {resume} not found"
    else:
        depth = len(bot.scheduler.get_jobs())
        last = (
            datetime.utcfromtimestamp(bot.last_poll).isoformat()
            if bot.last_poll
            else "never"
        )
        status_lines = []
        for sid, s in bot.sub_status.items():
            line = f"{sid}: {s['failures']} fails"
            if s.get("paused_until"):
                until = datetime.utcfromtimestamp(s["paused_until"]).isoformat()
                line += f", paused until {until}"
            status_lines.append(line)
        status = "; ".join(status_lines) if status_lines else "ok"
        msg = f"last_poll: {last}; queue_depth: {depth}; status: {status}"
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(msg)


@fl_group.command(name="purge", description="Purge local caches")
@app_commands.default_permissions(administrator=True)
@log_action("purge")
async def fl_purge(interaction: discord.Interaction) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "administrator", False
        ):
            raise PermissionError("Administrator permissions required")
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Purged")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@admin_cooldown()
@channel_group.command(name="create", description="Create a text channel")
@app_commands.default_permissions(manage_channels=True)
@app_commands.describe(name="Name for the new channel")
@log_action("channel_create", target_param="name")
async def channel_create(interaction: discord.Interaction, name: str) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None),
            "manage_channels",
            False,
        ):
            raise PermissionError("Manage Channels permission required")
        guild = interaction.guild
        if guild is None:
            raise RuntimeError("Guild not found")
        await guild.create_text_channel(name)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Channel created")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@admin_cooldown()
@channel_group.command(name="delete", description="Delete a text channel")
@app_commands.default_permissions(manage_channels=True)
@app_commands.describe(channel="Channel to delete")
@log_action("channel_delete", target_param="channel")
async def channel_delete(
    interaction: discord.Interaction, channel: discord.TextChannel
) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None),
            "manage_channels",
            False,
        ):
            raise PermissionError("Manage Channels permission required")
        await channel.delete()
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Channel deleted")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@admin_cooldown()
@channel_group.command(name="rename", description="Rename a text channel")
@app_commands.default_permissions(manage_channels=True)
@app_commands.describe(channel="Channel to rename", name="New channel name")
@log_action("channel_rename", target_param="channel")
async def channel_rename(
    interaction: discord.Interaction, channel: discord.TextChannel, name: str
) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None),
            "manage_channels",
            False,
        ):
            raise PermissionError("Manage Channels permission required")
        await channel.edit(name=name)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Channel renamed")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@admin_cooldown()
@admin_group.command(name="add", description="Add a role to a member")
@app_commands.default_permissions(manage_roles=True)
@log_action("role_add", target_param="role_id")
async def role_add(
    interaction: discord.Interaction, member: discord.Member, role_id: int
) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "manage_roles", False
        ):
            raise PermissionError("Manage Roles permission required")
        guild = interaction.guild
        if guild is None:
            raise RuntimeError("Guild not found")
        role = guild.get_role(role_id)
        if role is None:
            raise ValueError("Role not found")
        await member.add_roles(role)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Role added")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@admin_cooldown()
@admin_group.command(name="remove", description="Remove a role from a member")
@app_commands.default_permissions(manage_roles=True)
@log_action("role_remove", target_param="role_id")
async def role_remove(
    interaction: discord.Interaction, member: discord.Member, role_id: int
) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "manage_roles", False
        ):
            raise PermissionError("Manage Roles permission required")
        guild = interaction.guild
        if guild is None:
            raise RuntimeError("Guild not found")
        role = guild.get_role(role_id)
        if role is None:
            raise ValueError("Role not found")
        await member.remove_roles(role)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Role removed")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@admin_cooldown()
@admin_group.command(name="list", description="List guild roles")
@app_commands.default_permissions(manage_roles=True)
@log_action("role_list")
async def role_list(interaction: discord.Interaction) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "manage_roles", False
        ):
            raise PermissionError("Manage Roles permission required")
        guild = interaction.guild
        if guild is None:
            raise RuntimeError("Guild not found")
        roles = getattr(guild, "roles", []) or []
        desc = "\n".join(f"`{r.id}` {r.name}" for r in roles) if roles else "No roles"
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(desc)
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@admin_cooldown()
@reactionrole_group.command(name="add", description="Add a reaction role mapping")
@app_commands.default_permissions(manage_roles=True)
@log_action("reactionrole_add", target_param="message_id")
async def reactionrole_add(
    interaction: discord.Interaction, message_id: int, emoji: str, role_id: int
) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "manage_roles", False
        ):
            raise PermissionError("Manage Roles permission required")
        guild = interaction.guild
        if guild is None:
            raise RuntimeError("Guild not found")
        role = guild.get_role(role_id)
        if role is None:
            raise ValueError("Role not found")
        storage.set_reaction_role(bot.db, message_id, emoji, role_id, guild.id)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Reaction role added")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@admin_cooldown()
@reactionrole_group.command(name="remove", description="Remove a reaction role mapping")
@app_commands.default_permissions(manage_roles=True)
@log_action("reactionrole_remove", target_param="message_id")
async def reactionrole_remove(
    interaction: discord.Interaction, message_id: int, emoji: str
) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "manage_roles", False
        ):
            raise PermissionError("Manage Roles permission required")
        storage.remove_reaction_role(bot.db, message_id, emoji)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Reaction role removed")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@audit_group.command(name="search", description="Search audit log")
@app_commands.describe(
    user="Filter by user ID", action="Filter by action", limit="Max results"
)
@app_commands.default_permissions(administrator=True)
@log_action("audit_search")
async def audit_search(
    interaction: discord.Interaction,
    user: Optional[int] = None,
    action: Optional[str] = None,
    limit: int = 20,
) -> None:
    query = bot.db.query(models.AuditLog).order_by(models.AuditLog.id.desc())
    if user is not None:
        query = query.filter(models.AuditLog.user_id == user)
    if action is not None:
        query = query.filter(models.AuditLog.action == action)
    rows = query.limit(limit).all()
    desc = (
        "\n".join(f"{r.id} {r.user_id} {r.action} {r.target}" for r in rows)
        or "No results"
    )
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(desc, ephemeral=True)


@poll_group.command(name="create", description="Create a poll")
@app_commands.describe(
    question="Question to ask",
    poll_type="Type of poll",
    options="Semicolon-separated options for multiple or ranked",
    duration="Seconds until auto-close",
)
@app_commands.choices(
    poll_type=[
        app_commands.Choice(name="yes/no", value="yesno"),
        app_commands.Choice(name="multiple choice", value="multiple"),
        app_commands.Choice(name="ranked", value="ranked"),
    ]
)
async def poll_create(
    interaction: discord.Interaction,
    question: str,
    poll_type: app_commands.Choice[str],
    options: str | None = None,
    duration: int | None = None,
) -> None:
    opts = [o.strip() for o in (options or "").split(";") if o.strip()]
    if poll_type.value == "yesno":
        opts = ["Yes", "No"]
    elif not opts:
        await interaction.response.send_message("options required", ephemeral=True)
        return
    closes_at = (
        datetime.utcnow() + timedelta(seconds=duration)
        if duration and duration > 0
        else None
    )
    db = storage.init_db()
    poll = polling.create_poll(
        db,
        question,
        poll_type.value,
        opts,
        interaction.user.id,
        interaction.channel_id,
        closes_at,
    )
    db.close()
    content = f"**{question}**\n" + "\n".join(
        f"{i + 1}. {opt}" for i, opt in enumerate(opts)
    )
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    msg = await interaction.channel.send(content)
    if poll_type.value == "yesno":
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
    else:

        class PollButton(discord.ui.Button):
            def __init__(self, idx: int, label: str) -> None:
                super().__init__(label=label, custom_id=f"poll:{poll.id}:{idx}")
                self.idx = idx

            async def callback(self, btn_inter: discord.Interaction) -> None:
                dbi = storage.init_db()
                try:
                    polling.record_vote(dbi, poll.id, btn_inter.user.id, self.idx)
                finally:
                    dbi.close()
                await btn_inter.response.send_message("Vote recorded", ephemeral=True)

        class PollView(discord.ui.View):
            def __init__(self) -> None:
                super().__init__(timeout=None)
                for i, opt in enumerate(opts):
                    self.add_item(PollButton(i, opt))

        view = PollView()
        await msg.edit(view=view)
    db = storage.init_db()
    try:
        polling.set_message(db, poll.id, msg.id)
    finally:
        db.close()
    if closes_at:
        polling.schedule_close(bot, poll.id, closes_at)
    await interaction.response.send_message(f"Created poll {poll.id}", ephemeral=True)


@poll_group.command(name="close", description="Close a poll")
async def poll_close(interaction: discord.Interaction, poll_id: int) -> None:
    db = storage.init_db()
    poll = db.get(polling.Poll, poll_id)
    if not poll:
        db.close()
        await interaction.response.send_message("poll not found", ephemeral=True)
        return
    polling.close_poll(db, poll_id)
    db.close()
    channel = bot.get_channel(poll.channel_id)
    if hasattr(channel, "fetch_message") and poll.message_id:
        try:
            msg = await channel.fetch_message(poll.message_id)
            await msg.edit(view=None)
        except Exception:
            pass
    await interaction.response.send_message("Poll closed", ephemeral=True)


@poll_group.command(name="results", description="Show poll results")
async def poll_results_cmd(interaction: discord.Interaction, poll_id: int) -> None:
    db = storage.init_db()
    results = polling.poll_results(db, poll_id)
    db.close()
    if not results:
        await interaction.response.send_message("poll not found", ephemeral=True)
        return
    lines = [f"{opt}: {count}" for opt, count in results.items()]
    await interaction.response.send_message("\n".join(lines), ephemeral=True)


@poll_group.command(name="list", description="List active polls")
async def poll_list(interaction: discord.Interaction) -> None:
    db = storage.init_db()
    polls = polling.list_polls(db)
    db.close()
    if not polls:
        await interaction.response.send_message("No active polls", ephemeral=True)
        return
    lines = [f"{p.id}: {p.question}" for p in polls]
    await interaction.response.send_message("\n".join(lines), ephemeral=True)


@mod_group.command(name="warn", description="Warn a user")
@app_commands.describe(user="Member to warn", reason="Reason")
@app_commands.default_permissions(moderate_members=True)
@log_action("warn", target_param="user")
async def mod_warn(
    interaction: discord.Interaction,
    user: discord.Member,
    reason: str | None = None,
) -> None:
    if not getattr(
        getattr(interaction.user, "guild_permissions", None), "moderate_members", False
    ):
        await interaction.response.send_message(
            "Moderate Members permission required", ephemeral=True
        )
        return
    db = storage.init_db()
    try:
        moderation.add_infraction(
            db,
            interaction.guild_id,
            user.id,
            interaction.user.id,
            moderation.InfractionType.WARN,
            reason,
        )
        escalate = moderation.escalate(db, interaction.guild_id, user.id)
    finally:
        db.close()
    if escalate == moderation.InfractionType.MUTE:
        await user.timeout(timedelta(minutes=10), reason="Auto escalation")
        db2 = storage.init_db()
        try:
            moderation.add_infraction(
                db2,
                interaction.guild_id,
                user.id,
                interaction.user.id,
                moderation.InfractionType.MUTE,
                "Auto escalation",
            )
        finally:
            db2.close()
        msg = f"{user.mention} warned and muted"
    else:
        msg = f"{user.mention} warned"
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(msg, ephemeral=True)


@mod_group.command(name="mute", description="Mute a user")
@app_commands.describe(
    user="Member to mute", minutes="Minutes to mute", reason="Reason"
)
@app_commands.default_permissions(moderate_members=True)
@log_action("mute", target_param="user")
async def mod_mute(
    interaction: discord.Interaction,
    user: discord.Member,
    minutes: int = 10,
    reason: str | None = None,
) -> None:
    if not getattr(
        getattr(interaction.user, "guild_permissions", None), "moderate_members", False
    ):
        await interaction.response.send_message(
            "Moderate Members permission required", ephemeral=True
        )
        return
    await user.timeout(timedelta(minutes=minutes), reason=reason)
    db = storage.init_db()
    try:
        moderation.add_infraction(
            db,
            interaction.guild_id,
            user.id,
            interaction.user.id,
            moderation.InfractionType.MUTE,
            reason,
            datetime.utcnow() + timedelta(minutes=minutes),
        )
    finally:
        db.close()
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(f"{user.mention} muted", ephemeral=True)


@mod_group.command(name="kick", description="Kick a user")
@app_commands.describe(user="Member to kick", reason="Reason")
@app_commands.default_permissions(kick_members=True)
@log_action("kick", target_param="user")
async def mod_kick(
    interaction: discord.Interaction,
    user: discord.Member,
    reason: str | None = None,
) -> None:
    await interaction.guild.kick(user, reason=reason)
    db = storage.init_db()
    try:
        moderation.add_infraction(
            db,
            interaction.guild_id,
            user.id,
            interaction.user.id,
            moderation.InfractionType.KICK,
            reason,
        )
    finally:
        db.close()
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(f"{user.mention} kicked", ephemeral=True)


@mod_group.command(name="ban", description="Ban a user")
@app_commands.describe(user="Member to ban", reason="Reason")
@app_commands.default_permissions(ban_members=True)
@log_action("ban", target_param="user")
async def mod_ban(
    interaction: discord.Interaction,
    user: discord.Member,
    reason: str | None = None,
) -> None:
    await interaction.guild.ban(user, reason=reason)
    db = storage.init_db()
    try:
        moderation.add_infraction(
            db,
            interaction.guild_id,
            user.id,
            interaction.user.id,
            moderation.InfractionType.BAN,
            reason,
        )
    finally:
        db.close()
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(f"{user.mention} banned", ephemeral=True)


@mod_group.command(name="timeout", description="Timeout a user")
@app_commands.describe(
    user="Member to timeout", minutes="Minutes to timeout", reason="Reason"
)
@app_commands.default_permissions(moderate_members=True)
@log_action("timeout", target_param="user")
async def mod_timeout(
    interaction: discord.Interaction,
    user: discord.Member,
    minutes: int,
    reason: str | None = None,
) -> None:
    if minutes <= 0:
        await interaction.response.send_message("minutes must be > 0", ephemeral=True)
        return
    await user.timeout(timedelta(minutes=minutes), reason=reason)
    db = storage.init_db()
    try:
        moderation.add_infraction(
            db,
            interaction.guild_id,
            user.id,
            interaction.user.id,
            moderation.InfractionType.TIMEOUT,
            reason,
            datetime.utcnow() + timedelta(minutes=minutes),
        )
    finally:
        db.close()
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(f"{user.mention} timed out", ephemeral=True)


@mod_group.command(name="modlog", description="Show a user's infractions")
@app_commands.describe(user="Member to query")
@app_commands.default_permissions(moderate_members=True)
@log_action("modlog", target_param="user")
async def mod_modlog(interaction: discord.Interaction, user: discord.Member) -> None:
    db = storage.init_db()
    try:
        rows = moderation.list_infractions(db, interaction.guild_id, user.id)
    finally:
        db.close()
    lines = [f"{r.type} {r.reason or ''}" for r in rows] or ["No infractions"]
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message("\n".join(lines), ephemeral=True)


@mod_group.command(name="purge", description="Delete messages with optional filters")
@app_commands.describe(
    limit="Max messages to search",
    user="Only delete from user",
    contains="Only delete containing text",
)
@app_commands.default_permissions(manage_messages=True)
@log_action("purge")
async def mod_purge(
    interaction: discord.Interaction,
    limit: int = 100,
    user: Optional[discord.User] = None,
    contains: Optional[str] = None,
) -> None:
    def check(msg: discord.Message) -> bool:
        if user and msg.author.id != user.id:
            return False
        if contains and contains not in msg.content:
            return False
        return True

    deleted = await interaction.channel.purge(limit=limit, check=check)
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(
        f"Deleted {len(deleted)} messages", ephemeral=True
    )


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    info = storage.get_reaction_role(bot.db, payload.message_id, str(payload.emoji))
    if not info or payload.guild_id != info[1]:
        return
    guild = bot.get_guild(info[1])
    if guild is None:
        return
    role = guild.get_role(info[0])
    member = guild.get_member(payload.user_id) if role else None
    if member is None:
        return
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
    info = storage.get_reaction_role(bot.db, payload.message_id, str(payload.emoji))
    if not info or payload.guild_id != info[1]:
        return
    guild = bot.get_guild(info[1])
    if guild is None:
        return
    role = guild.get_role(info[0])
    member = guild.get_member(payload.user_id) if role else None
    if member is None:
        return
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await member.remove_roles(role)


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User) -> None:
    if user.bot:
        return
    db = storage.init_db()
    try:
        poll = (
            db.query(polling.Poll)
            .filter_by(message_id=reaction.message.id, closed=False)
            .first()
        )
        if not poll:
            return
        choice = (
            0
            if str(reaction.emoji) == "👍"
            else 1 if str(reaction.emoji) == "👎" else None
        )
        if choice is None:
            return
        polling.record_vote(db, poll.id, user.id, choice)
    finally:
        db.close()


async def login(request: web.Request) -> web.Response:
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify",
    }
    raise web.HTTPFound("https://discord.com/api/oauth2/authorize?" + urlencode(params))


async def oauth_callback(request: web.Request) -> web.Response:
    code = request.query.get("code")
    if not code:
        return web.Response(status=400, text="missing code")
    async with ClientSession() as session:
        data = {
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": OAUTH_REDIRECT_URI,
        }
        async with session.post(
            "https://discord.com/api/oauth2/token", data=data
        ) as resp:
            token_data = await resp.json()
        access = token_data.get("access_token")
        if not access:
            return web.Response(status=400, text="invalid token")
        async with session.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access}"},
        ) as resp:
            user = await resp.json()
    if str(user.get("id")) not in ADMIN_IDS:
        return web.Response(status=403, text="unauthorized")
    resp = web.HTTPFound("/")
    resp.set_cookie(
        "session",
        sign_session({"id": user["id"], "username": user.get("username", "")}),
        httponly=True,
        max_age=3600,
    )
    return resp


async def logout(request: web.Request) -> web.Response:
    resp = web.HTTPFound("/login")
    resp.del_cookie("session")
    return resp


async def metrics_handler(request: web.Request) -> web.Response:
    data = generate_latest()
    return web.Response(body=data, content_type=CONTENT_TYPE_LATEST)


async def ready_handler(request: web.Request) -> web.Response:
    if ready_flag:
        return web.Response(text="ok")
    return web.Response(status=503, text="not ready")


def create_management_app(db) -> web.Application:
    app = web.Application(middlewares=[auth_middleware])

    async def index(request: web.Request) -> web.Response:
        return web.Response(
            text=(
                "<h1>Management</h1><ul>"
                "<li><a href='/subscriptions'>Subscriptions</a></li>"
                "<li><a href='/roles'>Roles</a></li>"
                "<li><a href='/channels'>Channels</a></li>"
                "<li><a href='/birthdays'>Birthdays</a></li>"
                "<li><a href='/polls'>Polls</a></li>"
                "<li><a href='/timed-messages'>Timed Messages</a></li>"
                "<li><a href='/welcome'>Welcome</a></li>"
                "<li><a href='/appeals'>Appeals</a></li>"
                "<li><a href='/audit'>Audit Log</a></li>"
                "</ul>"
            ),
            content_type="text/html",
        )

    async def subscriptions_page(request: web.Request) -> web.Response:
        subs = db.query(models.Subscription).all()
        rows = "".join(
            f"<li>{s.id} {s.type} {s.target_id}<form method='post' action='/subscriptions/{s.id}/delete'><button>Delete</button></form></li>"
            for s in subs
        )
        return web.Response(
            text=f"<h1>Subscriptions</h1><ul>{rows}</ul>",
            content_type="text/html",
        )

    async def subscription_delete(request: web.Request) -> web.Response:
        sub_id = int(request.match_info["sub_id"])
        db.query(models.Subscription).filter(models.Subscription.id == sub_id).delete()
        db.commit()
        raise web.HTTPFound("/subscriptions")

    async def birthdays_page(request: web.Request) -> web.Response:
        rows = db.query(birthday.Birthday).all()
        items = "".join(
            f"<li>{r.guild_id}:{r.user_id} {r.date} {r.timezone}</li>" for r in rows
        )
        return web.Response(
            text=f"<h1>Birthdays</h1><ul>{items}</ul>", content_type="text/html"
        )

    async def roles_page(request: web.Request) -> web.Response:
        roles = db.query(models.ReactionRole).all()
        rows = "".join(
            f"<li>{r.message_id} {r.emoji} {r.role_id}<form method='post' action='/roles/remove'><input type='hidden' name='message_id' value='{r.message_id}'/><input type='hidden' name='emoji' value='{r.emoji}'/><button>Remove</button></form></li>"
            for r in roles
        )
        return web.Response(
            text=f"<h1>Roles</h1><ul>{rows}</ul>",
            content_type="text/html",
        )

    async def roles_remove(request: web.Request) -> web.Response:
        data = await request.post()
        message_id = int(data.get("message_id", 0))
        emoji = data.get("emoji", "")
        storage.remove_reaction_role(db, message_id, emoji)
        raise web.HTTPFound("/roles")

    async def audit_page(request: web.Request) -> web.Response:
        logs = (
            db.query(models.AuditLog)
            .order_by(models.AuditLog.id.desc())
            .limit(100)
            .all()
        )
        rows = "".join(
            f"<li>{log.created_at} {log.user_id} {log.action} {log.target}</li>"
            for log in logs
        )
        return web.Response(
            text=f"<h1>Audit Log</h1><ul>{rows}</ul>",
            content_type="text/html",
        )

    async def channels_page(request: web.Request) -> web.Response:
        channels = db.query(models.Channel).all()
        rows = "".join(
            f"<li>{c.id} {c.name or ''}<form method='post' action='/channels/{c.id}/settings'><input type='text' name='settings' value='{json.dumps(c.settings_json or {})}'/><button>Save</button></form></li>"
            for c in channels
        )
        return web.Response(
            text=f"<h1>Channels</h1><ul>{rows}</ul>",
            content_type="text/html",
        )

    async def channel_settings(request: web.Request) -> web.Response:
        channel_id = int(request.match_info["channel_id"])
        data = await request.post()
        try:
            settings = (
                json.loads(data.get("settings", "{}")) if data.get("settings") else {}
            )
        except Exception:
            return web.Response(status=400, text="invalid settings")
        channel = db.get(models.Channel, channel_id)
        if not channel:
            return web.Response(status=404, text="not found")
        channel.settings_json = settings
        db.commit()
        raise web.HTTPFound("/channels")

    async def polls_page(request: web.Request) -> web.Response:
        polls = polling.list_polls(db, active_only=False)
        rows = "".join(f"<li>{p.id} {p.question}</li>" for p in polls)
        form = (
            "<form method='post'>"
            "Question:<input name='question'/><br>"
            "Type:<input name='type'/><br>"
            "Options:<input name='options'/><br>"
            "Channel ID:<input name='channel_id'/><br>"
            "Closes at (ISO):<input name='closes_at'/><br>"
            "<button>Create</button></form>"
        )
        return web.Response(
            text=f"<h1>Polls</h1><ul>{rows}</ul>{form}",
            content_type="text/html",
        )

    async def poll_create(request: web.Request) -> web.Response:
        data = await request.post()
        question = data.get("question", "").strip()
        poll_type = data.get("type", "yesno").strip()
        options = [o.strip() for o in data.get("options", "").split(";") if o.strip()]
        channel_id = int(data.get("channel_id", 0))
        closes_at_str = data.get("closes_at")
        closes_at = datetime.fromisoformat(closes_at_str) if closes_at_str else None
        user_id = int(request["user"]["id"]) if request.get("user") else 0
        if not question or not channel_id:
            return web.Response(status=400, text="invalid poll")
        poll = polling.create_poll(
            db,
            question,
            poll_type,
            options,
            user_id,
            channel_id,
            closes_at,
        )
        if closes_at:
            polling.schedule_close(bot, poll.id, closes_at)
        raise web.HTTPFound("/polls")

    async def timed_messages_page(request: web.Request) -> web.Response:
        rows = db.query(models.TimedMessage).all()
        items = "".join(f"<li>{r.message_id} delete:{r.delete_at}</li>" for r in rows)
        form = (
            "<form method='post'>"
            "Channel ID:<input name='channel_id'/><br>"
            "Message:<input name='message'/><br>"
            "Seconds:<input name='seconds'/><br>"
            "<button>Send</button></form>"
        )
        return web.Response(
            text=f"<h1>Timed Messages</h1><ul>{items}</ul>{form}",
            content_type="text/html",
        )

    async def timed_messages_create(request: web.Request) -> web.Response:
        data = await request.post()
        channel_id = int(data.get("channel_id", 0))
        message = str(data.get("message", ""))
        seconds = int(data.get("seconds", 0))
        if not channel_id or not message or seconds <= 0:
            return web.Response(status=400, text="invalid timer")
        channel = bot.get_channel(channel_id) if bot else None
        if not channel or not hasattr(channel, "send"):
            return web.Response(status=404, text="channel not found")
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        sent = await channel.send(message)
        delete_at = datetime.utcnow() + timedelta(seconds=seconds)
        db.add(
            models.TimedMessage(
                message_id=sent.id, channel_id=channel_id, delete_at=delete_at
            )
        )
        db.commit()
        messages_scheduled.inc()
        raise web.HTTPFound("/timed-messages")

    async def welcome_page(request: web.Request) -> web.Response:
        rows = db.query(welcome.WelcomeConfig).all()
        items = "".join(
            f"<li>{r.guild_id} channel:{r.channel_id} role:{r.verify_role_id or ''} {r.message}</li>"
            for r in rows
        )
        form = (
            "<form method='post'>"
            "Guild ID:<input name='guild_id'/><br>"
            "Channel ID:<input name='channel_id'/><br>"
            "Message:<input name='message'/><br>"
            "Verify Role ID:<input name='verify_role'/><br>"
            "<button>Save</button></form>"
        )
        return web.Response(
            text=f"<h1>Welcome</h1><ul>{items}</ul>{form}",
            content_type="text/html",
        )

    async def welcome_set(request: web.Request) -> web.Response:
        data = await request.post()
        guild_id = int(data.get("guild_id", 0))
        channel_id = int(data.get("channel_id", 0))
        message = str(data.get("message", ""))
        verify_role = data.get("verify_role")
        verify_role_id = int(verify_role) if verify_role else None
        if not guild_id or not channel_id or not message:
            return web.Response(status=400, text="invalid config")
        welcome.set_config(db, guild_id, channel_id, message, verify_role_id)
        raise web.HTTPFound("/welcome")

    app.router.add_get("/", index)
    app.router.add_get("/subscriptions", subscriptions_page)
    app.router.add_post(r"/subscriptions/{sub_id:\d+}/delete", subscription_delete)
    app.router.add_get("/roles", roles_page)
    app.router.add_post("/roles/remove", roles_remove)
    app.router.add_get("/birthdays", birthdays_page)
    app.router.add_get("/channels", channels_page)
    app.router.add_post(r"/channels/{channel_id:\d+}/settings", channel_settings)
    app.router.add_get("/polls", polls_page)
    app.router.add_post("/polls", poll_create)
    app.router.add_get("/timed-messages", timed_messages_page)
    app.router.add_post("/timed-messages", timed_messages_create)
    app.router.add_get("/welcome", welcome_page)
    app.router.add_post("/welcome", welcome_set)
    app.router.add_get("/audit", audit_page)
    app.router.add_get("/login", login)
    app.router.add_get("/oauth/callback", oauth_callback)
    app.router.add_get("/logout", logout)
    app.router.add_get("/metrics", metrics_handler)
    app.router.add_get("/ready", ready_handler)
    moderation.register_routes(app, db)
    return app


async def run_bot() -> None:
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set")
    app = create_management_app(bot.db)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", MGMT_PORT)
    await site.start()
    if bot.bridge:
        await bot.bridge.start()
    try:
        await bot.start(TOKEN)
    finally:
        if bot.bridge:
            await bot.bridge.stop()
        await runner.cleanup()
        await adapter_client.close_session()


if __name__ == "__main__":
    main()
    asyncio.run(run_bot())
