import asyncio
from aiohttp.test_utils import TestServer, TestClient

from bot import main, storage, models


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
        await client.close()
        await server.close()

    asyncio.run(run())
