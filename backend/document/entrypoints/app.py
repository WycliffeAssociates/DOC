"""This module provides the FastAPI API definition."""

import os
import shutil

from document.config import settings
from document.domain import exceptions
from document.entrypoints.routes import router as doc_router
from document.entrypoints.stet.routes import router as stet_router
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

ASSETS_DOWNLOAD_DIR = "/app/assets_download"
BACKUP_DIR = "/app/"
EN_RG_DIR = os.path.join(ASSETS_DOWNLOAD_DIR, "en_rg")
DOCX_FILE_SRC = os.path.join(BACKUP_DIR, "en_rg_nt_survey.docx")
DOCX_FILE_DEST = os.path.join(EN_RG_DIR, "en_rg_nt_survey.docx")

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


# Until reviewer's guides can be accessed via data API, create their
# directory and copy them into place
@app.on_event("startup")
async def initialize_assets() -> None:
    """
    Ensures the en_rg directory and the .docx file exist in the assets_download volume.
    """
    try:
        # Create the en_rg directory if it doesn't exist
        os.makedirs(EN_RG_DIR, exist_ok=True)
        # Copy the .docx file if it doesn't already exist
        if not os.path.exists(DOCX_FILE_DEST):
            shutil.copy(DOCX_FILE_SRC, DOCX_FILE_DEST)
        print("Assets initialized successfully.")
    except Exception as e:
        print(f"Error initializing assets: {e}")


app.include_router(doc_router)
app.include_router(stet_router)
