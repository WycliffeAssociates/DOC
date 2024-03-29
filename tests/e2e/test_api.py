"""This module provides tests for the application's FastAPI API."""

import os
import pathlib

import bs4
import pytest
import requests
from document.config import settings
from document.domain import model, resource_lookup
from document.entrypoints.app import app
from fastapi.testclient import TestClient

from tests.shared.utils import (
    check_finished_document_with_verses_success,
    check_finished_document_without_verses_success,
    check_result,
)

logger = settings.logger(__name__)

##########################################################################
## Specific targeted tests (wrt language, resource type, resource code) ##
##########################################################################


@pytest.mark.docx
def test_en_ulb_wa_col_en_tn_wa_col_language_book_order_with_no_email_1c_docx() -> None:
    """
    Produce chapter interleaved document for English scripture and
    translation notes for the book of Colossians.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents_docx",
            json={
                # "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": True,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_result(response, suffix="docx")


@pytest.mark.skip
def test_en_ulb_wa_col_en_tn_wa_col_language_book_order_with_no_email_1c_c() -> None:
    """
    Produce chapter interleaved document for English scripture and
    translation notes for the book of Colossians.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                # "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_language_book_order_1c() -> None:
    """
    Produce chapter level interleaved document for English scripture,
    translation notes, and translation questions for the book of Col.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_language_book_order_1c_c() -> None:
    """
    Produce chapter level interleaved document for English scripture,
    translation notes, and translation questions for the book of Col.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_tn_wa_jud_language_book_order_1c() -> None:
    """
    Produce chapter level interleaved document for English scripture and
    translation notes for the book of Jude.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "jud",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "jud",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_tn_wa_jud_language_book_order_1c_c() -> None:
    """
    Produce chapter level interleaved document for English scripture and
    translation notes for the book of Jude.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "jud",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "jud",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_ar_ulb_jud_language_book_order_1c() -> None:
    """
    Produce chapter level interleaved document for language, ar, Arabic
    scripture. There are no other resources than USFM available at
    this time.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "ar",
                        "resource_type": "ulb",
                        "book_code": "jud",
                    },
                ],
            },
        )
        with pytest.raises(Exception):
            check_finished_document_with_verses_success(response, suffix="pdf")


def test_ar_ulb_jud_language_book_order_1c_c() -> None:
    """
    Produce chapter level interleaved document for language, ar, Arabic
    scripture. There are no other resources than USFM available at
    this time.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "ar",
                        "resource_type": "ulb",
                        "book_code": "jud",
                    },
                ],
            },
        )
        with pytest.raises(Exception):
            check_finished_document_with_verses_success(response, suffix="pdf")


def test_pt_br_ulb_tn_language_book_order_1c() -> None:
    """
    Produce chapter level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_pt_br_ulb_tn_language_book_order_1c_c() -> None:
    """
    Produce chapter level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "gen",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "gen",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_pt_br_ulb_tn_en_ulb_wa_tn_wa_luk_language_book_order_1c() -> None:
    """
    Produce chapter level interleaved document for Brazilian Portuguese
    and English scripture and translation notes for the book of Luke.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "luk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_pt_br_ulb_tn_en_ulb_wa_tn_wa_luk_language_book_order_1c_c() -> None:
    """
    Produce chapter level interleaved document for Brazilian Portuguese
    and English scripture and translation notes for the book of Luke.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "luk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_pt_br_ulb_tn_luk_en_ulb_wa_tn_wa_luk_sw_ulb_tn_col_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_pt_br_ulb_tn_luk_en_ulb_wa_tn_wa_luk_sw_ulb_tn_col_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "assembly_layout_kind": None,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tn_wa_col_en_tw_wa_col_sw_ulb_col_sw_tn_col_sw_tw_col_sw_ulb_tit_sw_tn_tit_sw_tw_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tn_wa_col_en_tw_wa_col_sw_ulb_col_sw_tn_col_sw_tw_col_sw_ulb_tit_sw_tn_tit_sw_tw_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "assembly_layout_kind": None,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tn-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tn",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tw_wa_col_sw_ulb_col_sw_tw_col_sw_ulb_tit_sw_tw_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tw_wa_col_sw_ulb_col_sw_tw_col_sw_ulb_tit_sw_tw_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "assembly_layout_kind": None,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tq_col_sw_tw_col_sw_ulb_tit_sw_tq_tit_sw_tw_tit_language_book_order_1c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tq_col_sw_tw_col_sw_ulb_tit_sw_tq_tit_sw_tw_tit_language_book_order_1c_c() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "assembly_layout_kind": None,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tq_col_sw_tw_col_zh_cuv_tit_sw_tq_tit_sw_tw_tit_language_book_order_1c() -> None:
    """
    This test demonstrates the quirk of combining resources for
    the same books but from different languages.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_en_ulb_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tq_col_sw_tw_col_zh_cuv_tit_sw_tq_tit_sw_tw_tit_language_book_order_1c_c() -> None:
    """
    This test demonstrates the quirk of combining resources for
    the same books but from different languages.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": None,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "en",
                        "resource_type": "ulb-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tq-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "en",
                        "resource_type": "tw-wa",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "ulb",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "col",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tq",
                        "book_code": "tit",
                    },
                    {
                        "lang_code": "sw",
                        "resource_type": "tw",
                        "book_code": "tit",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


###################################################################
# Tests that originally were randomly chosen and failed
# using our random combinatoric tests.
###################################################################


def test_zh_ulb_doesnt_exist_jol_zh_tn_jol_language_book_order_1c() -> None:
    """
    This shows that resource request for resource type ULB fails for
    lang_code zh because such a resource type does not exist for zh.
    Instead, cuv should have been requested. The other resources are
    found and thus a PDF document is still created, but it lacks the
    scripture verses.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "ulb",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "book_code": "jol",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response, suffix="pdf")


def test_zh_ulb_doesnt_exist_jol_zh_tn_jol_language_book_order_1c_c() -> None:
    """
    This shows that resource request for resource type ULB fails for
    lang_code zh because such a resource type does not exist for zh.
    Instead, cuv should have been requested. The other resources are
    found and thus a PDF document is still created, but it lacks the
    scripture verses.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "assembly_layout_kind": None,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "ulb",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "book_code": "jol",
                    },
                ],
            },
        )
        check_finished_document_without_verses_success(response, suffix="pdf")


