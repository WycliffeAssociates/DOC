"""
Entrypoint for backend. Here incoming document requests are processed
and eventually a final document produced.
"""

import asyncio
import concurrent.futures
import os
import shutil
import smtplib
import subprocess
import time
from collections.abc import Iterable, Mapping, Sequence
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itertools import tee
from typing import Any, Optional

import jinja2
import more_itertools
import pdfkit  # type: ignore
import requests
import toolz  # type: ignore
from celery import Celery, current_task
from celery.app.task import Task
from document.config import settings
from document.domain import (
    assembly_strategies,
    bible_books,
    model,
    parsing,
    resource_lookup,
    worker,
)
from document.utils import file_utils, number_utils
from fastapi import HTTPException, status
from more_itertools import partition
from pydantic import BaseModel, Json
from requests.exceptions import HTTPError

logger = settings.logger(__name__)

COMMASPACE = ", "
HYPHEN = "-"
UNDERSCORE = "_"

MAX_FILENAME_LENGTH = 240

NUM_ZEROS = 3


def resource_book_content_units(
    found_resource_lookup_dtos_iter: Iterable[model.ResourceLookupDto],
    resource_dirs_iter: Iterable[str],
    resource_requests: Sequence[model.ResourceRequest],
    layout_for_print: bool,
) -> Iterable[model.BookContent]:
    """Parse asset content for later use in document interleaving."""
    for resource_lookup_dto, resource_dir in zip(
        found_resource_lookup_dtos_iter, resource_dirs_iter
    ):
        yield parsing.book_content(
            resource_lookup_dto, resource_dir, resource_requests, layout_for_print
        )


