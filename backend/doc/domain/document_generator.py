"""
Entrypoint for backend. Here incoming document requests are processed
and eventually a final document produced.
"""

import subprocess
import time
from datetime import datetime
from os.path import exists, join
from typing import Any, Optional, Sequence, cast

from celery import current_task
from doc.config import settings
from doc.domain import parsing, resource_lookup, worker
from doc.domain.assembly_strategies.assembly_strategies_book_then_lang_by_chapter import (
    assemble_content_by_book_then_lang,
)
from doc.domain.assembly_strategies.assembly_strategies_lang_then_book_by_chapter import (
    assemble_content_by_lang_then_book,
)
from doc.domain.assembly_strategies_docx import (
    assembly_strategies_book_then_lang_by_chapter as book_then_lang,
)
from doc.domain.assembly_strategies_docx import (
    assembly_strategies_lang_then_book_by_chapter as lang_then_book,
)
from doc.domain.assembly_strategies_docx.assembly_strategy_utils import add_hr
from doc.domain.bible_books import BOOK_NAMES
from doc.domain.email_utils import send_email_with_attachment, should_send_email
from doc.domain.model import (
    AssemblyLayoutEnum,
    AssemblyStrategyEnum,
    Attachment,
    BCBook,
    ChunkSizeEnum,
    DocumentRequest,
    DocumentRequestSourceEnum,
    ResourceLookupDto,
    ResourceRequest,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
)
from doc.reviewers_guide.model import RGBook
from doc.utils.docx_util import generate_docx_toc
from doc.utils.file_utils import (
    docx_filepath,
    epub_filepath,
    file_needs_update,
    html_filepath,
    pdf_filepath,
    write_file,
)
from doc.utils.template_env import env
from doc.utils.tw_utils import (
    contains_tw,
    filter_unique_by_lang_code,
    translation_words_section,
)
from docx.enum.section import WD_SECTION  # type: ignore
from docxcompose.composer import Composer  # type: ignore
from docxtpl import DocxTemplate  # type: ignore
from htmldocx import HtmlToDocx  # type: ignore
from pydantic import Json

logger = settings.logger(__name__)


