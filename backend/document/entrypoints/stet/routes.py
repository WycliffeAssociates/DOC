from os import scandir
from typing import Sequence
from fastapi import APIRouter

import celery.states
from celery.result import AsyncResult
from document.config import settings
from document.domain import document_generator, exceptions, resource_lookup
from document.stet import model

from fastapi import FastAPI, HTTPException, Request, status

from fastapi.responses import JSONResponse

router = APIRouter()

logger = settings.logger(__name__)


@router.get("/stet/source_languages")
async def source_lang_codes_and_names(
    stet_dir: str = settings.STET_DIR,
) -> Sequence[tuple[str, str, bool]]:
    """
    Return list of all available language code, name tuples for which Translation Services has provided a source document.
    """
    # Scan what source docs are available and make sure to filter
    # source language candidates to only those languages.
    ietf_codes = [
        entry.name.split("stet_")[-1].removesuffix(".docx")
        for entry in scandir(stet_dir)
        if entry.is_file()
        and entry.name.startswith("stet_")
        and entry.name.endswith(".docx")
    ]
    logger.debug("ietf_codes: %s", ietf_codes)
    languages = [
        lang_code_and_name
        for lang_code_and_name in resource_lookup.lang_codes_and_names()
        if lang_code_and_name[0] in ietf_codes
    ]
    logger.debug("languages: %s", languages)
    return languages


@router.get("/stet/target_languages/{lang0_code}")
async def target_lang_codes_and_names(
    lang0_code: str,
) -> Sequence[tuple[str, str, bool]]:
    """
    Return list of all available language code, name tuples excluding
    the source language chosen: lang0_code.
    """
    logger.debug("source language: %s", lang0_code)
    languages = [
        lang_code_and_name
        for lang_code_and_name in resource_lookup.lang_codes_and_names()
        if lang_code_and_name[0] != lang0_code
    ]
    logger.debug("target languages: %s", languages)
    return languages


@router.post("/stet/documents_stet_docx")
async def generate_stet_docx_document(
    stet_document_request: model.StetDocumentRequest,
) -> JSONResponse:
    # Top level exception handler
    try:
        task = document_generator.generate_stet_docx_document.apply_async(
            args=(
                stet_document_request.lang0_code,
                stet_document_request.lang1_code,
                stet_document_request.email_address,
            )
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:  # catch any exceptions we weren't expecting, handlers handle the ones we do expect.
        logger.exception(
            "There was an error while attempting to fulfill the document "
            "request. Likely reason is the following exception:"
        )
        # Handle exceptions that aren't handled otherwise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
    else:
        logger.debug("task_id: %s", task.id)
        return JSONResponse({"task_id": task.id})


@router.get("/stet/task_status/{task_id}")
async def task_status(task_id: str) -> JSONResponse:
    res: AsyncResult[dict[str, str]] = AsyncResult(task_id)
    if res.state == celery.states.SUCCESS:
        return JSONResponse({"state": celery.states.SUCCESS, "result": res.result})
    return JSONResponse(
        {
            "state": res.state,
        }
    )
