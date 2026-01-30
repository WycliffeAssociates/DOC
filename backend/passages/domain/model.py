from typing import Optional, NamedTuple, final, TypeAlias

from doc.domain.model import ChapterNum
from pydantic import BaseModel, EmailStr


@final
class BibleReference(BaseModel):
    lang_code: str
    book_code: str
    book_name: str
    start_chapter: ChapterNum
    start_chapter_verse_ref: str
    end_chapter: Optional[ChapterNum]
    end_chapter_verse_ref: Optional[str]


@final
class BibleReferenceWithAvailability(BaseModel):
    reference: BibleReference
    is_available: bool


@final
class Passage(NamedTuple):
    reference: BibleReference
    passage_text: str  # HTML of passage
    localized_reference: str
    is_available: bool


@final
class PassagesDocumentRequest(BaseModel):
    lang0_code: str
    lang0_name: str
    lang1_code: Optional[str]
    lang1_name: Optional[str]
    bible_references: list[BibleReferenceWithAvailability]
    email_address: Optional[EmailStr]
