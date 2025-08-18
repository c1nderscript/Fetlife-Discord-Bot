import asyncio

from aiohttp.test_utils import TestServer, TestClient

from bot import main, moderation, models


def test_moderation_forms(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "secret")
    monkeypatch.setenv("ADMIN_IDS", "1")
    app_bot = main.main(require_env=False)
    db = app_bot.db

    class DummyMember:
        id = 2
        mention = "@user"

        async def timeout(self, *args, **kwargs):
            pass

    class DummyGuild:
        id = 1

        def get_member(self, uid):
            return DummyMember() if uid == 2 else None

        async def kick(self, member, reason=None):
            pass

        async def ban(self, member, reason=None):
            pass

    class DummyChannel:
        id = 10

        async def purge(self, limit, check):
            return []

    monkeypatch.setattr(app_bot, "get_guild", lambda _gid: DummyGuild())
    monkeypatch.setattr(app_bot, "get_channel", lambda _cid: DummyChannel())

    async def run():
        app = main.create_management_app(db)
        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()
        cookie = main.sign_session({"id": "1", "username": "admin"}, secret="secret")
        client.session.cookie_jar.update_cookies({"session": cookie})
        await client.post(
            "/moderation/warn",
            data={"guild_id": "1", "user_id": "2", "reason": "be nice"},
        )
        infra = db.query(moderation.Infraction).filter_by(user_id=2).one()
        assert infra.type == moderation.InfractionType.WARN.value
        log = db.query(models.AuditLog).filter_by(action="warn").one()
        assert log.target == "2"
        await client.post(
            "/moderation/purge",
            data={"channel_id": "10", "limit": "1"},
        )
        log2 = db.query(models.AuditLog).filter_by(action="purge").one()
        assert log2.target == "10"
        await client.close()
        await server.close()

    asyncio.run(run())


def test_moderation_requires_login(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "secret")
    monkeypatch.setenv("ADMIN_IDS", "1")
    app_bot = main.main(require_env=False)
    db = app_bot.db

    async def run():
        app = main.create_management_app(db)
        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()
        resp = await client.get("/moderation", allow_redirects=False)
        assert resp.status == 302
        await client.close()
        await server.close()

    asyncio.run(run())
