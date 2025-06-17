"""This module provides the FastAPI API definition."""

from os import makedirs
from os.path import join, exists
import shutil

from doc.config import settings
from doc.domain import exceptions
from doc.entrypoints.routes import router as doc_router
from stet.entrypoints.routes import router as stet_router
from passages.entrypoints.routes import router as passages_router
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Docker container paths
DOCKER_BASE_DIR = "/app"
DOCKER_EN_RG_DIR = join(DOCKER_BASE_DIR, settings.EN_RG_DIR)
DOCKER_DOCX_FILE_SRC = join(DOCKER_BASE_DIR, "en_rg_nt_survey.docx")
DOCKER_DOCX_FILE_DEST = join(DOCKER_EN_RG_DIR, "en_rg_nt_survey.docx")
# Local filesystem paths
LOCAL_ASSETS_DOWNLOAD_DIR = settings.RESOURCE_ASSETS_DIR
LOCAL_EN_RG_DIR = settings.EN_RG_DIR
LOCAL_DOCX_FILE_SRC = "en_rg_nt_survey.docx"
LOCAL_DOCX_FILE_DEST = join(LOCAL_EN_RG_DIR, "en_rg_nt_survey.docx")

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
        if exists(DOCKER_BASE_DIR):  # Executing inside Docker container
            makedirs(DOCKER_EN_RG_DIR, exist_ok=True)
            if not exists(DOCKER_DOCX_FILE_DEST):
                shutil.copy(DOCKER_DOCX_FILE_SRC, DOCKER_DOCX_FILE_DEST)
        elif exists(LOCAL_ASSETS_DOWNLOAD_DIR):  # Executing outside Docker container
            makedirs(LOCAL_EN_RG_DIR, exist_ok=True)
            if not exists(LOCAL_DOCX_FILE_DEST):
                shutil.copy(LOCAL_DOCX_FILE_SRC, LOCAL_DOCX_FILE_DEST)
        print("Assets initialized successfully.")
    except Exception as e:
        print(f"Error initializing assets: {e}")


app.include_router(doc_router)
app.include_router(stet_router)
app.include_router(passages_router)
