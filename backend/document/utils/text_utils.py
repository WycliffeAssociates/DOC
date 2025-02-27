import re


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_national_book_name(national_book_name: str) -> str:
    # Deal with irregularities in national book names, e.g., bem: 1timote
    if national_book_name[0] in [
        "1",
        "2",
        "3",
    ]:  # E.g., bem: 1Timote or 2 Timote
        national_book_name = (
            national_book_name[0]
            + " "
            + national_book_name[1:].strip().lower().capitalize()
        )
        national_book_name = normalize_spaces(national_book_name)
    else:
        national_book_name = national_book_name.strip().lower().capitalize()
    return national_book_name
