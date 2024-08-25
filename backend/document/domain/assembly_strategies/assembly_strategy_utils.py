"""
Utility functions used by assembly_strategies.
"""

from re import search, sub
from typing import Mapping, Optional, Sequence

from document.config import settings
from document.domain.bible_books import BOOK_NAMES
from document.domain.model import (
    BCBook,
    LangDirEnum,
    TNBook,
    TQBook,
    USFMBook,
)


logger = settings.logger(__name__)

H1, H2, H3, H4, H5, H6 = "h1", "h2", "h3", "h4", "h5", "h6"


def chapter_heading(
    chapter_num: int,
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
) -> str:
    return chapter_header_fmt_str.format(chapter_num)


def adjust_book_intro_headings(
    book_intro: str,
    h1: str = H1,
    h2: str = H2,
    h3: str = H3,
    h4: str = H4,
    h6: str = H6,
) -> str:
    """Change levels on headings."""
    # Move the H2 out of the way, we'll deal with it last.
    book_intro = sub(h2, h6, book_intro)
    book_intro = sub(h1, h2, book_intro)
    book_intro = sub(h3, h4, book_intro)
    book_intro = sub(h2, h3, book_intro)
    # Now adjust the temporary H6s.
    return sub(h6, h3, book_intro)


def adjust_commentary_headings(
    chapter_commentary: str,
    h1: str = H1,
    h2: str = H2,
    h3: str = H3,
    h4: str = H4,
    h5: str = H5,
    h6: str = H6,
) -> str:
    """Change levels on headings."""
    # Move the H4 out of the way, we'll deal with it last.
    chapter_commentary = sub(h4, h6, chapter_commentary)
    chapter_commentary = sub(h3, h4, chapter_commentary)
    chapter_commentary = sub(h1, h3, chapter_commentary)
    chapter_commentary = sub(h2, h4, chapter_commentary)
    # Now adjust the temporary H6s.
    return sub(h6, h5, chapter_commentary)


def chapter_intro(
    tn_book: Optional[TNBook],
    chapter_num: int,
    hr: str = "<hr/>",
) -> str:
    """Get the chapter intro."""
    content = []
    if (
        tn_book
        and chapter_num in tn_book.chapters
        and tn_book.chapters[chapter_num].intro_html
    ):
        content.append(tn_book.chapters[chapter_num].intro_html)
        content.append(hr)
    return "".join(content)


def has_footnotes(html_content: str) -> bool:
    return bool(search(r'<div[^>]*class="footnotes"', html_content))


