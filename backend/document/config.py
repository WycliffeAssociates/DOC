"""This module provides configuration values used by the application."""
import logging
from collections.abc import Mapping, Sequence
from logging import config as lc
from typing import final

import yaml
from pydantic import EmailStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


@final
class Settings(BaseSettings):
    """
    BaseSettings subclasses like this one allow values of constants to
    be overridden by environment variables like those defined in env
    files, e.g., ../../.env or by system level environment variables
    (which have higher priority).
    """

    # GITHUB_API_TOKEN: str = "FOO"  # This might be used in a later version
    DATA_API_URL: HttpUrl

    LTR_DIRECTION_HTML: str = "<div style='direction: ltr;'>"
    RTL_DIRECTION_HTML: str = "<div style='direction: rtl;'>"

    END_OF_CHAPTER_HTML: str = '<div class="end-of-chapter"></div>'
    RESOURCE_TYPE_NAME_FMT_STR: str = "<h2>{}</h2>"
    TN_VERSE_NOTES_ENCLOSING_DIV_FMT_STR: str = "<div style='column-count: 2;'>{}</div>"
    TQ_HEADING_AND_QUESTIONS_FMT_STR: str = (
        "<h3>{}</h3>\n<div style='column-count: 2;'>{}</div>"
    )
    HTML_ROW_BEGIN: str = "<div class='row'>"
    HTML_ROW_END: str = "</div>"
    HTML_COLUMN_BEGIN: str = "<div class='column'>"
    HTML_COLUMN_END: str = "</div>"
    HTML_COLUMN_LEFT_BEGIN: str = "<div class='column-left'>"
    HTML_COLUMN_RIGHT_BEGIN: str = "<div class='column-right'>"
    BOOK_NAME_FMT_STR: str = "<h2 style='text-align: center;'>{}</h2>"
    CHAPTER_HEADER_FMT_STR: str = '<h2 class="chapter">Chapter {}</h2>'
    UNORDERED_LIST_BEGIN_STR: str = "<ul>"
    UNORDERED_LIST_END_STR: str = "</ul>"
    OPENING_H3_FMT_STR: str = "<h3>{}"
    OPENING_H3_WITH_ID_FMT_STR: str = '<h3 id="{}-{}">{}'
    TRANSLATION_WORD_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{})"
    TRANSLATION_WORD_PREFIX_ANCHOR_LINK_FMT_STR: str = "({}: [{}](#{}-{}))"
    TRANSLATION_WORD_PREFIX_FMT_STR: str = "({}: {})"
    # TODO This needs to be changed to the .NET USFM renderer's marker
    # pattern. This is the USFM-Tools singlePageRenderer's expected output,
    # i.e., the output from the previous renderer.
    TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{}-ch-{}-v-{})"

    USFM_RESOURCE_TYPES: Sequence[str] = [
        "avd",
        "ayt",
        "blv",
        "cuv",
        "f10",
        "nav",
        "reg",
        # "udb",  # 2023-06-20 Content team doesn't want this used. This should probably be filtered at the graphql level though.
        "ugnt",
        "uhb",
        "ulb",
        "usfm",
    ]
    TN_RESOURCE_TYPE: str = "tn"
    EN_TN_CONDENSED_RESOURCE_TYPE: str = "tn-condensed"
    TQ_RESOURCE_TYPE: str = "tq"
    TW_RESOURCE_TYPE: str = "tw"
    BC_RESOURCE_TYPE: str = "bc"
    NON_USFM_RESOURCE_TYPES: Sequence[str] = [
        TN_RESOURCE_TYPE,
        EN_TN_CONDENSED_RESOURCE_TYPE,
        TQ_RESOURCE_TYPE,
        TW_RESOURCE_TYPE,
        BC_RESOURCE_TYPE,
    ]
    # NOTE This is only used to see if a lang_code is in the collection
    # otherwise it is a heart language. Eventually the graphql data api may
    # provide gateway/heart boolean value.
    GATEWAY_LANGUAGES: Sequence[str] = [
        "abs",
        "aju",
        "am",
        "apd",
        "ar",
        "ar-x-dcv",
        "ary",
        "arz",
        "as",
        "ase",
        "bem",
        "bg",
        "bgw",
        "bi",
        "bn",
        "ceb",
        "cmn",
        "cmn-x-omc",
        "csl",
        "dz",
        "en",
        "es",
        "es-419",
        "fa",
        "fil",
        "fr",
        "grt",
        "gu",
        "gug",
        "ha",
        "hbs",
        "hca",
        "he",
        "hi",
        "hne",
        "hu",
        "id",
        "id-x-dcv",
        "idb",
        "ilo",
        "ins",
        "ja",
        "jv",
        "kas",
        "km",
        "kn",
        "lbj",
        "ln",
        "lo",
        "mai",
        "mg",
        "ml",
        "mn",
        "mni",
        "mnk",
        "mr",
        "ms",
        "my",
        "ne",
        "nl",
        "npi",
        "or",
        "pa",
        "pbt",
        "pes",
        "pis",
        "plt",
        "pmy",
        "pnb",
        "prs",
        "ps",
        "psr",
        "pt",
        "pt-br",
        "raj",
        "rsl",
        "ru",
        "rwr",
        "sn",
        "sw",
        "swc",
        "swh",
        "ta",
        "te",
        "th",
        "ti",
        "tl",
        "tn",
        "tpi",
        "tr",
        "tsg",
        "ug",
        "ur",
        "vi",
        "zh",
        "zlm",
    ]

    # fmt: off
    BC_ARTICLE_URL_FMT_STR: str = "https://content.bibletranslationtools.org/WycliffeAssociates/en_bc/src/branch/master/{}"
    # fmt: on

    def logger(self, name: str) -> logging.Logger:
        """
        Return a Logger for scope named by name, e.g., module, that can be
        used for logging.
        """
        with open(self.LOGGING_CONFIG_FILE_PATH, "r") as fin:
            logging_config = yaml.safe_load(fin.read())
            lc.dictConfig(logging_config)
        return logging.getLogger(name)

    def api_test_url(self) -> str:
        """Non-secure local URL for running the Fastapi server for testing."""
        return "{}:{}".format(self.API_TEST_BASE_URL, self.API_LOCAL_PORT)

    API_TEST_BASE_URL: str = "http://localhost"

    API_LOCAL_PORT: int

    USE_GIT_CLI: bool = False

    LOGGING_CONFIG_FILE_PATH: str = "backend/logging_config.yaml"

    # Location where resource assets will be cloned.
    RESOURCE_ASSETS_DIR: str = "working/temp"

    # Location where generated PDFs are written.
    DOCUMENT_OUTPUT_DIR: str = "working/output"

    # Location where generated documents are copied to after being written.
    DOCUMENT_SERVE_DIR: str = "document_output"

    BACKEND_CORS_ORIGINS: list[str]

    DOCX_TEMPLATE_PATH: str = "template.docx"
    DOCX_COMPACT_TEMPLATE_PATH: str = "template_compact.docx"

    # Indicate if generated documents should be cached.
    ASSET_CACHING_ENABLED: bool = True
    # Caching window of time in which asset
    # files on disk are considered fresh rather than re-acquiring (in
    # the case of resource asset files) or re-generating them (in the
    # case of the final PDF). In hours.
    ASSET_CACHING_PERIOD: int

    # Return a list of the Markdown section titles that our
    # Python-Markdown remove_section_processor extension should remove.
    MARKDOWN_SECTIONS_TO_REMOVE: list[str] = [
        "Examples from the Bible stories",
        "Links",
        "Picture of",
        "Pictures",
    ]

    EMAIL_SEND_SUBJECT: str
    TO_EMAIL_ADDRESS: EmailStr

    # Provided by system env vars (fake values provided so github action can run):
    FROM_EMAIL_ADDRESS: EmailStr = "foo@example.com"
    SMTP_HOST: str = "https://example.com"
    SMTP_PORT: int = 111
    SMTP_PASSWORD: str = "fakepass"
    SEND_EMAIL: bool = False

    # Used by gunicorn
    PORT: int
    # Used by docker
    IMAGE_TAG: str

    # User agent value required by domain host to allow serving
    # files. Other values could possibly also work.
    USER_AGENT: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"

    # Used in assembly_strategy_utils module when zero-filling various strings
    NUM_ZEROS: int = 3

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


# mypy with pydantic v2 doesn't understand that defaults will be
# picked up from .env file as they had been in v1, thus the type
# ignore directive
settings = Settings()  # type: ignore
# Could also use:
# settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
