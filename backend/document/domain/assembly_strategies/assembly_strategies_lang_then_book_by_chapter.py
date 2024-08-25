from typing import Mapping, Optional, Sequence

from document.domain.bible_books import BOOK_NAMES
from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    bc_book_intro,
    book_title,
    chapter_commentary,
    chapter_heading,
    chapter_intro,
    has_footnotes,
    tn_book_intro,
    tn_chapter_verses,
    tn_language_direction_html,
    tq_chapter_verses,
    tq_language_direction_html,
    usfm_language_direction_html,
)
from document.domain.model import (
    AssemblyLayoutEnum,
    BCBook,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
)

logger = settings.logger(__name__)


def assemble_content_by_lang_then_book(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    assembly_layout_kind: AssemblyLayoutEnum,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> str:
    """
    Assemble by language then by book in lexicographical order before
    delegating more atomic ordering/interleaving to an assembly
    sub-strategy.
    """
    content = []
    # Create map for sorting books in canonical bible book order
    book_id_map = dict((id, pos) for pos, id in enumerate(BOOK_NAMES.keys()))
    # Collect and deduplicate language codes
    all_lang_codes = (
        {usfm_book.lang_code for usfm_book in usfm_books}
        .union(tn_book.lang_code for tn_book in tn_books)
        .union(tq_book.lang_code for tq_book in tq_books)
        .union(tw_book.lang_code for tw_book in tw_books)
        .union(bc_book.lang_code for bc_book in bc_books)
    )
    most_lang_codes = list(all_lang_codes)
    # Collect and deduplicate book codes
    all_book_codes = (
        {usfm_book.book_code for usfm_book in usfm_books}
        .union(tn_book.book_code for tn_book in tn_books)
        .union(tq_book.book_code for tq_book in tq_books)
        .union(tw_book.book_code for tw_book in tw_books)
        .union(bc_book.book_code for bc_book in bc_books)
    )
    most_book_codes = list(all_book_codes)
    # Cache book_id_map lookup
    book_codes_sorted = sorted(
        most_book_codes, key=lambda book_code: book_id_map[book_code]
    )
    for lang_code in most_lang_codes:
        for book_code in book_codes_sorted:
            # logger.debug("lang_code: %s, book_code: %s", lang_code, book_code)
            selected_usfm_books = [
                usfm_book
                for usfm_book in usfm_books
                if usfm_book.lang_code == lang_code and usfm_book.book_code == book_code
            ]
            usfm_book = selected_usfm_books[0] if selected_usfm_books else None
            usfm_book2 = (
                selected_usfm_books[1]
                if selected_usfm_books and len(selected_usfm_books) > 1
                else None
            )
            selected_tn_books = [
                tn_book
                for tn_book in tn_books
                if tn_book.lang_code == lang_code and tn_book.book_code == book_code
            ]
            tn_book = selected_tn_books[0] if selected_tn_books else None
            selected_tq_books = [
                tq_book
                for tq_book in tq_books
                if tq_book.lang_code == lang_code and tq_book.book_code == book_code
            ]
            tq_book = selected_tq_books[0] if selected_tq_books else None
            selected_tw_books = [
                tw_book
                for tw_book in tw_books
                if tw_book.lang_code == lang_code and tw_book.book_code == book_code
            ]
            tw_book = selected_tw_books[0] if selected_tw_books else None
            selected_bc_books = [
                bc_book
                for bc_book in bc_books
                if bc_book.lang_code == lang_code and bc_book.book_code == book_code
            ]
            bc_book = selected_bc_books[0] if selected_bc_books else None
            if usfm_book is not None:
                content.append(
                    assemble_usfm_by_book(
                        usfm_book,
                        tn_book,
                        tq_book,
                        tw_book,
                        usfm_book2,
                        bc_book,
                    )
                )
            elif usfm_book is None and tn_book is not None:
                content.append(
                    assemble_tn_by_book(
                        usfm_book,
                        tn_book,
                        tq_book,
                        tw_book,
                        usfm_book2,
                        bc_book,
                    )
                )
            elif usfm_book is None and tn_book is None and tq_book is not None:
                content.append(
                    assemble_tq_by_book(
                        usfm_book,
                        tn_book,
                        tq_book,
                        tw_book,
                        usfm_book2,
                        bc_book,
                    )
                )
            elif (
                usfm_book is None
                and tn_book is None
                and tq_book is None
                and (tw_book is not None or bc_book is not None)
            ):
                content.append(
                    assemble_tw_by_book(
                        usfm_book,
                        tn_book,
                        tq_book,
                        tw_book,
                        usfm_book2,
                        bc_book,
                    )
                )
    return "".join(content)


def assemble_usfm_by_book(
    usfm_book: Optional[USFMBook],
    tn_book: Optional[TNBook],
    tq_book: Optional[TQBook],
    tw_book: Optional[TWBook],
    usfm_book2: Optional[USFMBook],
    bc_book: Optional[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = "<hr/>",
    close_direction_html: str = "</div>",
) -> str:
    content = []
    content.append(usfm_language_direction_html(usfm_book))
    content.append(tn_book_intro(tn_book))
    content.append(bc_book_intro(bc_book))
    if usfm_book:
        content.append(book_title(usfm_book.book_code))
        for (
            chapter_num,
            chapter,
        ) in usfm_book.chapters.items():
            content.append(chapter.content)
            if not has_footnotes(chapter.content) and (
                usfm_book2 is not None
                or tn_book is not None
                or tq_book is not None
                or tw_book is not None
            ):
                content.append(hr)
            content.append(chapter_intro(tn_book, chapter_num))
            content.append(chapter_commentary(bc_book, chapter_num))
            content.append(tn_chapter_verses(tn_book, chapter_num))
            content.append(tq_chapter_verses(tq_book, chapter_num))
            # If the user chose two USFM resource types for a language. e.g., fr:
            # ulb, f10, show the second USFM content here
            if usfm_book2:
                if chapter_num in usfm_book2.chapters:
                    content.append(usfm_book2.chapters[chapter_num].content)
            content.append(end_of_chapter_html)
    content.append(close_direction_html)
    return "".join(content)


def assemble_tn_by_book(
    usfm_book: Optional[USFMBook],
    tn_book: Optional[TNBook],
    tq_book: Optional[TQBook],
    tw_book: Optional[TWBook],
    usfm_book2: Optional[USFMBook],
    bc_book: Optional[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
) -> str:
    content = []
    content.append(tn_language_direction_html(tn_book))
    content.append(tn_book_intro(tn_book))
    if tn_book:
        for chapter_num in tn_book.chapters:
            content.append(chapter_heading(chapter_num))
            content.append(chapter_intro(tn_book, chapter_num))
            content.append(chapter_commentary(bc_book, chapter_num))
            content.append(tn_chapter_verses(tn_book, chapter_num))
            content.append(tq_chapter_verses(tq_book, chapter_num))
            content.append(end_of_chapter_html)
    content.append(close_direction_html)
    return "".join(content)


def assemble_tq_by_book(
    usfm_book: Optional[USFMBook],
    tn_book: Optional[TNBook],
    tq_book: Optional[TQBook],
    tw_book: Optional[TWBook],
    usfm_book2: Optional[USFMBook],
    bc_book: Optional[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
) -> str:
    content = []
    content.append(tq_language_direction_html(tq_book))
    if tq_book:
        for chapter_num in tq_book.chapters:
            content.append(chapter_commentary(bc_book, chapter_num))
            content.append(chapter_heading(chapter_num))
            content.append(tq_chapter_verses(tq_book, chapter_num))
            content.append(end_of_chapter_html)
    content.append(close_direction_html)
    return "".join(content)


# It is possible to request only TW, however TW is handled at a
# higher level.
def assemble_tw_by_book(
    usfm_book: Optional[USFMBook],
    tn_book: Optional[TNBook],
    tq_book: Optional[TQBook],
    tw_book: Optional[TWBook],
    usfm_book2: Optional[USFMBook],
    bc_book: Optional[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
) -> str:
    content = []
    if bc_book:
        for chapter_num in bc_book.chapters:
            content.append(chapter_commentary(bc_book, chapter_num))
            content.append(end_of_chapter_html)
    return "".join(content)
