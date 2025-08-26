import re

from doc.config import settings


logger = settings.logger(__name__)


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


_ROMAN_TO_INT = {
    "I": "1",
    "II": "2",
    "III": "3",
}


def normalize_localized_book_name(localized_book_name: str) -> str:
    """
    >>> normalize_localized_book_name("1Peter")
    '1 Peter'
    >>> normalize_localized_book_name("I peter")
    '1 Peter'
    >>> normalize_localized_book_name("III John")
    '3 John'
    >>> normalize_localized_book_name("II john")
    '2 John'
    >>> normalize_localized_book_name("IIjohn")
    '2 John'
    >>> normalize_localized_book_name("john")
    'John'
    >>> normalize_localized_book_name("John")
    'John'
    >>> normalize_localized_book_name("Isaías")
    'Isaías'
    """
    name = localized_book_name.strip()
    match = re.match(r"^(1|2|3|i{1,3})", name, re.IGNORECASE)
    if match:
        numeral_raw = match.group(1)
        numeral_upper = numeral_raw.upper()
        next_char = name[len(numeral_raw) : len(numeral_raw) + 1]
        # Special case: single "I" must be followed by space or uppercase to count as numeral
        if numeral_upper == "I" and not (
            next_char.isspace() or (next_char and next_char.isupper())
        ):
            pass  # treat as normal word
        else:
            if numeral_upper in _ROMAN_TO_INT:
                number = _ROMAN_TO_INT[numeral_upper]
            else:
                number = numeral_upper  # already numeric
            rest = name[len(numeral_raw) :].strip()
            if rest:
                # rest = rest[0].upper() + rest[1:]
                rest = rest.lower().capitalize()
                name = f"{number} {rest}"
            else:
                name = number
            return normalize_spaces(name)
    # Default: just capitalize first letter
    # name = name[0].upper() + name[1:]
    name = name.lower().capitalize()
    return normalize_spaces(name)


def chapter_label_sans_numeric_part(s: str) -> str:
    parts = s.rsplit(maxsplit=1)
    # logger.debug("chapter label parts: %s", parts)
    if len(parts) > 1 and parts[-1].isdigit():
        result = parts[0]
    else:
        result = s
    # logger.debug("chapter label: %s", result)
    return result


def chapter_label_numeric_part(s: str) -> int:
    parts = s.rsplit(maxsplit=1)
    # logger.debug("chapter label parts: %s", parts)
    if len(parts) > 1 and parts[-1].isdigit():
        result = int(parts[-1])
    else:
        result = -1  # Sentinel
    return result


if __name__ == "__main__":

    # To run the doctests in this module, in the root of the project do:
    # python backend/document/domain/resource_lookup.py
    # or
    # python backend/document/domain/resource_lookup.py -v
    # See https://docs.python.org/3/library/doctest.html
    # for more details.
    import doctest

    doctest.testmod()
