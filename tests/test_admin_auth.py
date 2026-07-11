import os
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("BOT_TOKEN", "test-token")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("DATABASE_NAME", "botminton_test")
os.environ.setdefault("COMMON_GROUP_CHAT_ID", "common-chat")
os.environ.setdefault("ADMIN_USER_ID", "111")
os.environ.setdefault("JWT_SECRET", "test-secret")

from fastapi import FastAPI
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from jose import jwt

import backend.auth as auth
import backend.deps as deps
import backend.routes.users as users_route


class FakeTelegramClient:
    requests = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def post(self, url, json):
        self.requests.append({"url": url, "json": json})
        return SimpleNamespace(status_code=200)


def _user(telegram_id, username, is_admin=True, full_name=None):
    return SimpleNamespace(
        id=f"id-{telegram_id}",
        telegram_id=telegram_id,
        telegram_user_name=username,
        full_name=full_name,
        is_admin=is_admin,
    )


class AdminAuthTests(unittest.TestCase):
    def setUp(self):
        auth._otp_store.clear()
        auth._request_log.clear()
        FakeTelegramClient.requests.clear()

    def _auth_client(self):
        app = FastAPI()
        app.include_router(auth.router, prefix="/api/auth")
        return TestClient(app)

    def _users_client(self, actor_telegram_id):
        app = FastAPI()
        app.include_router(users_route.router, prefix="/api/users")
        app.dependency_overrides[users_route.require_admin] = lambda: actor_telegram_id
        return TestClient(app)

    def test_login_admins_includes_synthesized_super_admin(self):
        client = self._auth_client()

        with patch.object(
            auth,
            "list_admin_login_options",
            return_value=[
                {
                    "telegram_id": "111",
                    "telegram_user_name": None,
                    "full_name": "Super admin",
                    "is_admin": True,
                    "is_super_admin": True,
                },
                {
                    "telegram_id": "222",
                    "telegram_user_name": "clubadmin",
                    "full_name": "Club Admin",
                    "is_admin": True,
                    "is_super_admin": False,
                },
            ],
            create=True,
        ):
            response = client.get("/api/auth/admins")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "telegram_id": "111",
                    "telegram_user_name": None,
                    "full_name": "Super admin",
                    "is_admin": True,
                    "is_super_admin": True,
                },
                {
                    "telegram_id": "222",
                    "telegram_user_name": "clubadmin",
                    "full_name": "Club Admin",
                    "is_admin": True,
                    "is_super_admin": False,
                },
            ],
        )

    def test_otp_is_sent_to_selected_admin_and_token_subject_matches(self):
        client = self._auth_client()

        rng = SimpleNamespace(randint=lambda _low, _high: 123456)
        with (
            patch.object(auth, "check_admin", return_value=True, create=True),
            patch.object(auth.random, "SystemRandom", return_value=rng),
            patch.object(auth.httpx, "AsyncClient", FakeTelegramClient),
        ):
            request_response = client.post("/api/auth/request-otp", json={"telegram_id": "222"})
            verify_response = client.post(
                "/api/auth/verify-otp",
                json={"telegram_id": "222", "otp": "123456"},
            )

        self.assertEqual(request_response.status_code, 200)
        self.assertEqual(FakeTelegramClient.requests[0]["json"]["chat_id"], "222")
        self.assertEqual(verify_response.status_code, 200)
        token = verify_response.json()["access_token"]
        payload = jwt.decode(token, auth.JWT_SECRET, algorithms=[auth.ALGORITHM])
        self.assertEqual(payload["sub"], "222")

    def test_require_admin_accepts_database_admins(self):
        token = jwt.encode(
            {"sub": "222", "exp": int(time.time()) + 60},
            deps.JWT_SECRET,
            algorithm=deps.ALGORITHM,
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with patch.object(deps, "check_admin", return_value=True, create=True):
            self.assertEqual(deps.require_admin(credentials), "222")

    def test_only_super_admin_can_appoint_admins(self):
        client = self._users_client("333")

        with (
            patch.object(users_route, "check_super_admin", side_effect=lambda tid: tid == "111", create=True),
            patch.object(users_route, "update_user", return_value=_user("222", "clubadmin", True)),
        ):
            response = client.put("/api/users/222", json={"is_admin": True})

        self.assertEqual(response.status_code, 403)

    def test_super_admin_can_appoint_admins(self):
        client = self._users_client("111")

        with (
            patch.object(users_route, "check_super_admin", side_effect=lambda tid: tid == "111", create=True),
            patch.object(users_route, "update_user", return_value=_user("222", "clubadmin", True)) as update_user,
        ):
            response = client.put("/api/users/222", json={"is_admin": True})

        self.assertEqual(response.status_code, 200)
        update_user.assert_called_once_with("222", is_admin=True)
        self.assertTrue(response.json()["is_admin"])


if __name__ == "__main__":
    unittest.main()
