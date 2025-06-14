import json
import re
from doc.domain.bible_books import BOOK_NAMES


BOOK_INDEX = dict((id, pos) for pos, id in enumerate(BOOK_NAMES.keys()))
BOOK_VERSE_PATTERN = re.compile(r"(?:([1-3]?\s?[A-Z][a-z]+)\s)?(\d+:\d+)")
HEADER_PATTERN = re.compile(r"^(\w+)\s+\(([\d,; ]+)\)")


def parse_bible_blocks(text: str) -> dict[str, list[str]]:
    entries = {}
    blocks = re.split(r"\n(?=\w+\s+\([\d,; ]+\))", text.strip(), flags=re.MULTILINE)
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        header_match = HEADER_PATTERN.match(lines[0])
        if not header_match:
            continue
        word = header_match.group(1)
        strongs = header_match.group(2).replace(";", ",").replace(" ", "")
        key = f"{word} ({strongs})"
        # Flatten all lines into one paragraph and remove commas
        reference_text = " ".join(lines[1:]).replace(",", "")
        # Extract references
        result = []
        current_book = None
        for match in BOOK_VERSE_PATTERN.finditer(reference_text):
            book, ref = match.groups()
            if book:
                current_book = book
            if current_book:
                result.append(f"{current_book} {ref}")
            else:
                result.append(f"UNKNOWN {ref}")

        # Sort canonically
        def sort_key(ref: str) -> tuple[int, int, int]:
            try:
                book, chap_verse = ref.rsplit(" ", 1)
                chapter, verse = map(int, chap_verse.split(":"))
                book_index = BOOK_INDEX.get(book, 999)
                return (book_index, chapter, verse)
            except Exception:
                return (999, 0, 0)

        entries[key] = sorted(result, key=sort_key)
    return entries


def to_json(parsed_data: dict[str, list[str]]) -> str:
    return json.dumps(parsed_data, indent=2)
