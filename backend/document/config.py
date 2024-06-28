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

    SOURCE_DATA_JSON_FILENAME: str = "resources.json"
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
    # TODO
    TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{}-ch-{}-v-{})"

    USFM_RESOURCE_TYPES: Sequence[str] = [
        "ayt",
        "cuv",
        "f10",
        "nav",
        "reg",
        "udb",  # 2023-06-20 Content team doesn't want this used.
        # "udb-wa", # 2022-05-12 - Content team doesn't want this used.
        "ugnt",
        "uhb",  # parser blows on: AttributeError: 'SingleHTMLRenderer' object has no attribute 'renderCAS'
        "ulb",
        "usfm",
    ]
    EN_USFM_RESOURCE_TYPES: Sequence[str] = ["ulb-wa"]
    ALL_USFM_RESOURCE_TYPES: Sequence[str] = [
        *USFM_RESOURCE_TYPES,
        *EN_USFM_RESOURCE_TYPES,
    ]
    TN_RESOURCE_TYPE: str = "tn"
    EN_TN_CONDENSED_RESOURCE_TYPE: str = "tn-condensed"
    TQ_RESOURCE_TYPE: str = "tq"
    TW_RESOURCE_TYPE: str = "tw"
    BC_RESOURCE_TYPE: str = "bc"
    # List of language codes for which there is a content issue
    # such that a complete document request cannot
    # be formed.
    # Now that we use graphql, likely some of these can be added back
    LANG_CODE_FILTER_LIST: Sequence[str] = [
        # "aez",  # Has no chapter markers
        # "acq",
        # "gaj-x-ymnk",
        # "fa",
        # "hr",
        # "hu",
        # # "id",  # Was on this list because of licensing issues: it cannot be shown on BIEL
        # "kbt",
        # "kip",
        # "lus",
        # "mor",
        # "mve",
        # "pmy",  # Currently doesn't provide USFM, but might soon
        # "sr-Latn",
        # "tig",
        # "tem",
    ]
    # NOTE This is only used to see if a lang_code is in the collection
    # otherwise it is a heart language. Eventually the graphql data api may
    # provide gateway/heart boolean value.
    GATEWAY_LANGUAGES: Sequence[str] = [
        "am",
        "arb",
        "as",
        "bn",
        "pt-br",
        "my",
        "ceb",
        "zh",
        "en",
        "fr",
        "gu",
        "ha",
        "hi",
        "ilo",
        "id",
        "kn",
        "km",
        "lo",
        "es-419",
        "plt",
        "ml",
        "mr",
        "ne",
        "or",
        "pmy",  # Not returned by data API
        "fa",  # Not returned by data API
        "pa",
        "ru",
        "sw",
        "tl",
        "ta",
        "te",
        "th",
        "tpi",
        "ur",  # Not returned by data API
        "ur-deva",
        "vi",
    ]

    # fmt: off
    BC_ARTICLE_URL_FMT_STR: str = "https://content.bibletranslationtools.org/WycliffeAssociates/en_bc/src/branch/master/{}"
    # fmt: on

    OXML_LANGUAGE_LIST: list[str] = [
        "ar-SA",
        "bg-BG",
        "zh-CN",
        "zh-TW",
        "hr-HR",
        "cs-CZ",
        "da-DK",
        "nl-NL",
        "en-US",
        "et-EE",
        "fi-FI",
        "fr-FR",
        "de-DE",
        "el-GR",
        "he-IL",
        "hi-IN",
        "hu-HU",
        "id-ID",
        "it-IT",
        "ja-JP",
        "kk-KZ",
        "ko-KR",
        "lv-LV",
        "lt-LT",
        "ms-MY",
        "nb-NO",
        "pl-PL",
        "pt-BR",
        "pt-PT",
        "ro-RO",
        "ru-RU",
        "sr-latn-RS",
        "sk-SK",
        "sl-SI",
        "es-ES",
        "sv-SE",
        "th-TH",
        "tr-TR",
        "uk-UA",
        "vi-VN",
    ]
    OXML_LANGUAGE_LIST_LOWERCASE: list[str] = [
        language.lower() for language in OXML_LANGUAGE_LIST
    ]
    OXML_LANGUAGE_LIST_LOWERCASE_SPLIT: list[str] = [
        language for language in OXML_LANGUAGE_LIST_LOWERCASE if "-" in language
    ]

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

    # Return the file names, excluding suffix, of files that do not
    # contain content but which may be in the same directory or
    # subdirectories of a resource's acquired files.

    # -    ENGLISH_GIT_REPO_MAP: Mapping[str, str] = {
    # -        "ulb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_ulb",
    # -        "udb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_udb",
    # -        "tn-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn",
    # -        "tn-condensed": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn_condensed",
    # -        "tw-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tw",
    # -        "tq-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tq",
    # -        "bc-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_bc",
    # -    }
    # -    ID_GIT_REPO_MAP: Mapping[str, str] = {
    # -        "ayt": "https://content.bibletranslationtools.org/WA-Catalog/id_ayt",
    # -        "tn": "https://content.bibletranslationtools.org/WA-Catalog/id_tn",
    # -        "tq": "https://content.bibletranslationtools.org/WA-Catalog/id_tq",
    # -        "tw": "https://content.bibletranslationtools.org/WA-Catalog/id_tw",
    # -    }
    # -
    # -    ENGLISH_RESOURCE_TYPE_MAP: Mapping[str, str] = {
    # -        "ulb-wa": "Unlocked Literal Bible (ULB)",
    # -        # "udb-wa": "Unlocked Dynamic Bible (UDB)",
    # -        "tn-wa": "ULB Translation Notes",
    # -        "tn-condensed": "ULB Condensed Translation Notes",
    # -        "tq-wa": "ULB Translation Questions",
    # -        "tw-wa": "ULB Translation Words",
    # -        "bc-wa": "Bible Commentary",
    # -    }
    TN_CONDENSED_GIT_REPO_URL: str = (
        "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn_condensed"
    )

    # -    ID_LANGUAGE_NAME: str = "Bahasa Indonesian"
    # -    ID_RESOURCE_TYPE_MAP: Mapping[str, str] = {
    # -        "ayt": "Bahasa Indonesian Bible (ayt)",
    # -        "tn": "Translation Helps (tn)",
    # -        "tq": "Translation Questions (tq)",
    # -        "tw": "Translation Words (tw)",
    # -    }
    ID_AYT_GIT_REPO_URL: str = (
        "https://content.bibletranslationtools.org/WA-Catalog/id_ayt"
    )

    TEMPLATE_PATHS_MAP: Mapping[str, str] = {
        "book_intro": "backend/templates/tn/book_intro_template.md",
        "header_enclosing": "backend/templates/html/header_enclosing.html",
        "header_enclosing_landscape": "backend/templates/html/header_enclosing_landscape.html",  # used by dft project
        "header_no_css_enclosing": "backend/templates/html/header_no_css_enclosing.html",
        "header_compact_enclosing": "backend/templates/html/header_compact_enclosing.html",
        "footer_enclosing": "backend/templates/html/footer_enclosing.html",
        "cover": "backend/templates/html/cover.html",
        "email-html": "backend/templates/html/email.html",
        "email": "backend/templates/text/email.txt",
    }

    DOCX_TEMPLATE_PATH: str = "template.docx"
    DOCX_COMPACT_TEMPLATE_PATH: str = "template_compact.docx"

    # Indicate if generated documents should be cached.
    ASSET_CACHING_ENABLED: bool = True
    # Caching window of time in which asset
    # files on disk are considered fresh rather than re-acquiring (in
    # the case of resource asset files) or re-generating them (in the
    # case of the final PDF). In hours.
    ASSET_CACHING_PERIOD: int

    # It doesn't yet make sense to offer the (high level)
    # assembly strategy _and_ the assembly sub-strategy to the end user
    # as a document request parameter so we'll just choose an arbitrary
    # sub-strategy here. This means that we can write code for multiple
    # sub-strategies and choose one to put in play at a time here.

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
