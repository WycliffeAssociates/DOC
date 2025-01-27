from pydantic import BaseModel, EmailStr
from typing import Optional, NamedTuple, final


@final
class PassageReferenceDto(NamedTuple):
    lang_code: str
    book_code: str
    book_name: str
    chapter_num: int
    verse_reference: str


@final
class PassageDto(NamedTuple):
    passage_text: str  # HTML of passage
    passage_reference: str


@final
class PassagesDocumentRequest(BaseModel):
    lang_code: str
    passage_references: str  # comma-delimited passage references
    email_address: Optional[EmailStr]
