from dataclasses import dataclass, field
from typing import Optional, final
from pydantic import BaseModel, EmailStr


@dataclass
class VerseEntry:
    """A verse entry from the given doc"""

    source_reference: str
    source_text: str
    target_reference: str
    target_text: str


@dataclass
class WordEntry:
    """A word entry from the given doc"""

    word: str = ""
    strongs_numbers: str = ""
    definition: str = ""
    verses: list[VerseEntry] = field(default_factory=list)


@dataclass
class VerseReferenceDto:
    lang0_code: str
    lang1_code: str
    book_code: Optional[str]
    book_name: str
    chapter_num: int
    source_reference: str
    target_reference: str
    verse_refs: list[str] = field(default_factory=list)


@dataclass
class WordEntryDto:
    """A word entry data transfer object from the given doc"""

    word: str = ""
    strongs_numbers: str = ""
    definition: str = ""
    verse_ref_dtos: list[VerseReferenceDto] = field(default_factory=list)


@final
class StetDocumentRequest(BaseModel):
    # The source language
    lang0_code: str
    # The target language
    lang1_code: str
    email_address: Optional[EmailStr]
