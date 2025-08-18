import asyncio
from aiohttp.test_utils import TestServer, TestClient

from bot import main, storage, models, polling, welcome


def test_management_ui(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "secret")
    monkeypatch.setenv("ADMIN_IDS", "1")
    app_bot = main.main(require_env=False)
    db = app_bot.db
    sub_id = storage.add_subscription(db, 123, "events", "target")
    storage.set_reaction_role(db, 10, "😀", 20, 1)
    db.add(models.AuditLog(user_id=1, action="test", target="x", details={}))
    db.commit()

    async def run():
        app = main.create_management_app(db)
        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()
        resp = await client.get("/", allow_redirects=False)
        assert resp.status == 302
        cookie = main.sign_session({"id": "1", "username": "admin"}, secret="secret")
        client.session.cookie_jar.update_cookies({"session": cookie})
        resp = await client.get("/subscriptions")
        text = await resp.text()
        assert "events" in text
        await client.post(f"/subscriptions/{sub_id}/delete")
        assert storage.list_subscriptions(db, 123) == []
        await client.post("/channels/123/settings", data={"settings": '{"x":1}'})
        channel = db.get(models.Channel, 123)
        assert channel.settings_json == {"x": 1}
        await client.post("/roles/remove", data={"message_id": "10", "emoji": "😀"})
        assert storage.get_reaction_role(db, 10, "😀") is None
        resp = await client.get("/audit")
        text = await resp.text()
        assert "test" in text

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
            "/timed-messages",
            data={"channel_id": "1", "message": "hi", "seconds": "5"},
        )
        tm = db.query(models.TimedMessage).first()
        assert tm and tm.channel_id == 1

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
        await client.close()
        await server.close()

    asyncio.run(run())
