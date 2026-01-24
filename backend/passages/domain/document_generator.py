import json
import time
from typing import Mapping, Sequence, TYPE_CHECKING

from celery import current_task
from doc.config import settings
from doc.domain import worker
from doc.domain.bible_books import BOOK_NAMES
from doc.domain.email_utils import send_email_with_attachment, should_send_email
from doc.domain.model import Attachment
from doc.domain.parsing import split_chapter_into_verses, usfm_book_content
from doc.domain.resource_lookup import (
    book_codes_for_lang_from_usfm_only,
    prepare_resource_filepath,
    provision_asset_files,
    resource_lookup_dto,
    resource_types,
)
from doc.reviewers_guide.model import BibleReference
from doc.utils.file_utils import docx_filepath, file_needs_update
from doc.utils.text_utils import maybe_correct_book_name
from docx import Document
from docx.oxml import OxmlElement, parse_xml
from docx.shared import Inches, RGBColor

from htmldocx import HtmlToDocx  # type: ignore
from passages.domain.model import (
    Passage,
    BibleReferenceWithAvailability as PassageReference,
)
from passages.domain.parser import verse_text_html
from passages.domain.stet_verse_list_parser import BOOK_INDEX, parse_bible_blocks
from passages.utils.docx_utils import add_footer, add_header
from pydantic import Json

from docx.table import _Cell, _Row


if TYPE_CHECKING:
    from typing import TypeAlias

    Cell: TypeAlias = _Cell
    Row: TypeAlias = _Row
else:
    Cell = _Cell
    Row = _Row

logger = settings.logger(__name__)


def generate_docx_document(
    lang_code: str,
    lang_name: str,
    passage_reference_dtos: list[PassageReference],
    document_request_key_: str,
    docx_filepath_: str,
    working_dir: str = settings.WORKING_DIR,
    output_dir: str = settings.DOCUMENT_OUTPUT_DIR,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    resource_type_codes_and_names: Mapping[
        str, str
    ] = settings.RESOURCE_TYPE_CODES_AND_NAMES,
) -> str:
    """Generate the content for the Passages document"""
    book_codes = list(
        {
            passage_ref_dto.reference.book_code
            for passage_ref_dto in passage_reference_dtos
        }
    )
    resource_types_ = resource_types(lang_code, ",".join(book_codes))
    resource_types_codes = list(
        {lang_resource_type_tuple[0] for lang_resource_type_tuple in resource_types_}
    )
    usfm_resource_types = list(
        {
            resource_type_
            for resource_type_ in resource_types_codes
            if resource_type_ in usfm_resource_types
        }
    )
    ulb_usfm_resource_types = list(
        {
            usfm_resource_type_
            for usfm_resource_type_ in usfm_resource_types
            if "ulb" in usfm_resource_type_
        }
    )
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
                    False,
                )
                for chapter_num_, chapter_ in usfm_book.chapters.items():
                    usfm_book.chapters[chapter_num_].verses = split_chapter_into_verses(
                        chapter_
                    )
                usfm_books.append(usfm_book)
    current_task.update_state(state="Assembling content")
    passages = []
    for passage_ref_dto in passage_reference_dtos:
        reference = passage_ref_dto.reference
        selected_usfm_books = [
            usfm_book_
            for usfm_book_ in usfm_books
            if usfm_book_.lang_code == lang_code
            and usfm_book_.book_code == reference.book_code
            and usfm_book_.resource_type_name
            == resource_type_codes_and_names[usfm_resource_type]
        ]
        verse_text_html_ = ""
        selected_usfm_book = None
        if selected_usfm_books:
            selected_usfm_book = selected_usfm_books[0]
        if selected_usfm_book:
            verse_text_html_ = verse_text_html(reference, selected_usfm_book)
        else:
            verse_text_html_ = ""
        non_book_name_portion_of_reference = ""
        if (
            reference.end_chapter
            and reference.end_chapter > 0
            and reference.end_chapter_verse_ref
        ):
            non_book_name_portion_of_reference = f"{reference.start_chapter}:{reference.start_chapter_verse_ref}-{reference.end_chapter}:{reference.end_chapter_verse_ref}"
        else:
            non_book_name_portion_of_reference = (
                f"{reference.start_chapter}:{reference.start_chapter_verse_ref}"
            )
        localized_reference = (
            f"{selected_usfm_book.national_book_name} {non_book_name_portion_of_reference}"
            if selected_usfm_book and non_book_name_portion_of_reference
            else f"{reference.book_name} {non_book_name_portion_of_reference}"
        )
        passage = Passage(
            bible_reference=localized_reference,
            passage_text=verse_text_html_,
            is_available=passage_ref_dto.is_available,
        )
        passages.append(passage)
    current_task.update_state(state="Converting to Docx")
    generate_docx(passages, docx_filepath_, lang_code, lang_name)
    return docx_filepath_


