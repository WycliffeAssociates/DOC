from dataclasses import dataclass, field


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
