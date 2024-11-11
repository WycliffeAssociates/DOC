"""This module provides configuration values used by the application."""
import logging
from logging import config as lc
from typing import Mapping, Sequence, final

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

    # This can be expanded to include any additional types (if
    # there are any) that we want to be available to users. These are all
    # that I found of relevance in the data API.
    RESOURCE_TYPE_CODES_AND_NAMES: Mapping[str, str] = {
        "ayt": "Bahasa Indonesian Bible",
        "bc": "Bible Commentary",
        "blv": "Portuguese Bíblia Livre",
        "cuv": "新标点和合本",
        "f10": "French Louis Segond 1910 Bible",
        "nav": "New Arabic Version (Ketab El Hayat)",
        "reg": "Bible",
        "tn": "Translation Notes",
        "tn-condensed": "Condensed Translation Notes",
        "tq": "Translation Questions",
        "tw": "Translation Words",
        # "udb": "Unlocked Dynamic Bible",  # Content team doesn't want udb used
        "ugnt": "unfoldingWord® Greek New Testament",
        "uhb": "unfoldingWord® Hebrew Bible",
        "ulb": "Unlocked Literal Bible",
    }
    SHOW_TN_BOOK_INTRO: bool = False
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

    CHECK_USFM: bool
    CHECK_ALL_BOOKS_FOR_LANGUAGE: bool

    # Resources known to have USFM defects found through automatic
    # randomized testing and subsequent manual investigation. Where possible
    # we handle these defects on the fly. As an aside: When we find one
    # defective USFM resource for a language then the language might have
    # others.
    RESOURCES_WITH_USFM_DEFECTS: Sequence[tuple[str, str, str]] = [
        ("aaz-x-amarasibarat", "reg", "2pe"),
        ("aec", "reg", "mat"),
        ("ahm", "reg", "php"),
        ("ahm", "reg", "php"),
        ("aoa", "reg", "col"),
        ("aoa", "reg", "luk"),
        ("ayn", "reg", "jud"),
        ("bds", "reg", "phm"),
        ("bem", "reg", "isa"),
        ("bem-x-kabenmushi", "reg", "zec"),
        ("bem-x-kabenmushi", "reg", "2sa"),
        ("bem-x-kabenmushi", "reg", "mat"),
        ("bem-x-kabenmushi", "reg", "isa"),
        ("bem-x-kabenmushi", "reg", "jer"),
        ("bem-x-kabenmushi", "reg", "sng"),
        ("bem-x-kabenmushi", "reg", "deu"),
        ("bem-x-kabenmushi", "reg", "1ki"),
        ("bem-x-kabenmushi", "reg", "1ch"),
        ("bem-x-kabenmushi", "reg", "ecc"),
        ("bem-x-kabenmushi", "reg", "2ki"),
        ("bji", "reg", "mat"),
        ("bji", "reg", "1co"),
        ("bji", "reg", "jud"),
        ("bji", "reg", "1co"),
        ("bji", "reg", "luk"),
        ("bji", "reg", "gal"),
        ("bji", "reg", "col"),
        ("bji", "reg", "2pe"),
        ("bji", "reg", "luk"),
        ("bji", "reg", "col"),
        ("bji", "reg", "php"),
        ("bji", "reg", "heb"),
        ("bji", "reg", "1jn"),
        ("bji", "reg", "col"),
        ("bjz", "reg", "eph"),
        ("blo", "reg", "rom"),
        ("blo", "reg", "act"),
        ("blo", "reg", "col"),
        ("blo", "reg", "php"),
        ("blo", "reg", "heb"),
        ("blo", "reg", "1jn"),
        ("blo", "reg", "col"),
        ("bne", "reg", "gal"),
        ("bof", "reg", "mat"),
        ("bou", "reg", "gen"),
        ("btd-x-boang", "reg", "mat"),
        ("btd-x-boang", "reg", "1ti"),
        ("btd-x-boang", "reg", "phm"),
        ("btm", "reg", "phm"),
        ("btm", "reg", "1th"),
        ("btm", "reg", "2co"),
        ("btm", "reg", "1pe"),
        ("bwc", "reg", "lev"),
        ("bwc", "reg", "php"),
        ("bwc", "reg", "tit"),
        ("bwc", "reg", "jhn"),
        ("byi", "reg", "gen"),
        ("byi", "reg", "php"),
        ("byi", "reg", "jon"),
        ("byi", "reg", "nam"),
        ("byi", "reg", "rut"),  # failed to fix
        ("byi", "reg", "1pe"),
        ("byi", "reg", "2co"),
        ("byi", "reg", "jud"),
        ("byn", "reg", "2sa"),
        ("byn", "reg", "nam"),
        ("byn", "reg", "2co"),
        ("byn", "reg", "jud"),
        ("byn", "reg", "dan"),
        ("byn", "reg", "hab"),
        ("byn", "reg", "hag"),
        ("byn", "reg", "mic"),
        ("byn", "reg", "1ti"),
        ("byn", "reg", "2ti"),
        ("byn", "reg", "2pe"),
        ("bzu", "reg", "mrk"),
        ("bzu", "reg", "2jn"),
        ("bzu", "reg", "tit"),  # failed to fix
        ("bzu", "reg", "2th"),
        ("bzu", "reg", "2jn"),
        ("bzu", "reg", "php"),
        ("bzu", "reg", "2th"),  # failed to fix
        ("cbt", "reg", "jos"),
        ("cbt", "reg", "jdg"),  # failed to fix
        ("cbt", "reg", "rut"),
        ("cbt", "reg", "est"),
        ("cbt", "reg", "ezr"),
        ("cbt", "reg", "est"),
        ("cbt", "reg", "ezr"),
        ("ccp", "reg", "mat"),
        ("ccp", "reg", "2pe"),
        ("ccp", "reg", "gal"),
        ("ceb", "ulb", "gen"),
        ("cot", "reg", "rut"),
        ("cot", "reg", "oba"),
        ("dne", "reg", "3jn"),
        ("ekp", "reg", "2co"),
        ("ema-x-emai", "reg", "act"),
        ("erk-x-epang", "reg", "php"),
        ("eyo", "reg", "2jn"),
        ("eyo", "reg", "php"),
        # ("gow", "reg", "3jn"),
        ("gux-x-gourmantche", "reg", "deu"),
        ("gux-x-gourmantche", "reg", "jon"),
        ("gux-x-gourmantche", "reg", "jos"),
        ("gwg", "reg", "php"),
        ("gwg", "reg", "3jn"),
        ("gwg", "reg", "2co"),
        ("gwg", "reg", "2jn"),
        ("gwg", "reg", "gal"),
        ("gwg", "reg", "rom"),
        ("hay-x-nyaihangiro", "reg", "1jn"),
        ("hay-x-nyaihangiro", "reg", "phm"),
        ("iba-x-desatempunak", "reg", "phm"),
        (
            "iba-x-ibanempran",
            "reg",
            "2co",
        ),  # Sometimes missing verse marker, just a number
        (
            "iba-x-ibanempran",
            "reg",
            "eph",
        ),  # Sometimes missing verse marker, just a number
        (
            "iba-x-ibanempran",
            "reg",
            "jud",
        ),  # Sometimes missing verse marker, just a number
        (
            "iba-x-ibanempran",
            "reg",
            "col",
        ),  # Sometimes missing verse marker, just a number
        ("ife-x-ana", "reg", "1th"),  # duplicated chapter markers
        ("jid", "reg", "mat"),  # I don't see the problem with this one, test mnaually
        ("jni", "reg", "luk"),  #  I don't see the problem with this one, test mnaually
        ("jni", "ulb", "luk"),
        ("kdx", "reg", "1pe"),
        # ("khz-x-aroma", "reg", "2ti"), # 2ti doesn't exist as a choice
        # ("khz-x-aroma", "ulb", "rom"), # rom doesn't exist as a choice
        ("kin-x-biofu", "reg", "rut"),
        ("kin-x-kinyabinza", "reg", "phm"),
        ("kiz", "reg", "heb"),
        ("kiz", "reg", "php"),
        ("kiz", "reg", "1th"),  # failed to fix
        ("kiz", "reg", "jhn"),
        ("kiz", "reg", "2jn"),
        ("kki", "reg", "mat"),
        ("kki", "reg", "3jn"),
        ("kki", "reg", "1pe"),  # repeated chapter markers
        ("kki", "reg", "php"),  # repeated chapter markers
        ("kki", "reg", "2ti"),
        ("kki", "reg", "1th"),
        ("kki", "reg", "jud"),
        ("kng-x-kilemfu", "reg", "phm"),
        ("kng-x-kilemfu", "reg", "3jn"),
        ("kng-x-kilemfu", "reg", "1jn"),
        ("kng-x-kilemfu", "reg", "jud"),  # failed to fix
        ("kng-x-kilemfu", "reg", "eph"),
        # ("knl-x-kebahaulak", "reg", "jud"),
        ("kod", "reg", "luk"),
        ("kod", "reg", "2ti"),
        ("kod", "reg", "heb"),
        ("kod", "reg", "col"),
        # ("kod", "reg", "jud"), # jude doesn't exist as a choice
        ("kod", "reg", "phm"),
        ("kqi", "reg", "2th"),
        ("kqi", "reg", "2ti"),
        ("kqi", "reg", "mrk"),
        ("kqi", "reg", "heb"),  # failed to fix
        ("kqi", "reg", "1pe"),
        ("kqi", "reg", "tit"),
        ("ksm", "reg", "rom"),
        ("ksm", "reg", "1pe"),
        ("ksm", "reg", "2ti"),
        ("ksm", "reg", "heb"),
        ("ksm", "reg", "col"),
        ("ksm", "reg", "2pe"),
        ("kyt", "reg", "2ti"),
        ("kyt", "reg", "eph"),
        ("lbx-x-capuracu", "reg", "mrk"),
        ("lch-ZM-luchazi", "reg", "gen"),
        ("ldo", "reg", "1co"),
        ("leb-x-bisa", "reg", "zep"),
        ("lio", "reg", "phm"),
        ("lks", "reg", "heb"),
        ("lky", "reg", "jas"),
        ("lky", "reg", "2th"),
        ("lbx-x-capuracu", "reg", "3jn"),
        ("lbx-x-capuracu", "reg", "eph"),
        ("lrl", "reg", "1ti"),
        ("mfq-x-mual", "reg", "1ki"),
        ("mgs", "reg", "php"),
        ("mgs", "reg", "2th"),
        ("mhi-x-burolo", "reg", "mat"),
        ("mhi-x-burolo", "reg", "2jn"),
        ("mhi-x-burolo", "reg", "2th"),
        ("mhi-x-burolo", "reg", "1pe"),
        ("mhi-x-burolo", "reg", "2th"),
        ("mhy-x-benualima", "reg", "mrk"),
        # ("mwe", "reg", "tit"),
        ("mxo", "reg", "mrk"),
        ("nak-x-bileki", "reg", "mat"),
        ("nak-x-bileki", "reg", "1ti"),
        ("nak-x-bileki", "reg", "eph"),
        ("nak-x-bileki", "reg", "2ti"),
        ("nak-x-bileki", "reg", "jas"),
        ("nak-x-bileki", "reg", "mrk"),
        ("ndc-x-chibangwe", "reg", "mrk"),
        ("ndc-x-chidanda", "reg", "mat"),
        ("ndc-x-chidanda", "reg", "luk"),
        ("ndc-x-chidanda", "reg", "gal"),
        ("nfd", "reg", "gal"),
        ("nfd", "reg", "2th"),
        ("nfd", "reg", "2ti"),
        ("nfd", "reg", "heb"),
        ("nhx", "reg", "jos"),
        ("nnb-x-kishula", "reg", "mrk"),
        ("not", "reg", "jos"),
        ("now", "reg", "mic"),
        ("nue", "reg", "php"),
        ("nya-x-nyanja", "reg", "jon"),
        ("nyj", "reg", "col"),
        ("nyj", "reg", "nam"),
        ("nyj", "reg", "hag"),
        # ("nyj-x-kitiri", "reg", "2th"),
        ("nyn-x-runyaruguru", "reg", "1co"),
        ("nyr", "reg", "mat"),
        ("nyr", "reg", "php"),
        ("nyr", "reg", "3jn"),
        ("nyr", "reg", "jud"),
        ("nyr", "reg", "jas"),
        ("nza-x-mbembnthal", "reg", "act"),
        ("nza-x-mbembnthal", "reg", "luk"),
        ("nza-x-mbembnthal", "reg", "jud"),
        ("okv-x-bokoro", "reg", "2co"),
        ("okv-x-bokoro", "reg", "1jn"),
        ("okv-x-bokoro", "reg", "php"),
        ("okv-x-bokoro", "reg", "jud"),
        ("okv-x-bokoro", "reg", "jas"),
        ("omw-x-bonta", "reg", "1co"),
        ("ors-x-oranglau", "reg", "mrk"),
        ("ors-x-oranglau", "reg", "jhn"),
        ("pip", "reg", "1ti"),
        ("pip", "reg", "2co"),
        ("pip", "reg", "2th"),
        ("pip", "reg", "rom"),
        ("pip", "reg", "mat"),
        ("pse-x-riauasli", "reg", "luk"),
        ("rmn-x-yerliroman", "reg", "mat"),
        ("rmp", "ulb", "jas"),
        ("ruc", "reg", "jhn"),
        ("ruc", "reg", "1ti"),
        ("rw-x-kinyabwisha", "reg", "num"),
        ("rw-x-kinyabwisha", "reg", "luk"),
        ("saw", "reg", "1ch"),
        ("saw", "reg", "luk"),
        ("saw", "reg", "psa"),
        ("saw", "reg", "job"),
        ("saw", "reg", "sng"),
        ("saw", "reg", "dan"),
        ("saw", "reg", "est"),
        ("sbp", "reg", "phm"),
        ("sbp", "reg", "2th"),
        ("sbp", "reg", "1ti"),  # failed to fix
        ("sbp", "reg", "2ti"),
        ("sbp", "reg", "eph"),
        ("sbs-x-chiikuhane", "reg", "jon"),
        ("scg-x-mayau", "reg", "luk"),
        ("scg-x-mayau", "reg", "jas"),
        ("sdm-x-beginci", "reg", "2th"),
        ("sdm-x-beginci", "reg", "2pe"),
        ("set-x-csentani", "reg", "mrk"),
        ("set-x-csentani", "reg", "2jn"),
        ("sie-x-makoma", "reg", "2th"),
        ("sie-x-makoma", "reg", "2jn"),
        ("sie-x-makoma", "reg", "rut"),
        ("spy-x-bongomek", "reg", "phm"),
        ("spy-x-bongomek", "reg", "2jn"),
        ("spy-x-pok", "reg", "jud"),
        ("spy-x-pok", "reg", "3jn"),  # failed to fix
        ("ssc-x-kine", "reg", "2jn"),
        ("ssn-x-sanye", "reg", "col"),
        ("tar-x-ralamuli", "reg", "mrk"),
        ("tbp-x-airo", "reg", "php"),
        ("thr", "reg", "tit"),
        ("ttl-x-totelnamib", "reg", "3jn"),
        ("txy", "reg", "1co"),
        ("txy", "reg", "2jn"),
        ("tyn", "reg", "jud"),
        ("tyn", "reg", "mrk"),
        ("vin", "reg", "2co"),
        ("vin", "reg", "1th"),
        ("vin", "reg", "1ti"),
        ("vin", "reg", "gal"),
        ("wbj", "reg", "luk"),
        ("wbj", "reg", "tit"),
        ("wbj", "reg", "2jn"),
        ("wkd", "reg", "mrk"),
        ("wkd", "reg", "3jn"),
        ("wsk-x-makitu", "reg", "php"),
        ("wsk-x-makitu", "reg", "3jn"),
        ("xem-x-karambai", "reg", "luk"),
        ("xem-x-karambai", "reg", "eph"),
        ("xkg", "reg", "3jn"),
        ("xmt", "reg", "eph"),
        ("xwg", "reg", "luk"),
        ("zga-x-mahanji", "reg", "php"),
        ("ziw", "reg", "1th"),
        ("ziw", "reg", "1jn"),
        ("zlm-x-kisaran", "reg", "2ti"),
    ]

    TEMPLATE_PATHS_MAP: Mapping[str, str] = {
        "stet": "backend/templates/mustache/template.mustache",
        "stet_html": "backend/templates/html/stet.html",
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
    RESOURCE_ASSETS_DIR: str = "assets_download"

    # Location where intermediate generated document parts are saved.
    WORKING_DIR: str = "working_temp"

    # Location where generated PDFs are written.
    DOCUMENT_OUTPUT_DIR: str = "document_output"

    # Location where stet source Docx document(s) are stored
    STET_DIR: str = "stet"

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