def document_request_key(
    resource_requests: Sequence[model.ResourceRequest],
    assembly_strategy_kind: model.AssemblyStrategyEnum,
    assembly_layout_kind: model.AssemblyLayoutEnum,
    max_filename_len: int = MAX_FILENAME_LENGTH,
) -> str:
    """
    Create and return the document_request_key. The
    document_request_key uniquely identifies a document request.

    If the document request key is max_filename_len or more characters
    in length, then switch to using a shorter string that is based on the
    current time. The reason for this is that the document request key is
    used as the file name (with suffix appended) and each OS has a limit
    to how long a file name may be. max_filename_len should make room for
    the a file suffix, e.g., ".html", to be appended.

    It is really useful to have filenames with semantic meaning and so
    those are preferred when possible, i.e., when the file name is not
    too long.
    """
    resource_request_keys = UNDERSCORE.join(
        [
            HYPHEN.join(
                [
                    resource_request.lang_code,
                    resource_request.resource_type,
                    resource_request.resource_code,
                ]
            )
            for resource_request in resource_requests
        ]
    )
    document_request_key = "{}_{}_{}".format(
        resource_request_keys, assembly_strategy_kind.value, assembly_layout_kind.value
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


def template_path(
    key: str, template_paths_map: Mapping[str, str] = settings.TEMPLATE_PATHS_MAP
) -> str:
    """
    Return the path to the requested template give a lookup key.
    Return a different path if the code is running inside the Docker
    container.
    """
    return template_paths_map[key]


def template(template_lookup_key: str) -> str:
    """Return template as string."""
    with open(template_path(template_lookup_key), "r") as filepath:
        template = filepath.read()
    return template


def instantiated_template(template_lookup_key: str, dto: BaseModel) -> str:
    """
    Instantiate Jinja2 template with dto BaseModel instance. Return
    instantiated template as string.
    """
    with open(template_path(template_lookup_key), "r") as filepath:
        template = filepath.read()
    env = jinja2.Environment(autoescape=True).from_string(template)
    return env.render(data=dto)


def enclose_html_content(
    content: str,
    document_html_header: str,
    document_html_footer: str = template("footer_enclosing"),
) -> str:
    """
    Write the enclosing HTML header and footer elements around the
    HTML body content for the document.
    """
    return "{}{}{}".format(document_html_header, content, document_html_footer)


def document_html_header(
    assembly_layout_kind: Optional[model.AssemblyLayoutEnum],
) -> str:
    """
    Choose the appropriate HTML header given the
    assembly_layout_kind. The HTML header, naturally, contains the CSS
    definitions and they in turn can be used to affect visual
    compactness.
    """
    if assembly_layout_kind and assembly_layout_kind in [
        model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
    ]:
        return template("header_compact_enclosing")
    else:
        return template("header_enclosing")


def uses_section(
    uses: Sequence[model.TWUse],
    translation_word_verse_section_header_str: str = settings.TRANSLATION_WORD_VERSE_SECTION_HEADER_STR,
    unordered_list_begin_str: str = settings.UNORDERED_LIST_BEGIN_STR,
    translation_word_verse_ref_item_fmt_str: str = settings.TRANSLATION_WORD_VERSE_REF_ITEM_FMT_STR,
    unordered_list_end_str: str = settings.UNORDERED_LIST_END_STR,
    book_numbers: Mapping[str, str] = bible_books.BOOK_NUMBERS,
    book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
    num_zeros: int = NUM_ZEROS,
) -> model.HtmlContent:
    """
    Construct and return the 'Uses:' section which comes at the end of
    a translation word definition and wherein each item points to
    verses (as targeted by lang_code, book_id, chapter_num, and
    verse_num) wherein the word occurs.
    """
    html: list[model.HtmlContent] = []
    html.append(translation_word_verse_section_header_str)
    html.append(unordered_list_begin_str)
    for use in uses:
        html_content_str = model.HtmlContent(
            translation_word_verse_ref_item_fmt_str.format(
                use.lang_code,
                book_numbers[use.book_id].zfill(num_zeros),
                str(use.chapter_num).zfill(num_zeros),
                str(use.verse_num).zfill(num_zeros),
                book_names[use.book_id],
                use.chapter_num,
                use.verse_num,
            )
        )
        html.append(html_content_str)
    html.append(unordered_list_end_str)
    return model.HtmlContent("\n".join(html))


def translation_words_section(
    book_content_unit: model.TWBook,
    include_uses_section: bool = True,
    resource_type_name_fmt_str: str = settings.RESOURCE_TYPE_NAME_FMT_STR,
    opening_h3_fmt_str: str = settings.OPENING_H3_FMT_STR,
    opening_h3_with_id_fmt_str: str = settings.OPENING_H3_WITH_ID_FMT_STR,
) -> Iterable[model.HtmlContent]:
    """
    Build and return the translation words definition section, i.e.,
    the list of all translation words for this language, book
    combination. Include a 'Uses:' section that points from the
    translation word back to the verses which include the translation
    word if include_uses_section is True.
    """
    if book_content_unit.name_content_pairs:
        yield model.HtmlContent(
            resource_type_name_fmt_str.format(book_content_unit.resource_type_name)
        )

    for name_content_pair in book_content_unit.name_content_pairs:
        # NOTE Another approach to including all translation words would be to
        # only include words in the translation section which occur in current
        # lang_code, book verses. The problem with this is that translation note
        # 'See also' sections often refer to translation words that are not part
        # of the lang_code/book content and thus those links are dead unless we
        # include them even if they don't have any 'Uses' section. In other
        # words, by limiting the translation words we limit the ability of those
        # using the interleaved document to gain deeper understanding of the
        # interrelationships of words.

        # Make linking work: have to add ID to tags for anchor
        # links to work.
        name_content_pair.content = model.HtmlContent(
            name_content_pair.content.replace(
                opening_h3_fmt_str.format(name_content_pair.localized_word),
                opening_h3_with_id_fmt_str.format(
                    book_content_unit.lang_code,
                    name_content_pair.localized_word,
                    name_content_pair.localized_word,
                ),
            )
        )
        uses_section_ = model.HtmlContent("")

        # See comment above.
        if (
            include_uses_section
            and name_content_pair.localized_word in book_content_unit.uses
        ):
            uses_section_ = uses_section(
                book_content_unit.uses[name_content_pair.localized_word]
            )
            name_content_pair.content = model.HtmlContent(
                name_content_pair.content + uses_section_
            )
        yield name_content_pair.content


def assemble_content(
    document_request_key: str,
    document_request: model.DocumentRequest,
    book_content_units: Iterable[model.BookContent],
) -> str:
    """
    Assemble the content from all requested resources according to the
    assembly_strategy requested and write out to an HTML file
    for subsequent use.
    """
    # Get the assembly strategy function appropriate given the users
    # choice of document_request.assembly_strategy_kind
    assembly_strategy = assembly_strategies.assembly_strategy_factory(
        document_request.assembly_strategy_kind
    )
    t0 = time.time()
    # Now, actually do the assembly given the additional
    # information of the document_request.assembly_layout_kind and
    # return it as a string.
    content = "".join(
        assembly_strategy(book_content_units, document_request.assembly_layout_kind)
    )
    t1 = time.time()
    logger.debug("Time for interleaving document: %s", t1 - t0)

    t0 = time.time()
    tw_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, model.TWBook)
    ]
    # We need to see if the document request included any usfm because
    # if it did we'll generate not only the tw word defs but also the
    # links to them from the notes area that exists adjacent to the
    # scripture versees themselves.
    usfm_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, model.USFMBook)
    ]
    # Add the translation words definition section for each language requested.
    for tw_book_content_unit in toolz.unique(
        tw_book_content_units, key=lambda unit: unit.lang_code
    ):
        if usfm_book_content_units:
            # There is usfm content in this document request so we can
            # include the uses section in notes which links to individual word
            # definitions. The uses section will be incorporated by
            # assembly_strategies module if print layout is not chosen and
            # ignored otherwise.
            content = "{}{}".format(
                content, "".join(translation_words_section(tw_book_content_unit))
            )
        else:
            # There is no usfm content in this document request so
            # there is no need for the uses section.
            content = "{}{}".format(
                content,
                "".join(
                    translation_words_section(
                        tw_book_content_unit, include_uses_section=False
                    )
                ),
            )

    t1 = time.time()
    logger.debug("Time for add TW content to document: %s", t1 - t0)

    # Get the appropriate HTML template header content given the
    # document_request.assembly_layout_kind the user has chosen.
    header = document_html_header(document_request.assembly_layout_kind)
    # Finally compose the HTML document into one string that includes
    # the header template content.
    content = enclose_html_content(content, document_html_header=header)
    return content


