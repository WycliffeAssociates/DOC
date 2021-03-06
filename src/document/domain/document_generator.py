"""
Entrypoint for backend. Here incoming document requests are processed
and eventually a final document produced.
"""
import base64
import datetime
import logging  # For logdecorator
import os
import smtplib
import subprocess
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Generator, Iterable, Optional, Union

import icontract
import pdfkit
from document.config import settings
from document.domain import assembly_strategies, bible_books, model
from document.domain.resource import (
    Resource,
    resource_factory,
)
from document.utils import file_utils
from logdecorator import log_on_start
from more_itertools import partition
from pydantic import EmailStr
from usfm_tools.support import exceptions

logger = settings.logger(__name__)

COMMASPACE = ", "
HYPHEN = "-"
UNDERSCORE = "_"


# NOTE It is possible to have not found any resources due to a
# malformed document request, e.g., asking for a resource that
# doesn't exist. Thus we can't assert that self._found_resources
# has at least one resource.
# @icontract.require(lambda found_resources: found_resources)
def _update_found_resources_with_content(
    found_resources: list[Resource],
) -> list[Resource]:
    """
    Initialize the resources from their found assets and
    generate their content for later typesetting. If any of the
    found resources could not be loaded then return a list of them
    for later reporting.
    """
    unloaded_resources: list[Resource] = []
    for resource in found_resources:
        # usfm_tools parser can throw a MalformedUsfmError parse error if the
        # USFM for the resource is malformed (from the perspective of the
        # parser). If that happens keep track of said USFM resource for
        # reporting on the cover page of the generated PDF and log the issue,
        # but continue handling other resources in the document request.
        try:
            resource.update_resource_with_asset_content()
        except exceptions.MalformedUsfmError:
            unloaded_resources.append(resource)
            logger.debug(
                "Exception while reading USFM file for %s, skipping this \
                resource and continuing with remaining resource requests, \
                if any.",
                resource,
            )
            logger.exception("Caught exception:")
    return unloaded_resources


def _document_request_key(
    resource_requests: list[model.ResourceRequest], assembly_strategy_kind: str
) -> str:
    """
    Create and return the document_request_key. The
    document_request_key uniquely identifies a document request.
    """
    document_request_key = ""
    for resource_request in resource_requests:
        document_request_key += (
            HYPHEN.join(
                [
                    resource_request.lang_code,
                    resource_request.resource_type,
                    resource_request.resource_code,
                ]
            )
            + UNDERSCORE
        )
    return "{}_{}".format(document_request_key[:-1], assembly_strategy_kind)


def _resources_from(
    resource_requests: list[model.ResourceRequest],
) -> Generator[Resource, None, None]:
    """
    Given a DocumentRequest, return a list of Resource
    instances, one for each ResourceRequest in the
    DocumentRequest.
    """
    for resource_request in resource_requests:
        yield resource_factory(
            settings.working_dir(),
            settings.output_dir(),
            resource_request,
            resource_requests,
        )


def _enclose_html_content(content: str) -> str:
    """
    Write the enclosing HTML and body elements around the HTML
    body content for the document.
    """
    return "{}{}{}".format(
        settings.document_html_header(),
        content,
        settings.document_html_footer(),
    )


def _assemble_content(
    document_request_key: str,
    document_request: model.DocumentRequest,
    found_resources: Iterable[Resource],
) -> None:
    """
    Concatenate/interleave the content from all requested resources
    according to the assembly_strategy requested and write out to a single
    HTML file excluding a wrapping HTML and BODY element.
    Precondition: each resource has already generated HTML of its
    body content (sans enclosing HTML and body elements) and
    stored it in its _content instance variable.
    """
    assembly_strategy = assembly_strategies.assembly_strategy_factory(
        document_request.assembly_strategy_kind
    )
    content = assembly_strategy(found_resources)
    content = _enclose_html_content(content)
    html_file_path = "{}.html".format(
        os.path.join(settings.output_dir(), document_request_key)
    )
    logger.debug("About to write HTML to %s", html_file_path)
    file_utils.write_file(
        html_file_path,
        content,
    )


