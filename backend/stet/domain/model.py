from dataclasses import dataclass, field
from typing import NamedTuple, Optional, final
from pydantic import BaseModel, EmailStr


@final
class VerseEntry(NamedTuple):
    source_reference: str
    source_text: str
    target_reference: str
    target_text: str


@final
@dataclass
class WordEntry:
    words: list[str] = field(default_factory=list)
    strongs_numbers: str = ""
    definition: str = ""
    verses: list[VerseEntry] = field(default_factory=list)
    bolded_phrases: list[str] = field(default_factory=list)


@final
class VerseReferenceDto(NamedTuple):
    lang0_code: str
    lang1_code: str
    book_code: Optional[str]
    book_name: str
    chapter_num: int
    source_reference: str
    target_reference: str
    verse_refs: list[str]


@final
@dataclass
class WordEntryDto:
    words: list[str] = field(default_factory=list)
    strongs_numbers: str = ""
    definition: str = ""
    verse_ref_dtos: list[VerseReferenceDto] = field(default_factory=list)
    bolded_phrases: list[str] = field(default_factory=list)


@final
class StetDocumentRequest(BaseModel):
    # The source language
    lang0_code: str
    # The target language
    lang1_code: str
    email_address: Optional[EmailStr]
