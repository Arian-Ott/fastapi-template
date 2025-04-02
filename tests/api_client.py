import pytest
from abc import ABC, abstractmethod
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Optional
from uuid import uuid4
from api.core.security import create_access_token
from api.services.user import UserBuilder


class AbstractAuthenticatedEndpointTest(ABC):
    """
    Abstract base for endpoint testing with automatic JWT auth.
    Automatically creates a test user and injects headers.
    """

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, client: TestClient, db: Session):
        self.client = client
        self.db = db
        self._access_token = None
        self._test_user_email = f"test_{uuid4().hex[:6]}@example.com"
        self._test_user_username = f"user_{uuid4().hex[:6]}"
        self._test_user_id = str(uuid4())
        self._create_test_user()

    @property
    @abstractmethod
    def endpoint(self) -> str:
        pass

    def _create_test_user(self):
        user = UserBuilder(self.db)
        user._id = self._test_user_id
        user.set_username(self._test_user_username)
        user.set_password("testpassword123")
        user.set_email(self._test_user_email)
        user.commit()

    def generate_token(self) -> str:
        return create_access_token(data={"sub": self._test_user_email})

    def _auth_headers(self) -> dict:
        if not self._access_token:
            self._access_token = self.generate_token()
        return {"Authorization": f"Bearer {self._access_token}"}

    # ----------------------------
    # 🔁 HTTP Utility Methods
    # ----------------------------
    def auth_get(self, path: str, query: dict = None):
        return self.client.get(
            f"{self.endpoint}{path}",
            params=query or {},
            headers=self._auth_headers()
        )

    def auth_post(self, path: str, data: dict = None):
        return self.client.post(
            f"{self.endpoint}{path}",
            json=data or {},
            headers=self._auth_headers()
        )

    def auth_put(self, path: str, data: dict = None):
        return self.client.put(
            f"{self.endpoint}{path}",
            json=data or {},
            headers=self._auth_headers()
        )

    def auth_patch(self, path: str, data: dict = None):
        return self.client.patch(
            f"{self.endpoint}{path}",
            json=data or {},
            headers=self._auth_headers()
        )

    def auth_delete(self, path: str, data: dict = None):
        return self.client.delete(
            f"{self.endpoint}{path}",
            json=data or {},
            headers=self._auth_headers()
        )