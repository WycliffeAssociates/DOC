"""
Tests for assembly strategy lang-then-book for reviewer's guide
"""

from doc.config import settings
from doc.domain import model
from doc.entrypoints.app import app
from fastapi.testclient import TestClient

from tests.shared.utils import (
    check_finished_document_with_verses_success,
    check_finished_document_without_verses_success,
)

logger = settings.logger(__name__)


def test_en_rg_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.INTERLEAVE_BY_BOOK,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": True,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "rg",
                        "book_code": "gal",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response)


def test_en_ulb_gal_en_rg_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.INTERLEAVE_BY_BOOK,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": True,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "rg",
                        "book_code": "gal",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_gal_en_tn_gal_en_rg_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.INTERLEAVE_BY_BOOK,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": True,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "rg",
                        "book_code": "gal",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_gal_en_tn_gal_en_rg_en_tw_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.INTERLEAVE_BY_BOOK,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": True,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "rg",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw",
                        "book_code": "gal",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_gal_en_tn_gal_en_rg_en_bc_en_tw_language_book_order_1c() -> (
    None
):
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.INTERLEAVE_BY_BOOK,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": True,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "rg",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "bc",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw",
                        "book_code": "gal",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_gal_en_tn_gal_en_tq_gal_en_rg_en_bc_en_tw_language_book_order_1c() -> (
    None
):
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.INTERLEAVE_BY_BOOK,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": True,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "rg",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "bc",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw",
                        "book_code": "gal",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)


def test_en_ulb_gal_es_419_ulb_gal_en_tn_gal_es_419_tq_gal_en_tq_gal_en_rg_en_bc_es_419_bc_en_tw_es_419_tw_language_book_order_1c() -> (
    None
):
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.INTERLEAVE_BY_BOOK,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": True,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "ulb",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tn",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "es-419",
                        "resource_type": "tq",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "rg",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "bc",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "es-418",
                        "resource_type": "bc",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw",
                        "book_code": "gal",
                    },
                    {
                        "lang_code": "es-418",
                        "resource_type": "tw",
                        "book_code": "gal",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response)
