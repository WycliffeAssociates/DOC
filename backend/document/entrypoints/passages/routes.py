import json
from fastapi import APIRouter

import celery.states
from celery.result import AsyncResult
from document.config import settings
from document.passages import document_generator
from document.passages import model

from fastapi import HTTPException, status

from fastapi.responses import JSONResponse

router = APIRouter()

logger = settings.logger(__name__)


@router.post("/passages/document_docx")
async def generate_passages_docx_document(
    passages_document_request: model.PassagesDocumentRequest,
) -> JSONResponse:
    # Top level exception handler
    try:
        task = document_generator.generate_passages_docx_document.apply_async(
            args=(
                passages_document_request.lang_code,
                passages_document_request.lang_name,
                # Serialize the list of objects to a JSON string
                json.dumps(
                    passages_document_request.passage_references,
                    default=lambda obj: obj.model_dump(),
                ),
                passages_document_request.email_address,
            )
        )
    except HTTPException as exc:
        raise exc
    except (
        Exception
    ) as exc:  # catch any exceptions we weren't expecting, handlers handle the ones we do expect.
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


@router.get("/passages/task_status/{task_id}")
async def task_status(task_id: str) -> JSONResponse:
    res: AsyncResult[dict[str, str]] = AsyncResult(task_id)
    if res.state == celery.states.SUCCESS:
        return JSONResponse({"state": celery.states.SUCCESS, "result": res.result})
    return JSONResponse(
        {
            "state": res.state,
        }
    )