def _should_send_email(email_address: Optional[EmailStr]) -> bool:
    """
    Return True if configuration is set to send email and the user
    has supplied an email address.
    """
    return settings.SEND_EMAIL and email_address is not None


@log_on_start(logging.INFO, "Calling _send_email_with_pdf_attachment", logger=logger)
@icontract.require(
    lambda output_filename, document_request_key: os.path.exists(output_filename)
    and document_request_key
)
def _send_email_with_pdf_attachment(
    email_address: EmailStr, output_filename: str, document_request_key: str
) -> None:
    """
    If PDF exists, and environment configuration allows sending of
    email, then send an email to the document request
    recipient's email with the PDF attached.
    """
    if email_address:
        sender = settings.FROM_EMAIL_ADDRESS
        email_password = settings.SMTP_PASSWORD
        recipients = [email_address]

        logger.debug("Email sender %s, recipients: %s", sender, recipients)

        # Create the enclosing (outer) message
        outer = MIMEMultipart()
        outer["Subject"] = settings.EMAIL_SEND_SUBJECT
        outer["To"] = COMMASPACE.join(recipients)
        outer["From"] = sender
        # outer.preamble = "You will not see this in a MIME-aware mail reader.\n"

        # List of attachments
        attachments = [output_filename]

        # Add the attachments to the message
        for file in attachments:
            try:
                with open(file, "rb") as fp:
                    msg = MIMEBase("application", "octet-stream")
                    msg.set_payload(fp.read())
                encoders.encode_base64(msg)
                msg.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(file),
                )
                outer.attach(msg)
            except Exception:
                logger.exception(
                    "Unable to open one of the attachments. Caught exception: "
                )

        # Get the email body
        message_body = settings.instantiated_template(
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
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(sender, email_password)
                smtp.sendmail(sender, recipients, composed)
                smtp.close()
            logger.info("Email sent!")
        except Exception:
            logger.exception("Unable to send the email. Caught exception: ")


def _convert_html_to_pdf(
    document_request_key: str,
    found_resources: Iterable[Resource],
    unfound_resources: Iterable[Resource],
    unloaded_resources: list[Resource],
) -> None:
    """Generate PDF from HTML contained in self.content."""
    now = datetime.datetime.now()
    revision_date = "Generated on: {}-{}-{}".format(now.year, now.month, now.day)
    title = "{}".format(
        COMMASPACE.join(
            sorted(
                {
                    "{}: {}".format(
                        resource.lang_name,
                        bible_books.BOOK_NAMES[resource.resource_code],
                    )
                    for resource in found_resources
                }
            )
        )
    )
    unfound = "{}".format(
        COMMASPACE.join(
            sorted(
                {
                    "{}-{}-{}".format(
                        resource.lang_code,
                        resource.resource_type,
                        resource.resource_code,
                    )
                    for resource in unfound_resources
                }
            )
        )
    )
    unloaded = "{}".format(
        COMMASPACE.join(
            sorted(
                {
                    "{}-{}-{}".format(
                        resource.lang_code,
                        resource.resource_type,
                        resource.resource_code,
                    )
                    for resource in unloaded_resources
                }
            )
        )
    )
    if unloaded:
        logger.debug("Resources that could not be loaded: %s", unloaded)
    html_file_path = "{}.html".format(
        os.path.join(settings.output_dir(), document_request_key)
    )
    assert os.path.exists(html_file_path)
    output_pdf_file_path = _pdf_output_filename(document_request_key)
    with open(settings.LOGO_IMAGE_PATH, "rb") as fin:
        base64_encoded_logo_image = base64.b64encode(fin.read())
        images: dict[str, Union[str, bytes]] = {
            "logo": base64_encoded_logo_image,
        }
    # Use Jinja2 to instantiate the cover page.
    cover = settings.instantiated_template(
        "cover",
        model.CoverPayload(
            title=title,
            unfound=unfound,
            unloaded=unloaded,
            revision_date=revision_date,
            images=images,
        ),
    )
    cover_filepath = os.path.join(settings.working_dir(), "cover.html")
    with open(cover_filepath, "w") as fout:
        fout.write(cover)
    pdfkit.from_file(
        html_file_path,
        output_pdf_file_path,
        options=settings.WKHTMLTOPDF_OPTIONS,
        cover=cover_filepath,
    )
    assert os.path.exists(output_pdf_file_path)
    copy_command = "cp {}/{}.pdf {}".format(
        settings.output_dir(),
        document_request_key,
        settings.DOCKER_CONTAINER_PDF_OUTPUT_DIR,
    )
    logger.debug("IN_CONTAINER: {}".format(settings.IN_CONTAINER))
    if settings.IN_CONTAINER:
        logger.info("About to cp PDF to Docker volume map on host")
        logger.debug("Copy PDF command: %s", copy_command)
        subprocess.call(copy_command, shell=True)


def _generate_pdf(
    output_filename: str,
    document_request_key: str,
    document_request: model.DocumentRequest,
    found_resources: Iterable[Resource],
    unfound_resources: Iterable[Resource],
    unloaded_resources: list[Resource],
) -> None:
    """
    If the PDF doesn't yet exist, go ahead and generate it
    using the content for each resource.
    """
    if not os.path.isfile(output_filename):
        _assemble_content(document_request_key, document_request, found_resources)
        logger.info("Generating PDF %s...", output_filename)
        _convert_html_to_pdf(
            document_request_key, found_resources, unfound_resources, unloaded_resources
        )


@icontract.require(lambda document_request_key: document_request_key)
def _pdf_output_filename(document_request_key: str) -> str:
    """Given document_request_key, return the PDF output file path."""
    return os.path.join(settings.output_dir(), "{}.pdf".format(document_request_key))


@icontract.require(
    lambda document_request: document_request
    and document_request.resource_requests
    and [
        resource_request
        for resource_request in document_request.resource_requests
        if resource_request.lang_code
        and resource_request.resource_type in settings.resource_type_lookup_map().keys()
        and resource_request.resource_code in bible_books.BOOK_NAMES.keys()
    ]
)
@log_on_start(logging.DEBUG, "document_request: {document_request}", logger=logger)
def run(document_request: model.DocumentRequest) -> tuple[str, str]:
    """
    This is the main entry point for this module and the
    backend system as a whole.
    """
    resources = _resources_from(document_request.resource_requests)
    document_request_key = _document_request_key(
        document_request.resource_requests, document_request.assembly_strategy_kind
    )
    output_filename = _pdf_output_filename(document_request_key)

    # Immediately return pre-built PDF if the document previously been
    # generated and is fresh enough. In that case, front run all requests to
    # the cloud including the more low level resource asset caching
    # mechanism for comparatively immediate return of PDF.
    if file_utils.asset_file_needs_update(output_filename):
        unfound_resources, found_resources = partition(
            lambda resource: resource.find_location(), resources
        )
        # Need to use items produced by these two generators again so
        # materialize them into a list.
        found_resources_list = list(found_resources)
        unfound_resources_list = list(unfound_resources)

        for resource in found_resources_list:
            resource.provision_asset_files()

        for resource in unfound_resources:
            logger.info("%s was not found", resource)

        unloaded_resources = _update_found_resources_with_content(found_resources_list)

        _generate_pdf(
            output_filename,
            document_request_key,
            document_request,
            found_resources_list,
            unfound_resources_list,
            unloaded_resources,
        )
    if _should_send_email(document_request.email_address):
        _send_email_with_pdf_attachment(
            document_request.email_address, output_filename, document_request_key
        )
    return document_request_key, output_filename
