"""This module provides the FastAPI API definition."""


from typing import Sequence

import celery.states
from celery.result import AsyncResult
from document.config import settings
from document.domain import document_generator, exceptions, model, resource_lookup
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()


logger = settings.logger(__name__)

# CORS configuration to allow frontend to talk to backend
origins = settings.BACKEND_CORS_ORIGINS

logger.debug("CORS origins: %s", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(exceptions.InvalidDocumentRequestException)
def invalid_document_request_exception_handler(
    request: Request, exc: exceptions.InvalidDocumentRequestException
) -> JSONResponse:
    logger.error(f"{request}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": f"{exc.message}",
        },
    )


@app.exception_handler(exceptions.ResourceAssetFileNotFoundError)
def resource_asset_file_not_found_exception_handler(
    request: Request, exc: exceptions.ResourceAssetFileNotFoundError
) -> JSONResponse:
    logger.error(f"{request}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": f"{exc.message}",
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.post("/documents")
async def generate_document(document_request: model.DocumentRequest) -> JSONResponse:
    """
    Get the document request and hand it off to the document_generator
    module for processing.
    """
    # Top level exception handler
    try:
        task = document_generator.generate_document.apply_async(
            args=(document_request.json(),)
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


@app.post("/documents_docx")
async def generate_docx_document(
    document_request: model.DocumentRequest,
) -> JSONResponse:
    """
    Get the document request and hand it off to the document_generator
    module for processing.
    """
    # Top level exception handler
    try:
        task = document_generator.generate_docx_document.apply_async(
            args=(document_request.json(),)
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


@app.get("/task_status/{task_id}")
async def task_status(task_id: str) -> JSONResponse:
    res: AsyncResult[dict[str, str]] = AsyncResult(task_id)
    if res.state == celery.states.SUCCESS:
        return JSONResponse({"state": celery.states.SUCCESS, "result": res.result})
    return JSONResponse(
        {
            "state": res.state,
        }
    )


@app.get("/language_codes_and_names")
async def lang_codes_and_names() -> Sequence[tuple[str, str, bool]]:
    """
    Return list of all available language code, name tuples.
    """
    return resource_lookup.lang_codes_and_names()  # When using data API


@app.get("/shared_book_codes/{lang0_code}/{lang1_code}")
async def shared_book_codes(lang0_code: str, lang1_code: str) -> Sequence[Any]:
    """
    Return list of available resource codes common to both lang0_code and lang1_code.
    """
    return resource_lookup.shared_book_codes(lang0_code, lang1_code)


@app.get("/resource_types/{lang_code}/{book_codes}")
async def resource_types(
    lang_code: str,
    book_codes: str,
) -> Sequence[tuple[str, str]]:
    """
    Return the list of available resource types tuples for lang_code
    with book_codes.
    """
    return resource_lookup.resource_types(lang_code, book_codes)


@app.get("/book_codes_for_lang/{lang_code}")
async def book_codes_for_lang(lang_code: str) -> Sequence[tuple[str, str]]:
    """Return list of all available resource codes."""
    return resource_lookup.book_codes_for_lang(lang_code)


@app.get("/health/status")
async def health_status() -> tuple[dict[str, str], int]:
    """Ping-able server endpoint."""
    return {"status": "ok"}, 200