def should_send_email(
    # NOTE: email_address comes in as pydantic.EmailStr and leaves
    # the pydantic class validator as a str.
    email_address: Optional[str],
    send_email: bool = settings.SEND_EMAIL,
) -> bool:
    """
    Return True if configuration is set to send email and the user
    has supplied an email address.
    """
    return send_email and email_address is not None


def send_email_with_attachment(
    # NOTE: email_address comes in as pydantic.EmailStr and leaves
    # the pydantic class validator as a str.
    email_address: Optional[str],
    attachments: list[model.Attachment],
    document_request_key: str,
    content_disposition: str = "attachment",
    from_email_address: str = settings.FROM_EMAIL_ADDRESS,
    smtp_password: str = settings.SMTP_PASSWORD,
    email_send_subject: str = settings.EMAIL_SEND_SUBJECT,
    smtp_host: str = settings.SMTP_HOST,
    smtp_port: int = settings.SMTP_PORT,
    comma_space: str = COMMASPACE,
) -> None:
    """
    If environment configuration allows sending of
    email, then send an email to the document request
    recipient's email with the document attached.
    """
    if email_address:
        sender = from_email_address
        email_password = smtp_password
        recipients = [email_address]

        logger.debug("Email sender %s, recipients: %s", sender, recipients)

        # Create the enclosing (outer) message
        outer = MIMEMultipart()
        outer["Subject"] = email_send_subject
        outer["To"] = comma_space.join(recipients)
        outer["From"] = sender
        # outer.preamble = "You will not see this in a MIME-aware mail reader.\n"

        # List of attachments

        # Add the attachments to the message
        for attachment in attachments:
            try:
                with open(attachment.filepath, "rb") as fp:
                    msg = MIMEBase(attachment.mime_type[0], attachment.mime_type[1])
                    msg.set_payload(fp.read())
                encoders.encode_base64(msg)
                msg.add_header(
                    "Content-Disposition",
                    content_disposition,
                    filename=os.path.basename(attachment.filepath),
                )
                outer.attach(msg)
            except Exception:
                logger.exception(
                    "Unable to open one of the attachments. Caught exception: "
                )

        # Get the email body
        message_body = instantiated_template(
            "email",
            model.EmailPayload(
                document_request_key=document_request_key,
            ),
        )
        logger.debug("instantiated email template: %s", message_body)

        outer.attach(MIMEText(message_body, "plain"))

        composed = outer.as_string()

        # Send the email
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(sender, email_password)
                smtp.sendmail(sender, recipients, composed)
                smtp.close()
            logger.info("Email sent!")
        except Exception:
            logger.exception("Unable to send the email. Caught exception: ")