def test_zh_cuv_jol_zh_tn_jol_language_book_order_1c() -> None:
    """
    This test succeeds by correcting the mistake of the document request
    in the test above it, i.e., ulb -> cuv.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "book_code": "jol",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_zh_cuv_jol_zh_tn_jol_language_book_order_1c_c() -> None:
    """
    This test succeeds by correcting the mistake of the document request
    in the test above it, i.e., ulb -> cuv.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "assembly_layout_kind": None,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "book_code": "jol",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_zh_cuv_jol_zh_tn_jol_zh_tq_jol_zh_tw_jol_language_book_order_1c() -> None:
    """
    This test succeeds by correcting the mistake of the document request
    in the test above it, i.e., ulb -> cuv.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tq",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tw",
                        "book_code": "jol",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


@pytest.mark.docx
def test_zh_cuv_jol_zh_tn_jol_zh_tq_jol_zh_tw_jol_language_book_order_1c_docx() -> None:
    """
    This test succeeds by correcting the mistake of the document request
    in the test above it, i.e., ulb -> cuv.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents_docx",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "chunk_size": model.ChunkSizeEnum.CHAPTER,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": True,
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tq",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tw",
                        "book_code": "jol",
                    },
                ],
            },
        )
        check_result(response, suffix="docx")


def test_zh_cuv_jol_zh_tn_jol_zh_tq_jol_zh_tw_jol_language_book_order_1c_c() -> None:
    """
    This test succeeds by correcting the mistake of the document request
    in the test above it, i.e., ulb -> cuv.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": None,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "zh",
                        "resource_type": "cuv",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tn",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tq",
                        "book_code": "jol",
                    },
                    {
                        "lang_code": "zh",
                        "resource_type": "tw",
                        "book_code": "jol",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_pt_br_ulb_luk_pt_br_tn_luk_language_book_order_1c() -> None:
    """
    Produce chapter level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "luk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


def test_pt_br_ulb_luk_pt_br_tn_luk_language_book_order_1c_c() -> None:
    """
    Produce chapter level interleaved document for Brazilian Portuguese scripture and
    translation notes for the book of Genesis.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                # "assembly_layout_kind": model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
                "assembly_layout_kind": None,
                "layout_for_print": True,
                "generate_pdf": True,
                "generate_epub": False,
                "generate_docx": False,
                "resource_requests": [
                    {
                        "lang_code": "pt-br",
                        "resource_type": "ulb",
                        "book_code": "luk",
                    },
                    {
                        "lang_code": "pt-br",
                        "resource_type": "tn",
                        "book_code": "luk",
                    },
                ],
            },
        )
        check_finished_document_with_verses_success(response, suffix="pdf")


# [('fa',
#   [('tn', 'Translation Notes (tn)'),
#    ('ulb', 'Henry Martyn Open Source Bible (1876) (ulb)')]),
#  ('id',
#   [('tn', 'Translation Notes (tn)'),
#    ('tq', 'Translation Questions (tq)'),
#    ('tw', 'Translation Words (tw)')]),
#  ('pmy',
#   [('tn', 'Translation Notes (tn)'),
#    ('tq', 'Translation Questions (tq)'),
#    ('tw', 'Translation Words (tw)')])]
@pytest.mark.docx
def test_fa_ulb_tn_lbo_1c_chapter() -> None:
    """
    Check if translations.json resources available for fa yield
    successful document generation.
    """
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/documents_docx",
            json={
                "email_address": settings.TO_EMAIL_ADDRESS,
                "assembly_strategy_kind": model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
                "assembly_layout_kind": None,
                "layout_for_print": False,
                "generate_pdf": False,
                "generate_epub": False,
                "generate_docx": True,
                "resource_requests": [
                    {
                        "lang_code": "fa",
                        "resource_type": "ulb",
                        "book_code": "eph",
                    },
                    {
                        "lang_code": "fa",
                        "resource_type": "tn",
                        "book_code": "eph",
                    },
                ],
            },
        )
        check_result(response, suffix="docx")
