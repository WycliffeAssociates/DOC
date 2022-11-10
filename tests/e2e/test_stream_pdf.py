import logging
import os

import requests
import time
import yaml
from document.config import settings
from document.entrypoints.app import app
from fastapi.testclient import TestClient

from document.domain import model

logger = settings.logger(__name__)


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
        logger.debug("response.content: {}".format(response.json()))
        task_id = response.json()["task_id"]
        assert task_id

    while True:
        with TestClient(app=app, base_url=settings.api_test_url()) as client:
            response2: requests.Response = client.get(
                "/api/{}/status".format(task_id),
            )
            logger.debug("response: {}".format(response2))
            logger.debug("status: {}".format(response2.json()["state"]))
            if response2.json()["state"] == "SUCCESS":
                finished_document_request_key = response2.json()["result"]
                finished_document_path = os.path.join(
                    settings.document_serve_dir(),
                    "{}.pdf".format(finished_document_request_key),
                )
                logger.debug(
                    "finished_document_path: {}".format(finished_document_path)
                )
                assert os.path.exists(finished_document_path)
                assert response2.ok
                break
            time.sleep(4)
