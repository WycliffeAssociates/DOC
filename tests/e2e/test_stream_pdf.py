import logging
import os
import time
from typing import Literal

import requests
import yaml
from document.config import settings
from document.domain import model
from document.entrypoints.app import app
from fastapi.testclient import TestClient

logger = settings.logger(__name__)


def check_result(
    task_id: str,
    /,
    poll_duration: int,
    suffix: Literal["html"] | Literal["pdf"] | Literal["epub"] | Literal["docx"],
    status_url_fmt_str: str = "/api/{}/status",
    success_state: str = "SUCCESS",
) -> None:
    while True:
        with TestClient(app=app, base_url=settings.api_test_url()) as client:
            response: requests.Response = client.get(
                status_url_fmt_str.format(task_id),
            )
            logger.debug("response.json(): {}".format(response.json()))
            if response.json()["state"] == success_state:
                finished_document_request_key = response.json()["result"]
                finished_document_path = os.path.join(
                    settings.document_serve_dir(),
                    "{}.{}".format(finished_document_request_key, suffix),
                )
                logger.debug(
                    "finished_document_path: {}".format(finished_document_path)
                )
                assert os.path.exists(finished_document_path)
                assert response.ok
                break
            time.sleep(poll_duration)


def test_stream_pdf() -> None:
    """
    Produce verse level interleaved document for language, ar, Arabic
    scripture. There are no other resources than USFM available at
    this time.
    """
    # First generate the PDF
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response: requests.Response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "f10",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tn",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tq",
                        "resource_code": "col",
                    },
                    {
                        "lang_code": "fr",
                        "resource_type": "tw",
                        "resource_code": "col",
                    },
                ],
            },
        )
        logger.debug("response.json(): {}".format(response.json()))
        task_id = response.json()["task_id"]
        assert task_id

    check_result(task_id, poll_duration=4, suffix="pdf")
