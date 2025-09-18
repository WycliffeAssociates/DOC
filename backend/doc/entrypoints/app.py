"""This module provides the FastAPI API definition."""

import shutil
from os import makedirs
from os.path import join, exists

from doc.config import settings
from doc.domain import exceptions
from doc.entrypoints.routes import router as doc_router
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from passages.entrypoints.routes import router as passages_router
from stet.entrypoints.routes import router as stet_router


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


DOCKER_BASE_DIR = "/app"


SURVEY_FILES = {
    "nt": "en_rg_nt_survey.docx",
    "ot_rg1": "en_ot_survey_rg1_gen_deu.docx",
    "ot_rg2": "en_ot_survey_rg2_jos_est.docx",
    "ot_rg3": "en_ot_survey_rg3_job_sng.docx",
    "ot_rg4": "en_ot_survey_rg4_isa_mal.docx",
}


def build_paths(base_dir: str, en_rg_dir: str) -> dict[str, tuple[str, str]]:
    """
    Build src/dest pairs for each survey file.
    Returns a dict where key is 'nt', 'ot_rg1', etc.
    Each value is (src, dest).
    """
    return {
        key: (
            join(base_dir, filename),
            join(en_rg_dir, filename),
        )
        for key, filename in SURVEY_FILES.items()
    }


DOCKER_PATHS = build_paths(DOCKER_BASE_DIR, join(DOCKER_BASE_DIR, settings.EN_RG_DIR))
LOCAL_PATHS = build_paths("", settings.EN_RG_DIR)  # src is just filename in local case


def initialize_assets(
    docker_base_dir: str = DOCKER_BASE_DIR,
    docker_paths: dict[str, tuple[str, str]] = DOCKER_PATHS,
    survey_files: dict[str, str] = SURVEY_FILES,
    resource_assets_dir: str = settings.RESOURCE_ASSETS_DIR,
    local_paths: dict[str, tuple[str, str]] = LOCAL_PATHS,
) -> None:
    """
    Ensures the en_rg directory and the .docx file exist in the assets_download volume.
    """
    try:
        if exists(docker_base_dir):  # inside Docker
            makedirs(docker_paths["nt"][1].rsplit("/", 1)[0], exist_ok=True)
            for key, (src, dest) in docker_paths.items():
                if not exists(dest):
                    shutil.copy(src, dest)
                    if not exists(dest):
                        raise AssertionError(
                            f"{survey_files[key]} not copied into place!"
                        )
        elif exists(resource_assets_dir):  # outside Docker
            makedirs(local_paths["nt"][1].rsplit("/", 1)[0], exist_ok=True)
            for src, dest in local_paths.values():
                if not exists(dest):
                    shutil.copy(src, dest)
                    if not exists(dest):
                        raise AssertionError(
                            f"{survey_files[key]} not copied into place!"
                        )
        logger.info("Assets initialized successfully.")
    except Exception as e:
        logger.info(f"Error initializing assets: {e}")




# Until reviewer's guides can be accessed via data API, create their
# directory and copy them into place
@app.on_event("startup")
async def startup() -> None:
    initialize_assets()


app.include_router(doc_router)
app.include_router(stet_router)
app.include_router(passages_router)
