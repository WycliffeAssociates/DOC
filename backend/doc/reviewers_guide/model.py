"""Models for reviewer's guide"""

from typing import Optional, final
from pprint import pformat
from doc.domain.model import ChapterNum, LangDirEnum
from pydantic import BaseModel


@final
class Part1Item(BaseModel):
    text: str
    reference: str


@final
class Part2Item(BaseModel):
    reference: str
    question: str
    answer: str


@final
class BibleReference(BaseModel):
    book_code: str
    book_name: str
    start_chapter: ChapterNum
    start_chapter_verse_ref: str
    end_chapter: Optional[ChapterNum]
    end_chapter_verse_ref: Optional[str]


@final
class ParsedText(BaseModel):
    bible_reference: BibleReference
    background: Optional[str]
    directive: str
    part_1: list[Part1Item]
    part_1_directive: str
    part_2: list[Part2Item]
    part_2_directive: str
    comment_section: Optional[str] = None


@final
class RGChapter(BaseModel):
    content: list[ParsedText]


@final
class RGBook(BaseModel):
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
