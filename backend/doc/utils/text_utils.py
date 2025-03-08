import re
from doc.config import settings

logger = settings.logger(__name__)


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_localized_book_name(localized_book_name: str) -> str:
    # Deal with irregularities in localized book names, e.g., bem: 1timote
    if localized_book_name[0] in [
        "1",
        "2",
        "3",
    ]:  # E.g., bem: 1Timote or 2 Timote
        localized_book_name = (
            localized_book_name[0]
            + " "
            + localized_book_name[1:].strip().lower().capitalize()
        )
        localized_book_name = normalize_spaces(localized_book_name)
    else:
        localized_book_name = localized_book_name.strip().lower().capitalize()
    return localized_book_name


def chapter_label_sans_numeric_part(s: str) -> str:
    parts = s.rsplit(maxsplit=1)
    if len(parts) > 1 and parts[-1].isdigit():
        result = parts[0]
    else:
        result = s
    logger.debug("chapter label: %s", result)
    return result
