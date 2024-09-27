"""
This module provides classes that are used as data transfer objects.
In particular, many of the classes here are subclasses of
pydantic.BaseModel as FastAPI can use these classes to do automatic
validation and JSON serialization.
"""

from enum import Enum
from typing import Any, NamedTuple, Optional, Sequence, final

from document.config import settings
from document.domain.bible_books import BOOK_NAMES
from document.utils.number_utils import is_even
from pydantic import BaseModel, EmailStr
from pydantic.functional_validators import model_validator

# These type aliases give us more self-documenting code, but of course
# aren't strictly necessary.
VerseRef = str
ChapterNum = int


@final
class AssemblyStrategyEnum(str, Enum):
    """
    * LANGUAGE_BOOK_ORDER
      - This enum value signals to use the high level strategy that orders
        by language and then by book before delegating to an assembly
        sub-strategy.
    * BOOK_LANGUAGE_ORDER
      - This enum value signals to use the high level strategy that orders
        by book and then by language before delegating to an assembly
        sub-strategy.
    """

    LANGUAGE_BOOK_ORDER = "lbo"
    BOOK_LANGUAGE_ORDER = "blo"
    STET_STRATEGY = "stet"


@final
class AssemblyLayoutEnum(str, Enum):
    """
    An enum used by the assembly_strategies module to know how
    to layout the content.

    We can have N such layouts and each can be completely
    arbitrary, simply based on the desires of content designers.

    Layouts:

    * ONE_COLUMN
      All content in one column

    * ONE_COLUMN_COMPACT
      This layout minimizes whitespace in a one column layout so as to
      be appropriate for printing to paper.

    * TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
      Two columns, with scripture on the left and a different
      scripture on the right. Obviously only applicable when at least
      two languages have been chosen.

    * TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT
      This layout minimizes whitespace by using
      TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT layout but with a
      different CSS styling that results in less whitespace.
    """

    ONE_COLUMN = "1c"
    ONE_COLUMN_COMPACT = "1c_c"
    # NOTE The next two layouts only make sense
    # with an AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER assembly
    # strategy and when more than one language is chosen for the same
    # book.
    # fmt: off
    TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT = "2c_sl_sr"
    TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT = "2c_sl_sr_c"
    # fmt: on
    STET_LAYOUT = "stet"


@final
class ChunkSizeEnum(str, Enum):
    """
    The length of content to burst out at a time when interleaving.
    E.g., if CHAPTER is chosen as the chunk size then the interleaving will
    do so in chapter chunks (one chapter of scripture, then one chapter of helps,
    etc.). This exists because translators want to be able to choose
    the chunk size of scripture that should be grouped together for the
    purpose of translational cohesion.

    * CHAPTER
      - This enum value signals to make each chunk of interleaved
        content be one chapter's worth in length.
    """

    CHAPTER = "chapter"


# https://blog.meadsteve.dev/programming/2020/02/10/types-at-the-edges-in-python/
# https://pydantic-docs.helpmanual.io/usage/models/
@final
class ResourceRequest(BaseModel):
    """
    This class is used to encode a request for a resource. A
    document request composes N of these resource request instances.
    """

    lang_code: str
    resource_type: str
    book_code: str


@final
class DocumentRequestSourceEnum(str, Enum):
    """
    This class/enum captures the concept of: where did the document
    request originate from?
    """

    UI = "ui"
    TEST = "test"
    BIEL_UI = "biel_ui"


