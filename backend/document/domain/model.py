"""
This module provides classes that are used as data transfer objects.
In particular, many of the classes here are subclasses of
pydantic.BaseModel as FastAPI can use these classes to do automatic
validation and JSON serialization.
"""

from enum import Enum
from typing import Any, Callable, NamedTuple, Optional, Sequence, Union, final

import orjson
from pydantic import BaseModel, EmailStr

# These Type Aliases give us more self-documenting code, but of course
# aren't strictly necessary.
HtmlContent = str
MarkdownContent = str
VerseRef = str
ChapterNum = int


def orjson_dumps(v: Any, *, default: Optional[Callable[[Any], Any]]) -> str:
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


@final
class AssemblyStrategyEnum(str, Enum):
    """
    There is currently one high level assembly strategy kind to choose from:

    * LANGUAGE_BOOK_ORDER
      - This enum value signals to use the high level strategy that orders
        by language and then by book before delegating to an assembly
        sub-strategy.
    * BOOK_LANGUAGE_ORDER
      - This enum value signals to use the high level strategy that orders
        by book and then by language  before delegating to an assembly
        sub-strategy.

    NOTE
    We could later add others. As an arbitrary example,
    Perhaps we'd want a high level strategy that ordered by book then
    language (as opposed to the other way around) before delegating
    the lower level assembly to a sub-strategy as signaled by
    AssemblySubstrategyEnum. The sky is the limit.
    """

    LANGUAGE_BOOK_ORDER = "lbo"
    BOOK_LANGUAGE_ORDER = "blo"

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


@final
class AssemblyLayoutEnum(str, Enum):
    """
    A enum used by the assembly_strategies module to know how
    to layout the content.

    We can have N such layouts and each can be completely
    arbitrary, simply based on the desires of content designers.

    Said another way: the enum is just a name that is arbitrarily
    chosen to be compact but adequate to express the type of layout
    that is to be accomplished in the HTML document (prior to conversion
    to PDF).

    Layouts:

    * ONE_COLUMN
      One column verse and associated content interleave

    * ONE_COLUMN_COMPACT
      This layout minimizes whitespace in a one column layout so as to
      be appropriate for printing to paper.

    * TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
      Two columns, with scripture on the left and a different
      scripture on the right. Obviously only applicable when at least
      two languages have been chosen. This layout has less whitespace
      than TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT because verses on
      the left are typically about the same size as verses on the right
      and helps are shown vertically spanning the whole horizontal space
      after each verse.

    * TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT
      This layout minimizes whitespace by using
      TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT layout but with a
      different CSS styling that results in less whitespace.
    """

    ONE_COLUMN = "1c"
    ONE_COLUMN_COMPACT = "1c_c"
    # fmt: off
    # NOTE The next two layouts only make sense
    # with an AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER assembly
    # strategy and when more than one language is chosen for the same
    # book.
    TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT = "2c_sl_sr"
    TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT = "2c_sl_sr_c"
    # fmt: on

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


# https://blog.meadsteve.dev/programming/2020/02/10/types-at-the-edges-in-python/
# https://pydantic-docs.helpmanual.io/usage/models/
@final
class ResourceRequest(BaseModel):
    """
    This class is used to encode a request for a resource, e.g.,
    language 'English', en, resource type 'ulb', resource code, i.e.,
    book, 'gen'. A document request composes n of these resource
    request instances. Because this class inherits from pydantic's
    BaseModel we get validation and JSON serialization for free.
    """

    lang_code: str
    resource_type: str
    resource_code: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


@final
class DocumentRequest(BaseModel):
    """
    This class is used to send in a document generation request from
    the front end client. A document request is composed of n resource
    requests. Because this class inherits from pydantic's BaseModel we
    get validation, serialization, and special dunder functions for
    free.
    """

    email_address: Optional[EmailStr]
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
    assembly_layout_kind: Optional[AssemblyLayoutEnum]
    # The user can choose whether the result should be formatted to
    # print. When the user selects yes/True to format for print
    # then we'll choose a compact layout that makes sense for their
    # document request. This happens in
    # document_generator.select_assembly_layout_kind if
    # assembly_layout_kind is None in the document request.
    layout_for_print: bool = False
    resource_requests: Sequence[ResourceRequest]
    # Indicate whether PDF should be generated.
    generate_pdf: bool = True
    # Indicate whether ePub should be generated.
    generate_epub: bool = False
    # Indicate whether Docx should be generated.
    generate_docx: bool = False

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


