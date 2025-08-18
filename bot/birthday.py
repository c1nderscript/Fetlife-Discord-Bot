from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import Column, BigInteger, Date, String, Boolean

from .db import Base


class Birthday(Base):
    __tablename__ = "birthdays"
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    date = Column(Date, nullable=False)
    timezone = Column(String, nullable=False, default="UTC")
    private = Column(Boolean, nullable=False, default=False)
    role_id = Column(BigInteger, nullable=True)


birthday_group = app_commands.Group(name="birthday", description="Manage birthdays")


@birthday_group.command(name="set")
@app_commands.describe(
    date="Birthdate in YYYY-MM-DD",
    timezone="IANA timezone name",
    private="Hide your username in announcements",
    role="Role to assign on your birthday",
)
async def set_birthday(
    interaction: discord.Interaction,
    date: str,
    timezone: str = "UTC",
    private: bool = False,
    role: Optional[discord.Role] = None,
) -> None:
    try:
        bday = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        await interaction.response.send_message("Invalid date format.", ephemeral=True)
        return
    try:
        ZoneInfo(timezone)
    except Exception:
        await interaction.response.send_message("Invalid timezone.", ephemeral=True)
        return
    session = interaction.client.db
    entry = (
        session.query(Birthday)
        .filter_by(user_id=interaction.user.id, guild_id=interaction.guild_id)
        .first()
    )
    if entry:
        entry.date = bday
        entry.timezone = timezone
        entry.private = private
        entry.role_id = role.id if role else None
    else:
        entry = Birthday(
            user_id=interaction.user.id,
            guild_id=interaction.guild_id or 0,
            date=bday,
            timezone=timezone,
            private=private,
            role_id=role.id if role else None,
        )
        session.add(entry)
    session.commit()
    await interaction.response.send_message("Birthday saved.", ephemeral=True)


@birthday_group.command(name="list")
async def list_birthdays(interaction: discord.Interaction) -> None:
    session = interaction.client.db
    rows = session.query(Birthday).filter_by(guild_id=interaction.guild_id).all()
    if not rows:
        await interaction.response.send_message("No birthdays set.", ephemeral=True)
        return
    lines = []
    for r in rows:
        name = "Hidden" if r.private else f"<@{r.user_id}>"
        lines.append(f"{name}: {r.date.strftime('%m-%d')} ({r.timezone})")
    await interaction.response.send_message("\n".join(lines), ephemeral=True)


@birthday_group.command(name="remove")
async def remove_birthday(interaction: discord.Interaction) -> None:
    session = interaction.client.db
    session.query(Birthday).filter_by(
        user_id=interaction.user.id, guild_id=interaction.guild_id
    ).delete()
    session.commit()
    await interaction.response.send_message("Birthday removed.", ephemeral=True)


async def announce_birthdays(bot: commands.Bot) -> None:
    session = bot.db
    rows = session.query(Birthday).all()
    now_utc = datetime.utcnow()
    for row in rows:
        try:
            tz = ZoneInfo(row.timezone)
        except Exception:
            tz = ZoneInfo("UTC")
        today = now_utc.astimezone(tz).date()
        if today.month == row.date.month and today.day == row.date.day:
            from .config import get_guild_config

            cfg = get_guild_config(bot.config, row.guild_id)
            channel_id = int(cfg.get("birthday_channel", 0))
            channel = bot.get_channel(channel_id)
            if not channel:
                continue
            mention = "Someone" if row.private else f"<@{row.user_id}>"
            await channel.send(f"Happy birthday {mention}! 🎉")
            if row.role_id:
                guild = channel.guild
                member = guild.get_member(row.user_id)
                role = guild.get_role(row.role_id)
                if member and role:
                    await member.add_roles(role, reason="Birthday")


def schedule(bot: commands.Bot) -> None:
    bot.scheduler.add_job(announce_birthdays, "cron", hour=0, minute=0, args=[bot])