@final
class DocumentRequest(BaseModel):
    """
    This class reifies a document generation request from a client of
    the API.
    """

    email_address: Optional[EmailStr] = None
    assembly_strategy_kind: AssemblyStrategyEnum
    # NOTE For testing we want to exercise various layouts, thus we
    # make this attribute Optional so that we can specify it in unit
    # tests if desired. But the normal case is to set
    # assembly_layout_kind to None in a document request if we are
    # manually coding up a document request instance to send to the
    # API. If you go this latter route, say to use the API in a
    # different context than interacting with the UI then the onus is
    # on you as the developer to choose an assembly_layout_kind that
    # makes sense given the document request you have instantiated.
    # The system knows which make sense and which do not given your
    # document request and if you choose one that does not make sense
    # then you'll get an exception on purpose.
    assembly_layout_kind: Optional[AssemblyLayoutEnum] = AssemblyLayoutEnum.ONE_COLUMN
    # The user can choose whether the result should be formatted to
    # print. When the user selects yes/True to format for print
    # then we'll choose a compact layout that makes sense for their
    # document request.
    layout_for_print: bool = False
    resource_requests: Sequence[ResourceRequest]
    # Indicate whether PDF should be generated.
    generate_pdf: bool = True
    # Indicate whether ePub should be generated.
    generate_epub: bool = False
    # Indicate whether Docx should be generated.
    generate_docx: bool = False
    # Indicate the chunk size to interleave. Default to chapter. Verse
    # chunk size was deemed non-useful, but remains for now as a historical
    # option.
    chunk_size: ChunkSizeEnum = ChunkSizeEnum.CHAPTER
    # Indicate whether translation words, TW, should be limited to
    # only those that appear in the USFM requested (True), or, include all
    # the TW words available for the language requested (False).
    limit_words: bool = True
    # Indicate whether TN book intros should be included. Currently,
    # the content team does not want them included.
    include_tn_book_intros: bool = False
    # Indicate where the document request originated from. We default to
    # TEST so that tests don't have to specify and every other client, e.g.,
    # UI, should specify in order for
    # document_generator.select_assembly_layout_kind to produce
    # expected results.
    document_request_source: DocumentRequestSourceEnum = DocumentRequestSourceEnum.TEST

    @model_validator(mode="after")
    def ensure_valid_document_request(self) -> Any:
        """
        See ValueError messages below for the rules we are enforcing.
        """
        usfm_resource_types = settings.USFM_RESOURCE_TYPES
        non_usfm_resource_types = [
            settings.EN_TN_CONDENSED_RESOURCE_TYPE,
            settings.TN_RESOURCE_TYPE,
            settings.TQ_RESOURCE_TYPE,
            settings.TW_RESOURCE_TYPE,
            settings.BC_RESOURCE_TYPE,
        ]
        all_resource_types = [*usfm_resource_types, *non_usfm_resource_types]
        if not self.resource_requests:
            raise ValueError("DocumentRequest has no resource requests.")
        for resource_request in self.resource_requests:
            # Make sure resource_type for every ResourceRequest instance
            # is a valid value
            if resource_request.resource_type not in all_resource_types:
                raise ValueError(
                    f"{resource_request.resource_type} is not a valid resource type"
                )
            # Make sure book_code is a valid value
            if resource_request.book_code not in BOOK_NAMES.keys():
                raise ValueError(
                    f"{resource_request.book_code} is not a valid book code"
                )
        # Partition USFM resource requests by language
        language_groups: dict[str, list[ResourceRequest]] = {}
        for resource in filter(
            lambda r: r.resource_type in usfm_resource_types, self.resource_requests
        ):
            lang_code = resource.lang_code
            if lang_code not in language_groups:
                language_groups[lang_code] = []
            language_groups[lang_code].append(resource)
        # Get a list of the sorted set of books for each language for later
        # comparison.
        sorted_book_set_for_each_language = [
            sorted({item.book_code for item in value})
            for key, value in language_groups.items()
        ]
        # Next two assignments are later used to do a not all equal check.
        # Check if all sets have equal lengths
        are_lengths_equal = all(
            len(set_) == len(sorted_book_set_for_each_language[0])
            for set_ in sorted_book_set_for_each_language
        )
        # Check if all sets have equal elements
        are_sets_equal = all(
            set_ == sorted_book_set_for_each_language[0]
            for set_ in sorted_book_set_for_each_language
        )
        # Get the unique number of languages
        number_of_usfm_languages = len(
            # set(
            [
                resource_request.lang_code
                for resource_request in self.resource_requests
                if resource_request.resource_type in usfm_resource_types
            ]
            # )
        )
        if (
            self.assembly_strategy_kind != AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
            and self.assembly_layout_kind
            == AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
        ):
            raise ValueError(
                "Two column scripture left, scripture right layout is only compatible with book language order assembly strategy."
            )
        elif (
            self.assembly_strategy_kind == AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
            and self.assembly_layout_kind
            == AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
            # Because book content for different languages will be side by side for
            # the scripture left scripture right layout, we make sure there are a non-zero
            # even number of languages so that we can display them left and right in
            # pairs.
            and not is_even(number_of_usfm_languages)
        ):
            raise ValueError(
                "Two column scripture left, scripture right layout requires a non-zero even number of languages. For an uneven number of languages you'll want to use the one column layout kind."
            )
        elif (
            self.assembly_strategy_kind == AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER
            and self.assembly_layout_kind
            == AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
            # Because book content for different languages will be side by side for
            # the scripture left scripture right layout, we make sure there are a non-zero
            # even number of languages so that we can display them left and right in
            # pairs.
            # and number_of_usfm_languages > 1
            and is_even(number_of_usfm_languages)
            # Each language must have the same set of books in order to
            # use the scripture left scripture right layout strategy. As an example,
            # you wouldn't want to allow the sl-sr layout if the document request
            # asked for Swahili ulb for Lamentations and Spanish ulb for Nahum -
            # the set of books in each language are not the same and so do not make
            # sense to be displayed side by side.
            # and not all_equal(sorted_book_set_for_each_language)
            and not (are_lengths_equal and are_sets_equal)
        ):
            raise ValueError(
                "Two column scripture left, scripture right layout requires the same books for each language chosen since they are displayed side by side. If you want a different set of books for each language you'll instead need to use the one column layout."
            )
        return self


