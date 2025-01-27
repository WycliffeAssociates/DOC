from typing import Mapping, Sequence

from celery import current_task
from document.config import settings
from document.domain.parsing import (
    lookup_verse_text,
    split_chapter_into_verses,
    usfm_book_content,
)
from document.domain.resource_lookup import (
    RESOURCE_TYPE_CODES_AND_NAMES,
    prepare_resource_filepath,
    provision_asset_files,
    resource_lookup_dto,
    resource_types,
)
from document.passages.docx_utils import add_footer, add_header
from document.passages.model import PassageDto, PassageReferenceDto
from document.passages.parser import get_verse_text
from docx import Document  # type: ignore
from htmldocx import HtmlToDocx  # type: ignore

logger = settings.logger(__name__)


def generate_docx_document(
    lang_code: str,
    passage_reference_dtos: list[PassageReferenceDto],
    document_request_key_: str,
    docx_filepath_: str,
    working_dir: str = settings.WORKING_DIR,
    output_dir: str = settings.DOCUMENT_OUTPUT_DIR,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    resource_type_codes_and_names: Mapping[str, str] = RESOURCE_TYPE_CODES_AND_NAMES,
) -> str:
    """
    Generate the scriptural terms evaluation document.

    >>> from document.passages import generate_docx_document
    >>> generate_docx_document("en", list[PassageReferenceDto(lang_code="en", book_code="mat", book_name="Matthew", chapter_num=1, verse_reference="3-6"), PassageReferenceDto(lang_code="en", book_code="mat", book_name="Matthew", chapter_num=1, verse_reference="9-10"), PassageReferenceDto(lang_code="en", book_code="mat", book_name="Matthew", chapter_num=1, verse_reference="15")])
    """
    book_codes = [
        passage_ref_dto.book_code for passage_ref_dto in passage_reference_dtos
    ]
    resource_types_ = resource_types(lang_code, ",".join(book_codes))
    resource_types_codes = [
        lang_resource_type_tuple[0] for lang_resource_type_tuple in resource_types_
    ]
    usfm_resource_types = [
        resource_type_
        for resource_type_ in resource_types_codes
        if resource_type_ in usfm_resource_types
    ]
    ulb_usfm_resource_types = [
        usfm_resource_type_
        for usfm_resource_type_ in usfm_resource_types
        if "ulb" in usfm_resource_type_
    ]
    usfm_books = []
    usfm_resource_type = ""
    if ulb_usfm_resource_types:  # Prefer ulb if available
        usfm_resource_type = ulb_usfm_resource_types[0]
    elif usfm_resource_types:
        usfm_resource_type = usfm_resource_types[0]
    if usfm_resource_type:
        usfm_book = None
        for book_code in book_codes:
            current_task.update_state(state="Locating assets")
            resource_lookup_dto_ = resource_lookup_dto(
                lang_code, usfm_resource_type, book_code
            )
            if resource_lookup_dto_ and resource_lookup_dto_.url:
                current_task.update_state(state="Provisioning asset files")
                resource_dir = prepare_resource_filepath(resource_lookup_dto_)
                provision_asset_files(resource_lookup_dto_.url, resource_dir)
                current_task.update_state(state="Parsing asset files")
                usfm_book = usfm_book_content(
                    resource_lookup_dto_,
                    resource_dir,
                )
                for chapter_num_, chapter_ in usfm_book.chapters.items():
                    usfm_book.chapters[chapter_num_].verses = split_chapter_into_verses(
                        chapter_
                    )
                usfm_books.append(usfm_book)
    current_task.update_state(state="Assembling content")
    passages = []
    for passage_ref_dto in passage_reference_dtos:
        logger.debug("passage_ref_dto: %s", passage_ref_dto)
        selected_usfm_books = [
            usfm_book_
            for usfm_book_ in usfm_books
            if usfm_book_.lang_code == lang_code
            and usfm_book_.book_code == passage_ref_dto.book_code
            and usfm_book_.resource_type_name
            == resource_type_codes_and_names[usfm_resource_type]
        ]
        verse_text = ""
        selected_usfm_book = None
        if selected_usfm_books:
            selected_usfm_book = selected_usfm_books[0]
        if selected_usfm_book:
            verse_text = get_verse_text(passage_ref_dto, selected_usfm_book)
        else:
            verse_text = ""
        non_book_name_portion_of_reference = (
            f"{passage_ref_dto.chapter_num}:{passage_ref_dto.verse_reference}"
        )
        nationalized_reference = (
            f"{selected_usfm_book.national_book_name} {non_book_name_portion_of_reference}"
            if selected_usfm_book and non_book_name_portion_of_reference
            else passage_ref_dto.verse_reference
        )
        passage_dto = PassageDto(
            passage_reference=nationalized_reference,
            passage_text=verse_text,
        )
        passages.append(passage_dto)
    current_task.update_state(state="Converting to Docx")
    generate_docx(passages, docx_filepath_, lang_code)
    return docx_filepath_


def generate_docx(
    passage_dtos: list[PassageDto],
    docx_filepath: str,
    lang_code: str,
) -> None:
    doc = Document()
    html_to_docx = HtmlToDocx()
    for passage_dto in passage_dtos:
        html_to_docx.add_html_to_document(passage_dto.passage_reference, doc)
        html_to_docx.add_html_to_document(passage_dto.passage_text, doc)
    doc = add_footer(doc)
    doc = add_header(doc, lang_code, header_text="Passages")
    doc.save(docx_filepath)