# @worker.app.task(
#     autoretry_for=(Exception,),
#     retry_backoff=True,
#     retry_kwargs={"max_retries": 3},
# )
@worker.app.task
def generate_document(
    document_request_json: Json[Any], output_dir: str = settings.DOCUMENT_OUTPUT_DIR
) -> Json[Any]:
    """
    This is the main entry point for this module for non-docx generation.
    >>> from doc.domain import document_generator
    >>> document_request_json = '{"email_address":null,"assembly_strategy_kind":"lbo","assembly_layout_kind":"1c","layout_for_print":false,"resource_requests":[{"lang_code":"es-419","resource_type":"ulb","book_code":"mat"}],"generate_pdf":true,"generate_epub":false,"generate_docx":false,"chunk_size":"chapter","limit_words":false,"include_tn_book_intros":false,"document_request_source":"ui"}'
    >>> document_generator.generate_document(document_request_json)
    """
    logger.info("document_request_json: %s", document_request_json)
    current_task.update_state(state="Receiving request")
    document_request = DocumentRequest.parse_raw(document_request_json)
    document_request.assembly_layout_kind = select_assembly_layout_kind(
        document_request
    )
    # Generate the document request key that identifies this and
    # identical document requests.
    document_request_key_ = document_request_key(
        document_request.resource_requests,
        document_request.assembly_strategy_kind,
        document_request.assembly_layout_kind,
        document_request.chunk_size,
        document_request.limit_words,
    )
    html_filepath_ = html_filepath(document_request_key_)
    pdf_filepath_ = pdf_filepath(document_request_key_)
    epub_filepath_ = epub_filepath(document_request_key_)
    if file_needs_update(html_filepath_):
        # Update the state of the worker process. This is used by the
        # UI to report status.
        current_task.update_state(state="Locating assets")
        # HTML didn't exist in cache so go ahead and start by getting the
        # resource lookup DTOs for each resource request in the document
        # request.
        resource_lookup_dtos = []
        for resource_request in document_request.resource_requests:
            resource_lookup_dto = resource_lookup.resource_lookup_dto(
                resource_request.lang_code,
                resource_request.resource_type,
                resource_request.book_code,
            )
            if resource_lookup_dto:
                resource_lookup_dtos.append(resource_lookup_dto)
        # Determine which resource URLs were actually found.
        found_resource_lookup_dtos = [
            resource_lookup_dto
            for resource_lookup_dto in resource_lookup_dtos
            if resource_lookup_dto.url is not None
        ]
        # if not found_resource_lookup_dtos:
        #     raise exceptions.ResourceAssetFileNotFoundError(
        #         message="No supported resource assets were found"
        #     )
        current_task.update_state(state="Provisioning asset files")
        t0 = time.time()
        resource_dirs = [
            resource_lookup.prepare_resource_filepath(dto)
            for dto in found_resource_lookup_dtos
        ]
        for resource_dir, dto in zip(resource_dirs, found_resource_lookup_dtos):
            resource_lookup.provision_asset_files(dto.url, resource_dir)
        t1 = time.time()
        logger.info(
            "Time to provision asset files (acquire and write to disk): %s", t1 - t0
        )
        current_task.update_state(state="Parsing asset files")
        # Initialize found resources from their provisioned assets.
        t0 = time.time()
        usfm_books, tn_books, tq_books, tw_books, bc_books, rg_books = parsing.books(
            found_resource_lookup_dtos,
            resource_dirs,
            document_request.resource_requests,
            document_request.layout_for_print,
        )
        t1 = time.time()
        logger.info("Time to parse all resource content: %s", t1 - t0)
        current_task.update_state(state="Assembling content")
        content = assemble_content(
            document_request_key_,
            document_request,
            usfm_books,
            tn_books,
            tq_books,
            tw_books,
            bc_books,
            rg_books,
            found_resource_lookup_dtos,
        )
        if usfm_books:
            content = check_content_for_issues(content)
        content = create_title_page_and_wrap_in_template(
            content, document_request, found_resource_lookup_dtos, usfm_books
        )
        write_html_content_to_file(content, html_filepath_)
    else:
        logger.info("Cache hit for %s", html_filepath_)
    # Immediately return pre-built PDF if the document has previously been
    # generated and is fresh enough.
    if document_request.generate_pdf and file_needs_update(pdf_filepath_):
        current_task.update_state(state="Converting to PDF")
        convert_html_to_pdf(html_filepath_, pdf_filepath_, document_request_key_)
        if should_send_email(document_request.email_address):
            attachments = [
                Attachment(filepath=pdf_filepath_, mime_type=("application", "pdf"))
            ]
            current_task.update_state(state="Sending email")
            send_email_with_attachment(
                document_request.email_address,
                attachments,
                document_request_key_,
            )
    if document_request.generate_epub and file_needs_update(epub_filepath_):
        current_task.update_state(state="Converting to ePub")
        convert_html_to_epub(html_filepath_, epub_filepath_, document_request_key_)
        if should_send_email(document_request.email_address):
            attachments = [
                Attachment(
                    filepath=epub_filepath_, mime_type=("application", "epub+zip")
                )
            ]
            current_task.update_state(state="Sending email")
            send_email_with_attachment(
                document_request.email_address,
                attachments,
                document_request_key_,
            )
    return document_request_key_


