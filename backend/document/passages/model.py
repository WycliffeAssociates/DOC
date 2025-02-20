from pydantic import BaseModel, EmailStr
from typing import Optional, NamedTuple, final


@final
class PassageReferenceDto(BaseModel):
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
    lang_name: str
    passage_references: list[PassageReferenceDto]
    email_address: Optional[EmailStr]