def convert_html_to_pdf(
    html_filepath: str,
    pdf_filepath: str,
    email_address: Optional[str],
    document_request_key: str,
    wkhtmltopdf_options: dict[str, Optional[str]] = settings.WKHTMLTOPDF_OPTIONS,
) -> None:
    """
    Generate PDF from HTML, copy it to output directory, possibly send to email_address as attachment.
    """
    assert os.path.exists(html_filepath)
    logger.info("Generating PDF %s...", pdf_filepath)

    t0 = time.time()
    pdfkit.from_file(
        html_filepath,
        pdf_filepath,
        options=wkhtmltopdf_options,
    )
    t1 = time.time()
    logger.debug("Time for converting HTML to PDF: %s", t1 - t0)
    copy_file_to_docker_output_dir(pdf_filepath)
    if should_send_email(email_address):
        attachments = [
            model.Attachment(filepath=pdf_filepath, mime_type=("application", "pdf"))
        ]
        send_email_with_attachment(
            email_address,
            attachments,
            document_request_key,
        )


def convert_html_to_epub(
    html_filepath: str,
    epub_filepath: str,
    email_address: Optional[str],
    document_request_key: str,
    pandoc_options: str = settings.PANDOC_OPTIONS,
) -> None:
    """Generate ePub from HTML, possibly send to email_address as attachment."""
    assert os.path.exists(html_filepath)
    pandoc_command = "pandoc {} {} -o {}".format(
        pandoc_options,
        html_filepath,
        epub_filepath,
    )
    logger.debug("Generate ePub command: %s", pandoc_command)
    subprocess.call(pandoc_command, shell=True)
    copy_file_to_docker_output_dir(epub_filepath)
    if should_send_email(email_address):
        attachments = [
            model.Attachment(
                filepath=epub_filepath, mime_type=("application", "epub+zip")
            )
        ]
        send_email_with_attachment(
            email_address,
            attachments,
            document_request_key,
        )


def convert_html_to_docx(
    html_filepath: str,
    docx_filepath: str,
    email_address: Optional[str],
    document_request_key: str,
    pandoc_options: str = settings.PANDOC_OPTIONS,
) -> None:
    """Generate Docx from HTML, possibly send to email_address as attachment."""
    assert os.path.exists(html_filepath)
    pandoc_command = "pandoc {} {} -o {}".format(
        pandoc_options,
        html_filepath,
        docx_filepath,
    )
    logger.debug("Generate Docx command: %s", pandoc_command)
    subprocess.call(pandoc_command, shell=True)
    copy_file_to_docker_output_dir(docx_filepath)
    if should_send_email(email_address):
        attachments = [
            model.Attachment(
                filepath=docx_filepath,
                mime_type=(
                    "application",
                    "vnd.openxmlformats-officedocument.wordprocessingml.document",
                ),
            )
        ]
        send_email_with_attachment(
            email_address,
            attachments,
            document_request_key,
        )


