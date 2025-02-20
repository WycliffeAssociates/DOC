import json
import time
from typing import Mapping, Sequence

from celery import current_task
from document.config import settings
from document.domain import worker
from document.domain.bible_books import BOOK_NAMES
from document.domain.email import send_email_with_attachment, should_send_email
from document.domain.model import Attachment
from document.domain.parsing import split_chapter_into_verses, usfm_book_content
from document.domain.resource_lookup import (
    RESOURCE_TYPE_CODES_AND_NAMES,
    prepare_resource_filepath,
    provision_asset_files,
    resource_lookup_dto,
    resource_types,
)
from document.passages.docx_utils import add_footer, add_header
from document.passages.model import PassageDto, PassageReferenceDto
from document.passages.parser import verse_text_html
from document.utils.file_utils import docx_filepath, file_needs_update
from docx import Document  # type: ignore
from docx.oxml import OxmlElement  # type: ignore
from docx.oxml import parse_xml
from docx.shared import Inches  # type: ignore
from docx.table import _Cell  # type: ignore
from htmldocx import HtmlToDocx  # type: ignore
from pydantic import Json

logger = settings.logger(__name__)


def generate_docx_document(
    lang_code: str,
    lang_name: str,
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
        verse_text_html_ = ""
        selected_usfm_book = None
        if selected_usfm_books:
            selected_usfm_book = selected_usfm_books[0]
        if selected_usfm_book:
            verse_text_html_ = verse_text_html(passage_ref_dto, selected_usfm_book)
        else:
            verse_text_html_ = ""
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
            passage_text=verse_text_html_,
        )
        passages.append(passage_dto)
    current_task.update_state(state="Converting to Docx")
    generate_docx(passages, docx_filepath_, lang_code, lang_name)
    return docx_filepath_


def generate_docx(
    passage_dtos: list[PassageDto],
    docx_filepath: str,
    lang_code: str,
    lang_name: str,
) -> None:
    doc = Document()
    html_to_docx = HtmlToDocx()
    for passage_dto in passage_dtos:
        table = doc.add_table(rows=1, cols=2)
        table.autofit = False  # Disable automatic resizing
        table.allow_autofit = False  # Ensure fixed widths
        left_col_width = Inches(4.0)  # 2/3 of total
        right_col_width = Inches(2.0)  # 1/3 of total
        # Set column widths using preferred width settings
        table.columns[0].width = left_col_width
        table.columns[1].width = right_col_width
        for i, width in enumerate([left_col_width, right_col_width]):
            cell = table.cell(0, i)
            cell.width = width
            # Apply preferred width at the XML level
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            tcW = OxmlElement("w:tcW")
            tcW.set(f"{{{WORD_NAMESPACE}}}w", str(int(width.inches * 1440)))
            tcW.set(f"{{{WORD_NAMESPACE}}}type", "dxa")
            tcPr.append(tcW)
        # Fill left cell
        cell_left = table.cell(0, 0)
        html_to_docx.add_html_to_document(passage_dto.passage_reference, cell_left)
        html_to_docx.add_html_to_document(passage_dto.passage_text, cell_left)
        # Fill right cell (empty, just add vertical line)
        cell_right = table.cell(0, 1)
        cell_right.text = ""
        add_vertical_line(cell_right)
    doc = add_footer(doc)
    doc = add_header(doc, lang_name, header_text="Passages")
    doc.save(docx_filepath)


# Define the WordprocessingML namespace
WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def add_vertical_line(cell: _Cell) -> None:
    """Adds a vertical line to the left side of the given table cell."""
    cell_xml = cell._tc  # Access the underlying XML of the cell
    # Ensure the `<w:tcPr>` (table cell properties) element exists
    tc_pr = cell_xml.find(f"{{{WORD_NAMESPACE}}}tcPr")
    if tc_pr is None:
        tc_pr = parse_xml(f'<w:tcPr xmlns:w="{WORD_NAMESPACE}"/>')
        cell_xml.append(tc_pr)
    # Add the left border
    borders_xml = f"""
    <w:tcBorders xmlns:w="{WORD_NAMESPACE}">
        <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
    </w:tcBorders>
    """
    tc_pr.append(parse_xml(borders_xml))


def document_request_key(
    lang_code: str,
    passage_reference_dtos: list[PassageReferenceDto],
    max_filename_len: int = 240,
    underscore: str = "_",
    hyphen: str = "-",
) -> str:
    """
    Create and return the document_request_key. The
    document_request_key uniquely identifies a document request.

    If the document request key is max_filename_len or more characters
    in length, then switch to using a shorter string that is based on the
    current time. The reason for this is that the document request key is
    used as the file name (with suffix appended) and each OS has a limit
    to how long a file name may be. max_filename_len should make room for
    the file suffix, e.g., ".docx", to be appended.

    It is really useful to have filenames with semantic meaning and so
    those are preferred when possible, i.e., when the file name is not
    too long.
    """

    translation_table = str.maketrans(":;,-", "____")
    passages_key = underscore.join(
        [
            f"{passage_reference.book_code}_{passage_reference.chapter_num}_{passage_reference.verse_reference.translate(translation_table)}"
            for passage_reference in passage_reference_dtos
        ]
    )
    document_request_key_ = f"{lang_code}_{passages_key}_passages"
    if len(document_request_key_) >= max_filename_len:
        # Likely the generated filename was too long for the OS where this is
        # running. In that case, use the current time as a document_request_key
        # value as doing so results in an acceptably short length.
        timestamp_components = str(time.time()).split(".")
        return "{}_{}".format(timestamp_components[0], timestamp_components[1])
    else:
        # Use the semantic filename which declaratively describes the
        # document request components.
        return document_request_key_


@worker.app.task
def generate_passages_docx_document(
    lang_code: str,
    lang_name: str,
    passage_reference_dtos_json: str,
    email_address: str,
    book_names: dict[str, str] = BOOK_NAMES,
) -> Json[str]:
    passage_reference_dtos_list = json.loads(passage_reference_dtos_json)
    passage_reference_dtos = [
        PassageReferenceDto(**d) for d in passage_reference_dtos_list
    ]
    logger.debug(
        "passed args: lang_code: %s, passage_references: %s, email_adress: %s",
        lang_code,
        passage_reference_dtos,
        email_address,
    )
    document_request_key_ = document_request_key(lang_code, passage_reference_dtos)
    docx_filepath_ = docx_filepath(document_request_key_)
    if file_needs_update(docx_filepath_):
        generate_docx_document(
            lang_code,
            lang_name,
            passage_reference_dtos,
            document_request_key_,
            docx_filepath_,
        )
        if should_send_email(email_address):
            attachments = [
                Attachment(
                    filepath=docx_filepath_,
                    mime_type=(
                        "application",
                        "vnd.openxmlformats-officedocument.wordprocessingml.document",
                    ),
                )
            ]
            current_task.update_state(state="Sending email")
            send_email_with_attachment(
                email_address,
                attachments,
                document_request_key_,
            )
    else:
        logger.debug("Cache hit for %s", docx_filepath_)
    return document_request_key_
