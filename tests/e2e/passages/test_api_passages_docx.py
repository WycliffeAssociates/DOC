import json
import pytest
from fastapi.testclient import TestClient
from tests.shared.utils import check_result
from doc.entrypoints.app import app
from doc.config import settings
from passages.domain.model import PassageReferenceDto


# passage_references JSON is not correct, skipping for now as this is
# covered by frontend test anyway.
@pytest.mark.skip
@pytest.mark.passages
@pytest.mark.docx
def test_en_passages_docx() -> None:
    with TestClient(app=app, base_url=settings.api_test_url()) as client:
        response = client.post(
            "/passages/document_docx",
            json={
                "lang_code": "en",
                "passage_references": json.dumps(
                    [
                        PassageReferenceDto(
                            lang_code="en",
                            book_code="mat",
                            book_name="Matthew",
                            chapter_num=2,
                            verse_reference="1-12",
                        ).model_dump(),
                        PassageReferenceDto(
                            lang_code="en",
                            book_code="mat",
                            book_name="Matthew",
                            chapter_num=3,
                            verse_reference="13-17",
                        ).model_dump(),
                        PassageReferenceDto(
                            lang_code="en",
                            book_code="mat",
                            book_name="Matthew",
                            chapter_num=4,
                            verse_reference="1-11",
                        ).model_dump(),
                        PassageReferenceDto(
                            lang_code="en",
                            book_code="mat",
                            book_name="Matthew",
                            chapter_num=26,
                            verse_reference="3,7-10",
                        ).model_dump(),
                        PassageReferenceDto(
                            lang_code="en",
                            book_code="gen",
                            book_name="Genesis",
                            chapter_num=1,
                            verse_reference="1,3-4,12",
                        ).model_dump(),
                        PassageReferenceDto(
                            lang_code="en",
                            book_code="exo",
                            book_name="Exodus",
                            chapter_num=3,
                            verse_reference="5",
                        ).model_dump(),
                    ]
                ),
                "email_address": settings.TO_EMAIL_ADDRESS,
            },
        )
        check_result(response, suffix="docx")
