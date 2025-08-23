import asyncio
from aiohttp.test_utils import TestServer, TestClient

from bot import main, storage, models, polling, welcome, birthday, moderation
from bot.circuit_breaker import CircuitBreaker


def test_management_ui(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "secret")
    monkeypatch.setenv("ADMIN_IDS", "1")
    app_bot = main.main(require_env=False)
    db = app_bot.db
    sub_id = storage.add_subscription(db, 123, "events", "target")
    storage.set_reaction_role(db, 10, "😀", 20, 1)
    db.add(models.AuditLog(user_id=1, action="test", target="x", details={}))
    db.commit()

    first_bday = db.query(birthday.Birthday).first()

    calls: dict[str, tuple] = {}

    async def fake_warn(bot, db, guild_id, moderator_id, user_id, reason):
        calls["warn"] = (guild_id, moderator_id, user_id, reason)
        return "ok"

    async def fake_mute(bot, db, guild_id, moderator_id, user_id, minutes, reason):
        calls["mute"] = (guild_id, moderator_id, user_id, minutes, reason)
        return "ok"

    monkeypatch.setattr(moderation, "warn", fake_warn)
    monkeypatch.setattr(moderation, "mute", fake_mute)

    breaker = CircuitBreaker(1, 1)

    async def run():
        app = main.create_management_app(db, breaker)
        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()
        resp = await client.get("/", allow_redirects=False)
        assert resp.status == 302
        cookie = main.sign_session({"id": "1", "username": "admin"}, secret="secret")
        client.session.cookie_jar.update_cookies({"session": cookie})
        resp = await client.get("/subscriptions")
        text = await resp.text()
        assert "<h1>Subscriptions" in text and "events" in text and "<form" in text
        resp = await client.get("/roles")
        text = await resp.text()
        assert "<h1>Roles" in text and "😀" in text
        resp = await client.get("/birthdays")
        text = await resp.text()
        assert "<h1>Birthdays" in text
        if first_bday:
            assert first_bday.date.isoformat() in text
        resp = await client.get("/moderation")
        text = await resp.text()
        assert "<h1>Moderation" in text
        await client.post(
            "/moderation/warn", data={"guild_id": "1", "user_id": "2", "reason": "r"}
        )
        await client.post(
            "/moderation/mute",
            data={"guild_id": "1", "user_id": "2", "minutes": "5", "reason": "r"},
        )
        assert "warn" in calls and "mute" in calls
        await client.post(f"/subscriptions/{sub_id}/delete")
        assert all(s[0] != sub_id for s in storage.list_subscriptions(db, 123))
        await client.post("/channels/123/settings", data={"settings": '{"x":1}'})
        channel = db.get(models.Channel, 123)
        assert channel.settings_json == {"x": 1}
        await client.post("/roles/remove", data={"message_id": "10", "emoji": "😀"})
        assert storage.get_reaction_role(db, 10, "😀") is None
        resp = await client.get("/audit")
        text = await resp.text()
        assert "<h1>Audit Log" in text and "test" in text

        await client.post(
            "/polls",
            data={
                "question": "Best?",
                "type": "multiple",
                "options": "chips;cookies",
                "channel_id": "1",
                "duration": "1",
            },
        )
        polls = polling.list_polls(db, active_only=False)
        poll = next(p for p in polls if p.question == "Best?")
        polling.record_vote(db, poll.id, 1, 0)
        resp = await client.get(f"/polls/{poll.id}")
        text = await resp.text()
        assert "chips" in text and "1" in text
        await client.post(f"/polls/{poll.id}/close")
        db.refresh(poll)
        assert poll.closed

        class DummyMsg:
            id = 55
            channel = type("Chan", (), {"id": 1})()

        class DummyChannel:
            id = 1

            async def send(self, msg):
                return DummyMsg()

        monkeypatch.setattr(main.bot, "get_channel", lambda _cid: DummyChannel())
        await client.post(
            "/timers",
            data={"channel_id": "1", "message": "hi", "seconds": "5"},
        )
        tm = db.query(models.TimedMessage).first()
        assert tm and tm.channel_id == 1

        await client.post(
            "/autodelete",
            data={"channel_id": "1", "seconds": "30"},
        )
        settings = storage.get_channel_settings(db, 1)
        assert settings.get("autodelete") == 30

        await client.post(
            "/welcome",
            data={
                "guild_id": "1",
                "channel_id": "1",
                "message": "hello",
                "verify_role": "2",
            },
        )
        cfg = welcome.get_config(db, 1)
        assert cfg and cfg.message == "hello"
        resp = await client.post("/welcome/preview", data={"message": "hi {user}"})
        text = await resp.text()
        assert "<h1>Preview" in text and "hi @User" in text
        await client.close()
        await server.close()

    asyncio.run(run())