def html_filepath(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the HTML output file path."""
    return os.path.join(output_dir, "{}.html".format(document_request_key))


def pdf_filepath(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the PDF output file path."""
    return os.path.join(output_dir, "{}.pdf".format(document_request_key))


def epub_filepath(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the ePub output file path."""
    return os.path.join(output_dir, "{}.epub".format(document_request_key))


def docx_filepath(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the docx output file path."""
    return os.path.join(output_dir, "{}.docx".format(document_request_key))


def cover_filepath(
    document_request_key: str, output_dir: str = settings.output_dir()
) -> str:
    """Given document_request_key, return the HTML cover output file path."""
    return os.path.join(output_dir, "{}_cover.html".format(document_request_key))


def select_assembly_layout_kind(
    document_request: model.DocumentRequest,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    book_language_order: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER,
    print_layout: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
    # NOTE Could also have default value for non_print_layout_for_multiple_usfm of
    non_print_layout_for_multiple_usfm: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
    default_layout: model.AssemblyLayoutEnum = model.AssemblyLayoutEnum.ONE_COLUMN,
) -> model.AssemblyLayoutEnum:
    """
    Make an intelligent choice of what layout to use given the
    DocumentRequest instance the user has requested. Why? Because we
    don't want to bother the user with having to choose a layout which
    would require them to understand what layouts could work well for
    their particular document request. Instead, we make the choice for
    them.
    """
    if not document_request.layout_for_print:
        document_request.layout_for_print = False
    if document_request.layout_for_print:
        return print_layout

    # Partition ulb resource requests by language.
    language_groups = toolz.itertoolz.groupby(
        lambda r: r.lang_code,
        filter(
            lambda r: r.resource_type in usfm_resource_types,
            document_request.resource_requests,
        ),
    )
    # Get a list of the sorted set of books for each language for later
    # comparison.
    sorted_book_set_for_each_language = [
        sorted({item.resource_code for item in value})
        for key, value in language_groups.items()
    ]

    # Get the unique number of languages
    number_of_usfm_languages = len(
        set(
            [
                resource_request.lang_code
                for resource_request in document_request.resource_requests
                if resource_request.resource_type in usfm_resource_types
            ]
        )
    )

    if (
        document_request.assembly_strategy_kind == book_language_order
        # Because book content for different languages will be side by side for
        # the scripture left scripture right layout, we make sure there are a non-zero
        # even number of languages so that we can display them left and right in
        # pairs.
        and number_of_usfm_languages > 1
        and number_utils.is_even(number_of_usfm_languages)
        # Each language must have the same set of books in order to
        # use the scripture left scripture right layout strategy. As an example,
        # you wouldn't want to allow the sl-sr layout if the document request
        # asked for swahili ulb for lamentations and spanish ulb for nahum -
        # the set of books in each language are not the same and so do not make
        # sense to be displayed side by side.
        and more_itertools.all_equal(sorted_book_set_for_each_language)
    ):
        return non_print_layout_for_multiple_usfm

    return default_layout


def write_html_content_to_file(
    content: str,
    output_filename: str,
) -> None:
    """
    Write HTML content to file.
    """
    logger.debug("About to write HTML to %s", output_filename)
    # Write the HTML file to disk.
    file_utils.write_file(
        output_filename,
        content,
    )
    copy_file_to_docker_output_dir(output_filename)


def copy_file_to_docker_output_dir(
    filepath: str,
    docker_container_document_output_dir: str = settings.DOCKER_CONTAINER_DOCUMENT_OUTPUT_DIR,
    in_container: bool = settings.IN_CONTAINER,
) -> None:
    """
    Copy file to docker_container_document_output_dir.
    """
    assert os.path.exists(filepath)
    logger.debug("IN_CONTAINER: {}".format(in_container))
    if in_container:
        logger.info("About to cp file to Docker volume")
        shutil.copy(filepath, docker_container_document_output_dir)


@worker.app.task
def main(document_request_json: Json[Any]) -> Json[Any]:
    """
    This is the main entry point for this module.
    """
    # If an assembly_layout_kind has been chosen in the document request,
    # then we know that the request originated from a unit test. The UI does
    # not provide a way to choose an arbitrary layout, but unit tests can
    # specify a layout arbitrarily. We must handle both situations.
    document_request = model.DocumentRequest.parse_raw(document_request_json)
    logger.debug(
        "document_request: %s",
        document_request,
    )
    if not document_request.assembly_layout_kind:
        document_request.assembly_layout_kind = select_assembly_layout_kind(
            document_request
        )
        logger.debug(
            "updated document_request: %s",
            document_request,
        )
    # Generate the document request key that identifies this and
    # identical document requests.
    document_request_key_ = document_request_key(
        document_request.resource_requests,
        document_request.assembly_strategy_kind,
        document_request.assembly_layout_kind,
    )
    html_filepath_ = html_filepath(document_request_key_)
    pdf_filepath_ = pdf_filepath(document_request_key_)
    epub_filepath_ = epub_filepath(document_request_key_)
    docx_filepath_ = docx_filepath(document_request_key_)

    if file_utils.asset_file_needs_update(html_filepath_):
        current_task.update_state(state="Locate assets")
        # HTML didn't exist in cache so go ahead and start by getting the
        # resource lookup DTOs for each resource request in the document
        # request.
        resource_lookup_dtos = [
            resource_lookup.resource_lookup_dto(
                resource_request.lang_code,
                resource_request.resource_type,
                resource_request.resource_code,
            )
            for resource_request in document_request.resource_requests
        ]

        # Determine which resources were actually found and which were
        # not.
        _, found_resource_lookup_dtos_iter = partition(
            lambda resource_lookup_dto: resource_lookup_dto.url is not None,
            resource_lookup_dtos,
        )

        found_resource_lookup_dtos = list(found_resource_lookup_dtos_iter)

        current_task.update_state(state="Provision asset files")
        t0 = time.time()
        resource_dirs = [
            resource_lookup.provision_asset_files(dto)
            for dto in found_resource_lookup_dtos
        ]
        t1 = time.time()
        logger.debug(
            "Time to provision asset files (acquire and write to disk): %s", t1 - t0
        )

        current_task.update_state(state="Parse asset files")
        # Initialize found resources from their provisioned assets.
        t0 = time.time()
        book_content_units = resource_book_content_units(
            found_resource_lookup_dtos,
            resource_dirs,
            document_request.resource_requests,
            document_request.layout_for_print,
        )
        t1 = time.time()
        logger.debug("Time to parse resource content: %s", t1 - t0)

        current_task.update_state(state="Assembling content")
        content = assemble_content(
            document_request_key_, document_request, book_content_units
        )
        write_html_content_to_file(
            content,
            html_filepath_,
        )

    # Immediately return pre-built PDF if the document has previously been
    # generated and is fresh enough. In that case, front run all requests to
    # the cloud including the more low level resource asset caching
    # mechanism for comparatively immediate return of PDF.
    if document_request.generate_pdf and file_utils.asset_file_needs_update(
        pdf_filepath_
    ):
        current_task.update_state(state="Converting to PDF format")
        convert_html_to_pdf(
            html_filepath_,
            pdf_filepath_,
            document_request.email_address,
            document_request_key_,
        )

    if document_request.generate_epub and file_utils.asset_file_needs_update(
        epub_filepath_
    ):
        current_task.update_state(state="Converting to ePub format")
        convert_html_to_epub(
            html_filepath_,
            epub_filepath_,
            document_request.email_address,
            document_request_key_,
        )

    if document_request.generate_docx and file_utils.asset_file_needs_update(
        docx_filepath_
    ):
        current_task.update_state(state="Converting to Docx format")
        convert_html_to_docx(
            html_filepath_,
            docx_filepath_,
            document_request.email_address,
            document_request_key_,
        )

    return document_request_key_