def generate_docx(
    passage_dtos: list[Passage],
    docx_filepath: str,
    lang_code: str,
    lang_name: str,
    show_notes_column: bool = False,  # TODO make a UI option, for now default to False
) -> None:
    """Generate the Passages output document in docx format"""
    TOTAL_WIDTH = Inches(6.0)
    doc = Document()
    html_to_docx = HtmlToDocx()
    for passage_dto in passage_dtos:
        if show_notes_column:
            table = doc.add_table(rows=1, cols=2)
            left_col_width = Inches(4.0)
            right_col_width = Inches(2.0)
            col_widths = [left_col_width, right_col_width]
        else:
            table = doc.add_table(rows=1, cols=1)
            col_widths = [TOTAL_WIDTH]
        table.autofit = False
        table.allow_autofit = False
        # Apply column + cell widths explicitly
        for i, width in enumerate(col_widths):
            table.columns[i].width = width
            cell = table.cell(0, i)
            cell.width = width
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            tcW = OxmlElement("w:tcW")
            tcW.set(f"{{{WORD_NAMESPACE}}}w", str(int(width.inches * 1440)))
            tcW.set(f"{{{WORD_NAMESPACE}}}type", "dxa")
            tcPr.append(tcW)
        # Fill left (or only) cell
        cell_left = table.cell(0, 0)
        # Add bible reference with color depending on availability
        p = cell_left.add_paragraph()  # create a fresh paragraph for control
        run = p.add_run(passage_dto.bible_reference)
        # run.bold = True  # optional – if you want it emphasized
        # run.font.size = Pt(10)                  # optional
        if passage_dto.is_available:
            run.font.color.rgb = RGBColor(102, 118, 139)  # ≈ #66768B
        else:
            run.font.color.rgb = RGBColor(176, 184, 195)  # ≈ #B0B8C3
        # Then add the passage text (still using html_to_docx if it has other formatting)
        html_to_docx.add_html_to_document(
            passage_dto.passage_text,
            cell_left,
        )
        # Fill right notes column only if enabled
        if show_notes_column:
            cell_right = table.cell(0, 1)
            cell_right.text = ""
            add_vertical_line(cell_right)
    doc = add_footer(doc)
    doc = add_header(doc, lang_name, header_text="Passages")
    doc.save(docx_filepath)


# Define the WordprocessingML namespace
WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def add_vertical_line(cell: Cell) -> None:
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
    passage_reference_dtos: list[PassageReference],
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
            f"{passage_reference.reference.book_code}_{passage_reference.reference.start_chapter}_{passage_reference.reference.start_chapter_verse_ref.translate(translation_table)}"
            for passage_reference in passage_reference_dtos
        ]
    )
    document_request_key_ = f"{lang_code}_{passages_key}_passages"
    if len(document_request_key_) >= max_filename_len:
        # Likely the generated filename was too long for the OS where this is
        # running. In that case, use the current time as a document_request_key
        # value as doing so results in an acceptably short length.
        timestamp_components = str(time.time()).split(".")
        return f"{timestamp_components[0]}_{timestamp_components[1]}"
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
    docx_filepath_prefix: str = "passages_",
    book_names: dict[str, str] = BOOK_NAMES,
) -> Json[str]:
    passage_reference_dtos_list = json.loads(passage_reference_dtos_json)
    passage_reference_dtos = [
        PassageReference(**d) for d in passage_reference_dtos_list
    ]
    logger.debug(
        "passed args: lang_code: %s, passage_references: %s, email_adress: %s",
        lang_code,
        passage_reference_dtos,
        email_address,
    )
    document_request_key_ = document_request_key(lang_code, passage_reference_dtos)
    docx_filepath_ = f"{docx_filepath(document_request_key_, docx_filepath_prefix)}"
    logger.debug("docx_filepath_: %s", docx_filepath_)
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


@worker.app.task
def stet_exhaustive_verse_list(
    lang_code: str = "en",
    filepath: str = "backend/passages/data/Spiritual_Terms_Evaluation_Exhaustive_Verse_List.txt",
) -> Sequence[BibleReference]:
    """
    >>> from passages.domain.document_generator import stet_exhaustive_verse_list
    >>> result = stet_exhaustive_verse_list()
    >>> result[0]
    Matthew 10:1
    """
    bible_references = []
    with open(filepath, "r") as fi:
        text = fi.read()
        parsed = parse_bible_blocks(text)
        for sublist in parsed.values():
            for value in sublist:
                if len(value.split()) >= 2:
                    bible_references.append(parse_bible_reference(value))
    # Remove duplicates and sort based on the book index, chapter, and verse
    unique_bible_references = sorted(
        set(bible_references),
        key=lambda ref: (
            BOOK_INDEX[ref.book_code],
            ref.start_chapter,
            ref.start_chapter_verse_ref,
        ),
    )
    # Localize the book names
    book_name_map = {
        book_code_and_name[0]: book_code_and_name[1]
        for book_code_and_name in book_codes_for_lang_from_usfm_only(lang_code)
    }
    for bible_reference in unique_bible_references:
        maybe_localized_book_name = book_name_map.get(
            bible_reference.book_code, bible_reference.book_name
        )
        logger.debug("maybe_localized_book_name: %s", maybe_localized_book_name)
        localized_book_name = maybe_correct_book_name(
            lang_code, maybe_localized_book_name
        )
        bible_reference.book_name = localized_book_name
    return unique_bible_references


def get_book_code(book_name: str) -> str:
    return next(code for code, name in BOOK_NAMES.items() if name == book_name)


def parse_bible_reference(book_and_reference_raw: str) -> BibleReference:
    book_name_and_reference = book_and_reference_raw.split()
    book_name = (
        " ".join(book_name_and_reference[:-1])
        if len(book_name_and_reference) > 2
        else book_name_and_reference[0]
    )
    chapter_reference = book_name_and_reference[-1]
    chapter = int(chapter_reference.split(":")[0])
    chapter_verse_ref = chapter_reference.split(":")[1]
    bible_reference = BibleReference(
        book_code=get_book_code(book_name),
        book_name=book_name,
        start_chapter=chapter,
        start_chapter_verse_ref=chapter_verse_ref,
        end_chapter=None,
        end_chapter_verse_ref=None,
    )
    return bible_reference
