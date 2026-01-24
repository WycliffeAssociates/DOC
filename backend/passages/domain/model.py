from typing import Optional, NamedTuple, final

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
    passage_text: str  # HTML of passage
    bible_reference: str
    is_available: bool


@final
class PassagesDocumentRequest(BaseModel):
    lang_code: str
    lang_name: str
    bible_references: list[BibleReferenceWithAvailability]
    email_address: Optional[EmailStr]
