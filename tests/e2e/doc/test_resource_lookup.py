from fastapi.testclient import TestClient
import pytest
from doc.config import settings
from doc.entrypoints.app import app


def test_chapters_in_books() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.get("/chapters_in_books")
        assert response.status_code == 200