@worker.app.task
def generate_docx_document(
    document_request_json: Json[Any],
    output_dir: str = settings.DOCUMENT_OUTPUT_DIR,
) -> Json[str]:
    """
    This is the alternative entry point for Docx document creation only.
    """
    document_request = DocumentRequest.parse_raw(document_request_json)
    logger.info(
        "document_request: %s",
        document_request,
    )
    document_request.assembly_layout_kind = select_assembly_layout_kind(
        document_request
    )
    # Generate the document request key that identifies this and
    # identical document requests.
    document_request_key_ = document_request_key(
        document_request.resource_requests,
        document_request.assembly_strategy_kind,
        document_request.assembly_layout_kind,
        document_request.chunk_size,
        document_request.limit_words,
    )
    html_filepath_ = html_filepath(document_request_key_)
    docx_filepath_ = docx_filepath(document_request_key_)
    if document_request.generate_docx and file_needs_update(docx_filepath_):
        # Update the state of the worker process. This is used by the
        # UI to report status.
        current_task.update_state(state="Locating assets")
        # Docx didn't exist in cache so go ahead and start by getting the
        # resource lookup DTOs for each resource request in the document
        # request.
        resource_lookup_dtos = []
        for resource_request in document_request.resource_requests:
            resource_lookup_dto = resource_lookup.resource_lookup_dto(
                resource_request.lang_code,
                resource_request.resource_type,
                resource_request.book_code,
            )
            if resource_lookup_dto:
                resource_lookup_dtos.append(resource_lookup_dto)
        # Determine which resource URLs were actually found.
        found_resource_lookup_dtos = [
            resource_lookup_dto
            for resource_lookup_dto in resource_lookup_dtos
            if resource_lookup_dto.url is not None
        ]
        current_task.update_state(state="Provisioning asset files")
        t0 = time.time()
        resource_dirs = [
            resource_lookup.prepare_resource_filepath(dto)
            for dto in found_resource_lookup_dtos
        ]
        for resource_dir, dto in zip(resource_dirs, found_resource_lookup_dtos):
            resource_lookup.provision_asset_files(dto.url, resource_dir)
        t1 = time.time()
        logger.info(
            "Time to provision asset files (acquire and write to disk): %s", t1 - t0
        )
        current_task.update_state(state="Parsing asset files")
        # Initialize found resources from their provisioned assets.
        t0 = time.time()
        usfm_books, tn_books, tq_books, tw_books, bc_books, rg_books = parsing.books(
            found_resource_lookup_dtos,
            resource_dirs,
            document_request.resource_requests,
            document_request.layout_for_print,
        )
        t1 = time.time()
        logger.info("Time to parse all resource content: %s", t1 - t0)
        current_task.update_state(state="Assembling content")
        composer = assemble_docx_content(
            document_request_key_,
            document_request,
            usfm_books,
            tn_books,
            tq_books,
            tw_books,
            bc_books,
            rg_books,
        )
        # TODO At this point, like in generate_document, we should check the
        # underlying HTML content to see if it contains verses and display a
        # message in the document to the end user if it does not (so that they
        # get some indication of why the scripture is missing).
        #
        # Construct sensical phrases to display for title1 and title2 on first
        # page of Word document.
        title1, title2 = get_languages_title_page_strings(
            found_resource_lookup_dtos, usfm_books
        )
        current_task.update_state(state="Converting to Docx")
        convert_html_to_docx(
            html_filepath_,
            docx_filepath_,
            composer,
            document_request.layout_for_print,
            title1,
            title2,
        )
        if should_send_email(document_request.email_address):
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
                document_request.email_address,
                attachments,
                document_request_key_,
            )
    else:
        logger.info("Cache hit for %s", docx_filepath_)
    return document_request_key_