@final
class FinishedDocumentDetails(BaseModel):
    """
    Pydantic model that we use as a return value to send back via
    FastAPI to the client. For now it just contains the finished
    document filepath on disk.
    """

    finished_document_request_key: Optional[str]
    message: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


@final
class AssetSourceEnum(str, Enum):
    """
    This class/enum captures the concept of: where did the resource's
    asset files come from? At present they come from either a GIT
    repository, an individual USFM file download, or a ZIP file
    download.
    """

    GIT = "git"
    USFM = "usfm"
    ZIP = "zip"


@final
class ResourceLookupDto(NamedTuple):
    """
    'Data transfer object' that we use to send lookup related info to
    the resource.
    """

    lang_code: str
    lang_name: str
    resource_type: str
    resource_type_name: str
    resource_code: str
    url: Optional[str]
    source: AssetSourceEnum
    jsonpath: Optional[str]


@final
class TNChapter(NamedTuple):
    """
    A class to hold a chapter's intro translation notes and a mapping
    of its verse references to translation notes HTML content.
    """

    intro_html: HtmlContent
    verses: dict[VerseRef, HtmlContent]


@final
class TNBook(NamedTuple):
    """
    A class to hold a book's intro translation notes and a mapping
    of chapter numbers to translation notes HTML content.
    """

    lang_code: str
    lang_name: str
    resource_code: str
    resource_type_name: str
    intro_html: HtmlContent
    chapters: dict[ChapterNum, TNChapter]


@final
class TQChapter(NamedTuple):
    """
    A class to hold a mapping of verse references to translation
    questions HTML content.
    """

    verses: dict[VerseRef, HtmlContent]


@final
class TQBook(NamedTuple):
    """
    A class to hold a mapping of chapter numbers to translation questions
    HTML content.
    """

    lang_code: str
    lang_name: str
    resource_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, TQChapter]


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


@final
class TWNameContentPair:
    """
    A class to hold the localized translation word and its associated
    HTML content (which was converted from its Markdown).
    """

    def __init__(self, localized_word: str, content: HtmlContent):
        self.localized_word = localized_word
        self.content = content  # content gets mutated after instantiation therefore we don't use a NamedTuple (which is immutable)


@final
class TWBook(NamedTuple):
    """
    A class to hold a list of TWNameContentPair instances and a list
    of TWUses instances.
    """

    lang_code: str
    lang_name: str
    resource_code: str
    resource_type_name: str
    name_content_pairs: list[TWNameContentPair] = []
    uses: dict[str, list[TWUse]] = {}


@final
class BCChapter(NamedTuple):
    """
    A class to hold a mapping of verse references to bible
    commentary HTML content.
    """

    commentary: HtmlContent


@final
class BCBook(NamedTuple):
    """
    A class to hold a mapping of chapter numbers to translation questions
    HTML content.
    """

    book_intro: str
    lang_code: str
    lang_name: str
    resource_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, BCChapter]


@final
class USFMChapter(NamedTuple):
    """
    A class to hold the USFM converted to HTML content for a chapter
    in total (including things like 'chunk breaks' and other verse
    formatting HTML elements), chapter_content, and by verse per
    chapter (missing the 'chunk breaks' and other inter-verse HTML
    formatting elements), chapter_verses. The purpose of
    'chapter_content' is so that you can display a whole chapter at a
    time should the system wish to do so. The purpose of
    'chapter_verses' is so that you can display verses in a particular
    chapter one at a time or a range of them at a time should the
    system desire to do so.
    """

    content: list[HtmlContent]
    verses: dict[VerseRef, HtmlContent]
    footnotes: HtmlContent


@final
class USFMBook(NamedTuple):
    """A class to hold a book's USFMChapter instances."""

    lang_code: str
    lang_name: str
    resource_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, USFMChapter]


BookContent = Union[USFMBook, TNBook, TQBook, TWBook, BCBook]


@final
class CodeNameTypeTriplet(BaseModel):
    """A utility class to provide validation in resource_lookup module."""

    lang_code: str
    lang_name: str
    resource_types: list[str]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


@final
class WikiLink(NamedTuple):
    """
    Reify a wiki link for use in link_transformer_preprocessor
    module.
    """

    url: str


@final
class Attachment(NamedTuple):
    filepath: str
    mime_type: tuple[str, str]
