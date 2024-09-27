import pytest
from fastapi.testclient import TestClient
from tests.shared.utils import check_result
from document.entrypoints.app import app
from document.config import settings


@pytest.mark.stet
@pytest.mark.docx
def test_en_es_419_stet_docx() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/stet/documents_stet_docx",
            json={
                "lang0_code": "en",
                "lang1_code": "es-419",
                "email_address": settings.TO_EMAIL_ADDRESS,
            },
        )
        check_result(response, suffix="docx")


@pytest.mark.stet
@pytest.mark.docx
def test_en_abu_stet_docx() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/stet/documents_stet_docx",
            json={
                "lang0_code": "en",
                "lang1_code": "abu",
                "email_address": settings.TO_EMAIL_ADDRESS,
            },
        )
        check_result(response, suffix="docx")