def document_request_key(
    resource_requests: Sequence[ResourceRequest],
    assembly_strategy_kind: AssemblyStrategyEnum,
    assembly_layout_kind: AssemblyLayoutEnum,
    chunk_size: ChunkSizeEnum,
    limit_words: bool,
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
    the file suffix, e.g., ".html", to be appended.

    It is really useful to have filenames with semantic meaning and so
    those are preferred when possible, i.e., when the file name is not
    too long.
    """
    resource_request_keys = underscore.join(
        [
            hyphen.join(
                [
                    resource_request.lang_code,
                    resource_request.resource_type,
                    resource_request.book_code,
                ]
            )
            for resource_request in resource_requests
        ]
    )
    if any(contains_tw(resource_request) for resource_request in resource_requests):
        document_request_key = "{}_{}_{}_{}_{}".format(
            resource_request_keys,
            assembly_strategy_kind.value,
            assembly_layout_kind.value,
            chunk_size.value,
            "lwt" if limit_words else "lwf",
        )
    else:
        document_request_key = "{}_{}_{}_{}".format(
            resource_request_keys,
            assembly_strategy_kind.value,
            assembly_layout_kind.value,
            chunk_size.value,
        )
    if len(document_request_key) >= max_filename_len:
        # Likely the generated filename was too long for the OS where this is
        # running. In that case, use the current time as a document_request_key
        # value as doing so results in an acceptably short length.
        timestamp_components = str(time.time()).split(".")
        return "{}_{}".format(timestamp_components[0], timestamp_components[1])
    else:
        # Use the semantic filename which declaratively describes the
        # document request components.
        return document_request_key


def instantiated_html_header_template(
    template_lookup_key: str, title1: str, title2: str, title3: str
) -> str:
    template = env.get_template(template_lookup_key)
    timestring = datetime.now().ctime()
    return template.render(
        timestring=timestring, title1=title1, title2=title2, title3=title3
    )


def enclose_html_content(
    content: str,
    document_html_header: str,
    document_html_footer: str = "</body></html>",
) -> str:
    """
    Write the enclosing HTML header and footer elements around the
    HTML body content for the document.
    """
    return "{}{}{}".format(document_html_header, content, document_html_footer)


def document_html_header(
    assembly_layout_kind: Optional[AssemblyLayoutEnum],
    generate_docx: bool,
    title1: str,
    title2: str,
    title3: str,
) -> str:
    """
    Choose the appropriate HTML header given the
    assembly_layout_kind. The HTML header, naturally, contains the CSS
    definitions and they in turn can be used to affect visual
    compactness.
    """
    if generate_docx:
        template = env.get_template("html/header_no_css_enclosing.html")
        return template.render()

    if assembly_layout_kind and assembly_layout_kind in [
        AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
    ]:
        return instantiated_html_header_template(
            "html/header_compact_enclosing.html", title1, title2, title3
        )
    return instantiated_html_header_template(
        "html/header_enclosing.html", title1, title2, title3
    )


def assemble_content(
    document_request_key: str,
    document_request: DocumentRequest,
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    found_resource_lookup_dtos: Sequence[ResourceLookupDto],
) -> str:
    """
    Assemble and return the content from all requested resources according to the
    assembly_strategy requested.
    """
    t0 = time.time()
    content = ""
    if (
        document_request.assembly_strategy_kind
        == AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    ):
        content = "".join(
            assemble_content_by_lang_then_book(
                usfm_books,
                tn_books,
                tq_books,
                tw_books,
                bc_books,
                rg_books,
                cast(AssemblyLayoutEnum, document_request.assembly_layout_kind),
            )
        )
    elif (
        document_request.assembly_strategy_kind
        == AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
    ):
        content = "".join(
            assemble_content_by_book_then_lang(
                usfm_books,
                tn_books,
                tq_books,
                tw_books,
                bc_books,
                rg_books,
                cast(AssemblyLayoutEnum, document_request.assembly_layout_kind),
            )
        )
    t1 = time.time()
    logger.info("Time for interleaving document: %s", t1 - t0)
    t0 = time.time()
    # Add the translation words definition section for each language requested.
    unique_lang_codes = set()
    for tw_book in tw_books:
        if tw_book.lang_code not in unique_lang_codes:
            unique_lang_codes.add(tw_book.lang_code)
            content = "{}{}<hr/>".format(
                content,
                translation_words_section(
                    tw_book,
                    usfm_books,
                    document_request.limit_words,
                    document_request.resource_requests,
                ),
            )
    t1 = time.time()
    logger.info("Time for add TW content to document: %s", t1 - t0)
    return content


def create_title_page_and_wrap_in_template(
    content: str,
    document_request: DocumentRequest,
    found_resource_lookup_dtos: Sequence[ResourceLookupDto],
    usfm_books: Sequence[USFMBook],
) -> str:
    title1, title2 = get_languages_title_page_strings(
        found_resource_lookup_dtos, usfm_books
    )
    title3 = "Formatted for Translators"
    header = document_html_header(
        document_request.assembly_layout_kind,
        document_request.generate_docx,
        title1,
        title2,
        title3,
    )
    content = enclose_html_content(content, document_html_header=header)
    return content


def assemble_docx_content(
    document_request_key: str,
    document_request: DocumentRequest,
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
) -> Composer:
    """
    Assemble and return the content from all requested resources according to the
    assembly_strategy requested.
    """
    t0 = time.time()
    composer = None
    if (
        document_request.assembly_strategy_kind
        == AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER
    ):
        composer = lang_then_book.assemble_content_by_lang_then_book(
            usfm_books,
            tn_books,
            tq_books,
            tw_books,
            bc_books,
            rg_books,
            cast(AssemblyLayoutEnum, document_request.assembly_layout_kind),
            document_request.chunk_size,
        )
    elif (
        document_request.assembly_strategy_kind
        == AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
    ):
        composer = book_then_lang.assemble_content_by_book_then_lang(
            usfm_books,
            tn_books,
            tq_books,
            tw_books,
            bc_books,
            rg_books,
            cast(AssemblyLayoutEnum, document_request.assembly_layout_kind),
            document_request.chunk_size,
        )
    t1 = time.time()
    logger.info("Time for interleaving document: %s", t1 - t0)
    tw_subdocs = []
    if tw_books:
        html_to_docx = HtmlToDocx()
        t0 = time.time()
        # Add the translation words definition section for each language requested.
        unique_tw_books = filter_unique_by_lang_code(tw_books)
        for tw_book in unique_tw_books:
            tw_subdoc = html_to_docx.parse_html_string(
                translation_words_section(
                    tw_book,
                    usfm_books,
                    document_request.limit_words,
                    document_request.resource_requests,
                )
            )
            if tw_subdoc.paragraphs:
                p = tw_subdoc.paragraphs[-1]
                add_hr(p)
                tw_subdocs.append(tw_subdoc)
        t1 = time.time()
        logger.info("Time for adding TW content to document: %s", t1 - t0)
    # Now add any TW subdocs to the composer
    if composer:
        for tw_subdoc_ in tw_subdocs:
            composer.append(tw_subdoc_)
    return composer


# HTML to PDF converters:
# princexml ($$$$) (fastest); also available through docraptor api ($$) but slow,
# wkhtmltopdf via pdfkit (can't handle column-count directive so can't use due to
# multi-column layouts requirement),
# weasyprint (does a nice job, we use this),
# pagedjs-cli (does a really nice job, but is really slow - uses puppeteer underneath),
# electron-pdf (similar speed to wkhtmltopdf) which uses chrome underneath the hood,
# gotenburg which uses chrome under the hood and provides a nice api in Docker (untested),
# raw chrome headless (works well and is about the same speed as weasyprint),
# ebook-convert (faster than weasyprint, but does arbitrary page breaks in formatting and can't do headers and footers)
def convert_html_to_pdf(
    html_filepath: str,
    pdf_filepath: str,
    document_request_key: str,
) -> None:
    """
    Generate PDF from HTML and copy it to output directory.
    """
    assert exists(html_filepath)
    logger.info("Generating PDF %s...", pdf_filepath)
    t0 = time.time()
    # command = [
    #     "ebook-convert",
    #     html_filepath,
    #     pdf_filepath,
    #     "--disable-font-rescaling",
    # ]
    command = [
        "weasyprint",
        html_filepath,
        pdf_filepath,
    ]
    logger.info("Generate PDF command: %s", " ".join(command))
    subprocess.run(
        command,
        check=True,
        text=True,
    )
    t1 = time.time()
    logger.info("Time for converting HTML to PDF: %s", t1 - t0)


# HTML to ePub converters:
# pandoc (this doesn't respect two column),
# html-to-epub which is written in go (this doesn't respect two column),
# ebook-convert (this respects two column).
def convert_html_to_epub(
    html_filepath: str,
    epub_filepath: str,
    document_request_key: str,
) -> None:
    """Generate ePub from HTML and copy it to output directory."""
    assert exists(html_filepath)
    command = [
        "ebook-convert",
        html_filepath,
        epub_filepath,
        "--no-default-epub-cover",
    ]
    logger.info("Generate ePub command: %s", " ".join(command))
    t0 = time.time()
    subprocess.run(command, check=True, text=True)
    t1 = time.time()
    logger.info("Time for converting HTML to ePub: %s", t1 - t0)


def convert_html_to_docx(
    html_filepath: str,
    docx_filepath: str,
    composer: Composer,
    layout_for_print: bool,
    title1: str = "title1",
    title2: str = "title2",
    title3: str = "Formatted for Translators",
    docx_template_path: str = settings.DOCX_TEMPLATE_PATH,
    docx_compact_template_path: str = settings.DOCX_COMPACT_TEMPLATE_PATH,
) -> None:
    """Generate Docx and copy it to output directory."""
    t0 = time.time()
    # Get data for front page of Docx template.
    title1 = title1
    title2 = title2
    title3 = title3
    # fmt: off
    template_path = docx_compact_template_path if layout_for_print else docx_template_path
    # fmt: on
    doc = DocxTemplate(template_path)
    toc_path = generate_docx_toc(docx_filepath)
    toc = doc.new_subdoc(toc_path)
    context = {
        "title1": title1,
        "title2": title2,
        "title3": title3,
        "TOC": toc,
    }
    doc.render(context)
    # Start new section for different column layout
    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    new_section.start_type
    master = Composer(doc)
    # Add the main (non-front-matter) content.
    master.append(composer.doc)
    master.save(docx_filepath)
    t1 = time.time()
    logger.info("Time for converting HTML to Docx: %s", t1 - t0)


def cover_filepath(
    document_request_key: str, output_dir: str = settings.DOCUMENT_OUTPUT_DIR
) -> str:
    """Given document_request_key, return the HTML cover output file path."""
    return join(output_dir, "{}_cover.html".format(document_request_key))


def select_assembly_layout_kind(
    document_request: DocumentRequest,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    language_book_order: AssemblyStrategyEnum = AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER,
    book_language_order: AssemblyStrategyEnum = AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
    stet_strategy: AssemblyStrategyEnum = AssemblyStrategyEnum.STET_STRATEGY,
    one_column_compact: AssemblyLayoutEnum = AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
    sl_sr: AssemblyLayoutEnum = AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
    sl_sr_compact: AssemblyLayoutEnum = AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
    one_column: AssemblyLayoutEnum = AssemblyLayoutEnum.ONE_COLUMN,
    stet_layout: AssemblyLayoutEnum = AssemblyLayoutEnum.STET_LAYOUT,
) -> AssemblyLayoutEnum:
    """
    Make an intelligent choice of what layout to use given the
    DocumentRequest instance the user has requested. Note that prior to
    this, we've already validated the DocumentRequest instance in the
    DocumentRequest's validator. If we hadn't then we wouldn't be able
    to make the assumptions this function makes.
    """
    # The assembly_layout_kind does not get set by the UI, so if it is set
    # now that means that the request is coming from a client other than the UI.
    # In either case validation of the DocumentRequest instance will have
    # already occurred by this point thus ensuring that the document
    # request's values are valid in which case we can simply return the
    # assembly_layout_kind that was set.
    if (
        document_request.document_request_source == DocumentRequestSourceEnum.TEST
        and document_request.assembly_layout_kind
    ):
        return document_request.assembly_layout_kind
    if document_request.assembly_strategy_kind == stet_strategy:
        return stet_layout
    if (
        document_request.layout_for_print
        and document_request.assembly_strategy_kind == language_book_order
    ):
        return one_column_compact
    elif (
        not document_request.layout_for_print
        and document_request.assembly_strategy_kind == language_book_order
    ):
        return one_column
    elif (
        not document_request.layout_for_print
        and document_request.assembly_strategy_kind == book_language_order
    ):
        # return sl_sr
        return one_column
    elif (
        document_request.layout_for_print
        and document_request.assembly_strategy_kind == book_language_order
    ):
        # return sl_sr_compact
        return one_column_compact
    return one_column


def write_html_content_to_file(
    content: str,
    output_filename: str,
) -> None:
    """
    Write HTML content to file.
    """
    logger.info("About to write HTML to %s", output_filename)
    # Write the HTML file to disk.
    write_file(
        output_filename,
        content,
    )


def check_content_for_issues(
    content: str,
) -> str:
    """
    Check for defects and notify support via logs of possible source
    content issues. Also modify the content to include a message for
    the end user to inform them that there is a problem with the
    underlying source USFM and that the translators need to fix it.
    This will help them understand why they have missing content.
    """
    logger.info(
        "Checking USFM content for issues before creating requested document..."
    )
    if 'class="verse"' not in content:
        logger.info("No verses found in HTML")
        logger.info(
            "About to modify content to include message notifying user of problem with USFM source text format..."
        )
        updated_content = "NOTE: There are issues with the requested underlying scripture USFM text that make it unusable by this system until translators fix the issue for the language(s), book(s), and resource(s) combination you have requested."
        logger.info(
            "Due to potential issues with the source content, here is the HTML content for you to inspect: %s",
            content,
        )
        return updated_content
    return content


def get_languages_title_page_strings(
    resource_lookup_dtos: Sequence[ResourceLookupDto],
    usfm_books: Sequence[USFMBook],
) -> tuple[str, str]:
    lang_codes = list(
        {resource_lookup_dto.lang_code for resource_lookup_dto in resource_lookup_dtos}
    )
    lang0_book_names = set()
    lang0_resource_type_names = set()
    lang1_book_names = set()
    lang1_resource_type_names = set()
    lang0_title, lang1_title = "", ""
    if usfm_books:
        lang0_books = [
            usfm_book
            for usfm_book in usfm_books
            if usfm_book.lang_code == lang_codes[0]
        ]
        for book in lang0_books:
            if book.national_book_name:
                lang0_book_names.add(book.national_book_name)
            lang0_resource_type_names.add(book.resource_type_name)
        lang0_title = f"{lang0_books[0].lang_name}: {', '.join(sorted(lang0_resource_type_names))} for {', '.join(sorted(lang0_book_names))}"
    else:
        language0_resource_lookup_dtos = [
            resource_lookup_dto
            for resource_lookup_dto in resource_lookup_dtos
            if resource_lookup_dto.lang_code == lang_codes[0]
        ]
        for dto in language0_resource_lookup_dtos:
            lang0_book_names.add(BOOK_NAMES[dto.book_code])
            lang0_resource_type_names.add(dto.resource_type_name)
        if language0_resource_lookup_dtos:
            lang0_title = f"{language0_resource_lookup_dtos[0].lang_name}: {', '.join(sorted(lang0_resource_type_names))} for {', '.join(sorted(lang0_book_names))}"
    if len(lang_codes) > 1:
        lang1_books = [
            usfm_book
            for usfm_book in usfm_books
            if usfm_book.lang_code == lang_codes[1]
        ]
        for book in lang1_books:
            if book.national_book_name:
                lang1_book_names.add(book.national_book_name)
            lang1_resource_type_names.add(book.resource_type_name)
        if lang1_books:
            lang1_title = f"{lang1_books[0].lang_name}: {', '.join(sorted(lang1_resource_type_names))} for {', '.join(sorted(lang1_book_names))}"
        else:
            language1_resource_lookup_dtos = [
                resource_lookup_dto
                for resource_lookup_dto in resource_lookup_dtos
                if resource_lookup_dto.lang_code == lang_codes[1]
            ]
            for dto in language1_resource_lookup_dtos:
                lang1_book_names.add(BOOK_NAMES[dto.book_code])
                lang1_resource_type_names.add(dto.resource_type_name)
            if language1_resource_lookup_dtos:
                lang1_title = f"{language1_resource_lookup_dtos[0].lang_name}: {', '.join(sorted(lang1_resource_type_names))} for {', '.join(sorted(lang1_book_names))}"
    return lang0_title, lang1_title


if __name__ == "__main__":
    # To run the doctests in the this module, in the root of the project do:
    # FROM_EMAIL_ADDRESS=... python backend/doc/domain/resource_lookup.py
    # See https://docs.python.org/3/library/doctest.html
    # for more details.
    import doctest

    doctest.testmod()