@final
class LangDirEnum(str, Enum):
    """
    This class/enum enumerates the possible language display
    directions: LTR or RTL.
    """

    LTR = "ltr"
    RTL = "rtl"


@final
class ResourceLookupDto(NamedTuple):
    """
    'Data transfer object' that we use to send resource lookup related
    info around in the system.
    """

    lang_code: str
    lang_name: str
    resource_type: str
    resource_type_name: str
    book_code: str
    lang_direction: LangDirEnum
    url: Optional[str]


@final
class TNChapter(NamedTuple):
    """
    A class to hold a chapter's intro translation notes and a mapping
    of its verse references to translation notes HTML content.
    """

    intro_html: str
    verses: dict[VerseRef, str]


@final
class TNBook(NamedTuple):
    """
    A class to hold a book's intro translation notes and a mapping
    of chapter numbers to translation notes HTML content.
    """

    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    book_intro: str
    chapters: dict[ChapterNum, TNChapter]
    lang_direction: LangDirEnum


@final
class TQChapter(NamedTuple):
    """
    A class to hold a mapping of verse references to translation
    questions HTML content.
    """

    verses: dict[VerseRef, str]


@final
class TQBook(NamedTuple):
    """
    A class to hold a mapping of chapter numbers to translation questions
    HTML content.
    """

    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, TQChapter]
    lang_direction: LangDirEnum


@final
class TWUse(NamedTuple):
    """
    A class to reify a reference to a translation word occurring
    in a USFM verse.
    """

    lang_code: str
    book_id: str
    book_name: str
    chapter_num: ChapterNum
    verse_num: VerseRef
    localized_word: str


# `content' gets mutated after instantiation therefore we can't subclass NamedTuple
@final
class TWNameContentPair:
    """
    A class to hold the localized translation word and its associated
    HTML content.
    """

    def __init__(self, localized_word: str, content: str):
        self.localized_word = localized_word
        self.content = content


@final
class TWBook(NamedTuple):
    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    lang_direction: LangDirEnum
    name_content_pairs: list[TWNameContentPair] = []
    # uses: dict[str, list[TWUse]] = {}


@final
class BCChapter(NamedTuple):
    commentary: str


@final
class BCBook(NamedTuple):
    """
    A class to hold a mapping of chapter numbers to translation questions
    HTML content.
    """

    book_intro: str
    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, BCChapter]
    lang_direction: LangDirEnum = LangDirEnum.LTR


@final
class USFMChapter(BaseModel):
    """
    A class to hold the USFM converted to HTML content for a chapter
    in total (including things like 'chunk breaks' and other verse
    formatting HTML elements), content, and chapter verses, i.e., missing
    the 'chunk breaks' and other inter-verse HTML formatting elements.
    The purpose of 'content' is so that you can display a whole
    chapter at a time when desired. The purpose of 'verses' is so that you
    can display verses in a particular chapter one at a time or a range of
    them at a time.
    """

    content: str
    verses: Optional[dict[VerseRef, str]]


@final
class USFMBook(NamedTuple):
    """A class to hold a book's USFMChapter instances."""

    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, USFMChapter]
    lang_direction: LangDirEnum


@final
class WikiLink(NamedTuple):
    """
    Reify a wiki link for use in link_transformer_preprocessor
    module.
    """

    url: str


@final
class Attachment(NamedTuple):
    """
    An email attachment.
    """

    filepath: str
    mime_type: tuple[str, str]