def book_title(
    book_code: str,
    fmt_str: str = settings.BOOK_NAME_FMT_STR,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> str:
    return fmt_str.format(book_names[book_code])


def bc_book_intro(
    bc_book: Optional[BCBook],
    hr: str = "<hr/>",
) -> str:
    content = ""
    if bc_book and bc_book.book_intro:
        content = f"{bc_book.book_intro}{hr}"
    return content


def tn_book_intro(
    tn_book: Optional[TNBook],
    hr: str = "<hr/>",
) -> str:
    content = ""
    if tn_book and tn_book.book_intro:
        content = f"{tn_book.book_intro}{hr}"
    return content


def chapter_commentary(
    bc_book: Optional[BCBook],
    chapter_num: int,
    hr: str = "<hr/>",
) -> str:
    """Get the chapter commentary."""
    content = ""
    if (
        bc_book
        and chapter_num in bc_book.chapters
        and bc_book.chapters[chapter_num].commentary
    ):
        content = f"{bc_book.chapters[chapter_num].commentary}{hr}"
    return content


def usfm_language_direction_html(
    usfm_book: Optional[USFMBook],
    rtl_direction_html: str = settings.RTL_DIRECTION_HTML,
    ltr_direction_html: str = settings.LTR_DIRECTION_HTML,
) -> str:
    if usfm_book and usfm_book.lang_direction == LangDirEnum.RTL:
        return rtl_direction_html
    else:
        return ltr_direction_html


def tn_language_direction_html(
    tn_book: Optional[TNBook],
    rtl_direction_html: str = settings.RTL_DIRECTION_HTML,
    ltr_direction_html: str = settings.LTR_DIRECTION_HTML,
) -> str:
    if tn_book and tn_book.lang_direction == LangDirEnum.RTL:
        return rtl_direction_html
    else:
        return ltr_direction_html


def tq_language_direction_html(
    tq_book: Optional[TQBook],
    rtl_direction_html: str = settings.RTL_DIRECTION_HTML,
    ltr_direction_html: str = settings.LTR_DIRECTION_HTML,
) -> str:
    if tq_book and tq_book.lang_direction == LangDirEnum.RTL:
        return rtl_direction_html
    else:
        return ltr_direction_html


def bc_language_direction_html(
    bc_book: Optional[BCBook],
    rtl_direction_html: str = settings.RTL_DIRECTION_HTML,
    ltr_direction_html: str = settings.LTR_DIRECTION_HTML,
) -> str:
    if bc_book and bc_book.lang_direction == LangDirEnum.RTL:
        return rtl_direction_html
    else:
        return ltr_direction_html


def tn_chapter_verses(
    tn_book: Optional[TNBook],
    chapter_num: int,
    fmt_str: str = settings.TN_VERSE_NOTES_ENCLOSING_DIV_FMT_STR,
    hr: str = "<hr/>",
) -> str:
    """
    Return the HTML for verses that are in the chapter with
    chapter_num.
    """
    content = []
    if tn_book and chapter_num in tn_book.chapters:
        tn_verses = tn_book.chapters[chapter_num].verses
        content.append(fmt_str.format("".join(tn_verses.values())))
        content.append(hr)
    return "".join(content)


def tq_chapter_verses(
    tq_book: Optional[TQBook],
    chapter_num: int,
    fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
    hr: str = "<hr/>",
) -> str:
    """Return the HTML for verses in chapter_num."""
    content = []
    if tq_book and chapter_num in tq_book.chapters:
        tq_verses = tq_book.chapters[chapter_num].verses
        content.append(
            fmt_str.format(
                tq_book.resource_type_name,
                "".join(tq_verses.values()),
            )
        )
        content.append(hr)
    return "".join(content)


def languages_in_books(usfm_books: Sequence[USFMBook]) -> Sequence[str]:
    """
    Return the distinct languages in the usfm_books.

    """
    language_set = set()
    for book in usfm_books:
        language_set.add(book.lang_code)
    languages = sorted(language_set)
    return languages


def ensure_primary_usfm_books_for_different_languages_are_adjacent(
    usfm_books: Sequence[USFMBook],
) -> Sequence[USFMBook]:
    """
    Interleave/zip USFM book content units such that they are
    juxtaposed language to language in pairs.
    """
    languages = languages_in_books(usfm_books)
    lang0_usfm_books = [
        usfm_book for usfm_book in usfm_books if usfm_book.lang_code == languages[0]
    ]
    # Get book content units for language 1.
    try:
        lang1_usfm_books = [
            usfm_book for usfm_book in usfm_books if usfm_book.lang_code == languages[1]
        ]
    except IndexError as exc:
        logger.debug("Error: %s", exc)
        return lang0_usfm_books
    else:
        return interleave(lang0_usfm_books, lang1_usfm_books)


def interleave(
    lang0_usfm_books: Sequence[USFMBook], lang1_usfm_books: Sequence[USFMBook]
) -> Sequence[USFMBook]:
    """
    Interleave USFM books and then flatten list of tuples into regular flat list
    """
    interleaved = []
    max_len = max(len(lang0_usfm_books), len(lang1_usfm_books))
    for i in range(max_len):
        if i < len(lang0_usfm_books):
            interleaved.append(lang0_usfm_books[i])
        if i < len(lang1_usfm_books):
            interleaved.append(lang1_usfm_books[i])
    return interleaved


if __name__ == "__main__":

    # To run the doctests in the this module, in the root of the project do:
    # python backend/document/domain/resource_lookup.py
    # or
    # python backend/document/domain/resource_lookup.py -v
    # See https://docs.python.org/3/library/doctest.html
    # for more details.
    import doctest

    doctest.testmod()
