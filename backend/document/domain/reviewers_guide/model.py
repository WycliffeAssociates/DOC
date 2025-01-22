"""Models for reviewer's guide"""

from dataclasses import dataclass
from typing import NamedTuple, Optional, final
from pprint import pformat
from document.domain.model import ChapterNum, LangDirEnum


@final
class Part1Item(NamedTuple):
    text: str
    reference: str


@final
class Part2Item(NamedTuple):
    reference: str
    question: str
    answer: str


@final
class BibleReference(NamedTuple):
    book_code: str
    book_name: str
    chapter: int
    verse_ref: str


@final
@dataclass
class ParsedText:
    bible_reference: BibleReference
    background: Optional[str]
    directive: str
    part_1: list[Part1Item]
    part_1_directive: str
    part_2: list[Part2Item]
    part_2_directive: str
    comment_section: Optional[str] = None


@final
class RGChapter(NamedTuple):
    content: ParsedText


@final
class RGBook(NamedTuple):
    lang_code: str
    lang_name: str
    book_code: str
    resource_type_name: str
    chapters: dict[ChapterNum, RGChapter]
    lang_direction: LangDirEnum

    # For pprint
    def __repr__(self) -> str:
        chapters_str = pformat(self.chapters)
        return (
            f"RGBook(\n"
            f"  lang_code={self.lang_code},\n"
            f"  lang_name={self.lang_name},\n"
            f"  book_code={self.book_code},\n"
            f"  resource_type_name={self.resource_type_name},\n"
            f"  chapters={chapters_str},\n"
            f"  lang_direction={self.lang_direction}\n"
            f")"
        )
