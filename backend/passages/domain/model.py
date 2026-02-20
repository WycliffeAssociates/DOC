from typing import Optional, NamedTuple, final, TypeAlias

from doc.domain.model import ChapterNum
from doc.reviewers_guide.model import BibleReference
from pydantic import BaseModel, EmailStr




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
