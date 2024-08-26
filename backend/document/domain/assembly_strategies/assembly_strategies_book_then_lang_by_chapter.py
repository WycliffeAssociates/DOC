from typing import Mapping, Sequence

from document.domain.bible_books import BOOK_NAMES, BOOK_CHAPTERS
from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    bc_book_intro,
    book_title,
    chapter_commentary,
    chapter_intro,
    ensure_primary_usfm_books_for_different_languages_are_adjacent,
    has_footnotes,
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
from document.utils.number_utils import is_even

logger = settings.logger(__name__)


def assemble_content_by_book_then_lang(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    assembly_layout_kind: AssemblyLayoutEnum,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> str:
    """
    Assemble by book then by language in alphabetic order before
    delegating more atomic ordering/interleaving to an assembly
    sub-strategy.
    """
    content = []
    book_id_map = dict((id, pos) for pos, id in enumerate(BOOK_NAMES.keys()))
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
    for book_code in book_codes_sorted:
        selected_usfm_books = [
            usfm_book for usfm_book in usfm_books if usfm_book.book_code == book_code
        ]
        selected_tn_books = [
            tn_book for tn_book in tn_books if tn_book.book_code == book_code
        ]
        selected_tq_books = [
            tq_book for tq_book in tq_books if tq_book.book_code == book_code
        ]
        selected_tw_books = [
            tw_book for tw_book in tw_books if tw_book.book_code == book_code
        ]
        selected_bc_books = [
            bc_book for bc_book in bc_books if bc_book.book_code == book_code
        ]
        if selected_usfm_books and (
            assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN
            or assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN_COMPACT
        ):
            content.append(
                assemble_usfm_by_chapter(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    selected_tw_books,
                    selected_bc_books,
                )
            )
        elif (
            not selected_usfm_books
            and selected_tn_books
            and (
                assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN
                or assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN_COMPACT
            )
        ):
            content.append(
                assemble_tn_by_chapter(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    selected_tw_books,
                    selected_bc_books,
                )
            )
        elif (
            not selected_usfm_books
            and not selected_tn_books
            and selected_tq_books
            and (
                assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN
                or assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN_COMPACT
            )
        ):
            content.append(
                assemble_tq_by_chapter(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    selected_tw_books,
                    selected_bc_books,
                )
            )
        elif (
            not selected_usfm_books
            and not selected_tn_books
            and not selected_tq_books
            and (selected_tw_books or selected_bc_books)
            and (
                assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN
                or assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN_COMPACT
            )
        ):
            content.append(
                assemble_tw_by_chapter(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    selected_tw_books,
                    selected_bc_books,
                )
            )
        elif selected_usfm_books and (
            assembly_layout_kind
            == AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
            or assembly_layout_kind
            == AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT
        ):
            content.append(
                assemble_usfm_by_chapter_2c_sl_sr(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    selected_tw_books,
                    selected_bc_books,
                )
            )
    return "".join(content)


def assemble_usfm_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
    hr: str = "<hr/>",
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
) -> str:
    """
    Construct the HTML wherein at least one USFM resource exists, one column
    layout.
    """

    content = []

    def sort_key(resource: USFMBook) -> str:
        return resource.lang_code

    def tn_sort_key(resource: TNBook) -> str:
        return resource.lang_code

    def tq_sort_key(resource: TQBook) -> str:
        return resource.lang_code

    def bc_sort_key(resource: BCBook) -> str:
        return resource.lang_code

    usfm_books = sorted(usfm_books, key=sort_key)
    tn_books = sorted(tn_books, key=tn_sort_key)
    tq_books = sorted(tq_books, key=tq_sort_key)
    bc_books = sorted(bc_books, key=bc_sort_key)
    book_codes = {usfm_book.book_code for usfm_book in usfm_books}
    for book_code in book_codes:
        # Content team doesn't want TN book intros: https://github.com/WycliffeAssociates/DOC/issues/121
        # for tn_book in [
        #     tn_book for tn_book in tn_books if tn_book.book_code == book_code
        # ]:
        #     content.append(tn_language_direction_html(tn_book))
        #     book_intro_ = tn_book_intro(tn_book)
        #     book_intro_adj = adjust_book_intro_headings(book_intro_)
        #     content.append(book_intro_adj)
        #     content.append(close_direction_html)
        for bc_book in [
            bc_book for bc_book in bc_books if bc_book.book_code == book_code
        ]:
            content.append(bc_book_intro(bc_book))
        num_chapters = book_chapters[book_code]
        # Add the book title, e.g., 1 Peter
        content.append(book_title(book_code))
        for chapter_num in range(1, num_chapters + 1):
            for usfm_book in [
                usfm_book
                for usfm_book in usfm_books
                if usfm_book.book_code == book_code
            ]:
                if chapter_num in usfm_book.chapters:
                    content.append(usfm_language_direction_html(usfm_book))
                    content.append(usfm_book.chapters[chapter_num].content)
                    content.append(close_direction_html)
                    if not has_footnotes(usfm_book.chapters[chapter_num].content):
                        content.append(hr)
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                if chapter_num in tn_book.chapters:
                    content.append(tn_language_direction_html(tn_book))
                    content.append(chapter_intro(tn_book, chapter_num))
                    content.append(close_direction_html)
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                if chapter_num in bc_book.chapters:
                    content.append(chapter_commentary(bc_book, chapter_num))
            # Add the interleaved tn notes
            tn_verses = None
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                if chapter_num in tn_book.chapters:
                    tn_verses = tn_chapter_verses(tn_book, chapter_num)
                    if tn_verses:
                        content.append(tn_language_direction_html(tn_book))
                        content.append(tn_verses)
                        content.append(close_direction_html)
            tq_verses = None
            for tq_book in [
                tq_book for tq_book in tq_books if tq_book.book_code == book_code
            ]:
                if chapter_num in tq_book.chapters:
                    tq_verses = tq_chapter_verses(tq_book, chapter_num)
                    if tq_verses:
                        content.append(tq_language_direction_html(tq_book))
                        content.append(tq_verses)
                        content.append(close_direction_html)
            content.append(end_of_chapter_html)
    return "".join(content)


def assemble_tn_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
) -> str:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tn_books exists.
    """
    content = []

    def sort_key(resource: TNBook) -> str:
        return resource.lang_code

    def tq_sort_key(resource: TQBook) -> str:
        return resource.lang_code

    def bc_sort_key(resource: BCBook) -> str:
        return resource.lang_code

    tn_books = sorted(tn_books, key=sort_key)
    tq_books = sorted(tq_books, key=tq_sort_key)
    bc_books = sorted(bc_books, key=bc_sort_key)
    book_codes = {tn_book.book_code for tn_book in tn_books}
    for book_code in book_codes:
        # Content team doesn't want TN book intros: https://github.com/WycliffeAssociates/DOC/issues/121
        # Add book intros for each tn_book
        # for tn_book in [
        #     tn_book for tn_book in tn_books if tn_book.book_code == book_code
        # ]:
        #     content.append(tn_language_direction_html(tn_book))
        #     book_intro_ = tn_book_intro(tn_book)
        #     book_intro_adj = adjust_book_intro_headings(book_intro_)
        #     content.append(book_intro_adj)
        #     content.append(close_direction_html)
        for bc_book in [
            bc_book for bc_book in bc_books if bc_book.book_code == book_code
        ]:
            content.append(bc_book_intro(bc_book))
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            content.append("Chapter {}".format(chapter_num))
            # Add chapter intro
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                if chapter_num in tn_book.chapters:
                    content.append(tn_language_direction_html(tn_book))
                    content.append(chapter_intro(tn_book, chapter_num))
                    content.append(close_direction_html)
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                if chapter_num in bc_book.chapters:
                    content.append(chapter_commentary(bc_book, chapter_num))
            # Add tn notes
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                if chapter_num in tn_book.chapters:
                    tn_verses = tn_chapter_verses(tn_book, chapter_num)
                    content.append(tn_language_direction_html(tn_book))
                    content.append(tn_verses)
                    content.append(close_direction_html)
            # Add tq questions
            for tq_book in [
                tq_book for tq_book in tq_books if tq_book.book_code == book_code
            ]:
                if chapter_num in tq_book.chapters:
                    tq_verses = tq_chapter_verses(tq_book, chapter_num)
                    content.append(tq_language_direction_html(tq_book))
                    content.append(tq_verses)
                    content.append(close_direction_html)
            content.append(end_of_chapter_html)
    return "".join(content)


def assemble_tq_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
) -> str:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tq_books exists.
    """
    content = []

    def sort_key(resource: TQBook) -> str:
        return resource.lang_code

    def bc_sort_key(resource: BCBook) -> str:
        return resource.lang_code

    tq_books = sorted(tq_books, key=sort_key)
    bc_books = sorted(bc_books, key=bc_sort_key)
    book_codes = {tq_book.book_code for tq_book in tq_books}
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            content.append("Chapter {}".format(chapter_num))
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                if chapter_num in bc_book.chapters:
                    content.append(chapter_commentary(bc_book, chapter_num))
            for tq_book in [
                tq_book for tq_book in tq_books if tq_book.book_code == book_code
            ]:
                if chapter_num in tq_book.chapters:
                    tq_verses = tq_chapter_verses(tq_book, chapter_num)
                    if tq_verses:
                        content.append(tq_language_direction_html(tq_book))
                        content.append(tq_verses)
                        content.append(close_direction_html)
            content.append(end_of_chapter_html)
    return "".join(content)


# This function could be a little confusing for newcomers. TW lives at
# the language level not the book level, but this function gets invoked
# at the book level due to how the algorithm works. See
# assemble_content_by_book_then_lang above for the conditional that
# invokes it to see the details. At the book level it is almost a noop
# for TW since that is handled elsewhere in
# document_generator.assemble_content.
def assemble_tw_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
) -> str:
    content = []

    def sort_key(resource: BCBook) -> str:
        return resource.lang_code

    bc_books = sorted(bc_books, key=sort_key)
    for bc_book in bc_books:
        content.append(bc_book_intro(bc_book))
        for chapter_num, chapter in bc_book.chapters.items():
            content.append(chapter_commentary(bc_book, chapter_num))
            content.append(end_of_chapter_html)
    return "".join(content)


def assemble_usfm_by_chapter_2c_sl_sr(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    html_row_begin: str = settings.HTML_ROW_BEGIN,
    html_column_begin: str = settings.HTML_COLUMN_BEGIN,
    html_column_left_begin: str = settings.HTML_COLUMN_LEFT_BEGIN,
    html_column_right_begin: str = settings.HTML_COLUMN_RIGHT_BEGIN,
    html_column_end: str = settings.HTML_COLUMN_END,
    html_row_end: str = settings.HTML_ROW_END,
    close_direction_html: str = "</div>",
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
) -> str:
    """
    Construct the HTML for the two column scripture left scripture
    right layout.

    Ensure that different languages' USFMs ends up next to each other
    in the two column layout.

    Discussion:

    First let's find all possible USFM combinations for two languages
    that have both a primary USFM, e.g., ulb, available and a secondary
    USFM, e.g., udb, available for selection:

    primary_lang0, primary_lang1, secondary_lang0, secondary_lang1

    0                 0                0             1
    0                 0                1             0
    0                 0                1             1
    0                 1                0             0
    0                 1                0             1
    0                 1                1             0
    0                 1                1             1
    1                 0                0             0
    1                 0                0             1
    1                 0                1             0
    1                 0                1             1
    1                 1                0             1
    1                 1                1             0
    1                 1                1             1

    of which we can eliminate those that do not have the minimum of
    two languages and eliminate those that do not have USFMs
    for both languages yielding:

    primary_lang0, primary_lang1, secondary_lang0, secondary_lang1

    0                 0                1             1
    0                 1                1             0
    0                 1                1             1
    1                 0                0             1
    1                 0                1             1
    1                 1                0             1
    1                 1                1             0
    1                 1                1             1

    Let's now reorder columns to make the subsequent step easier:

    primary_lang0, secondary_lang0, primary_lang1, secondary_lang1

    0                   1             0              1
    0                   1             1              0
    0                   1             1              1
    1                   0             0              1
    1                   1             0              1
    1                   0             1              1
    1                   1             1              0
    1                   1             1              1

    which yields the following possible USFM layouts when we fix
    that lang0 always appears on the left and lang1 always appears on
    the right of the two column layout:

    secondary_lang0     | secondary_lang1

    or

    secondary_lang0     | primary_lang1

    or

    secondary_lang0     | primary_lang1
                        | secondary_lang1

    or

    primary_lang0       | secondary_lang1

    or

    primary_lang0       | secondary_lang1
    secondary_lang0     |

    or

    primary_lang0       | primary_lang1
                        | secondary_lang1

    or

    primary_lang0       | primary_lang1
    secondary_lang0     |

    or

    primary_lang0       | primary_lang1
    secondary_lang0     | secondary_lang1
    """

    content = []

    def sort_key(resource: USFMBook) -> str:
        return resource.lang_code

    def tn_sort_key(resource: TNBook) -> str:
        return resource.lang_code

    def tq_sort_key(resource: TQBook) -> str:
        return resource.lang_code

    def bc_sort_key(resource: BCBook) -> str:
        return resource.lang_code

    usfm_books = sorted(usfm_books, key=sort_key)
    tn_books = sorted(tn_books, key=tn_sort_key)
    tq_books = sorted(tq_books, key=tq_sort_key)
    bc_books = sorted(bc_books, key=bc_sort_key)
    # Order USFM book content units so that they are in language pairs
    # for side by side display.
    zipped_usfm_books = ensure_primary_usfm_books_for_different_languages_are_adjacent(
        usfm_books
    )
    # Content team doesn't want TN book intros: https://github.com/WycliffeAssociates/DOC/issues/121
    # Add book intros for each tn_book
    # for tn_book in tn_books:
    #     if tn_book.book_intro:
    #         content.append(tn_language_direction_html(tn_book))
    #         book_intro_ = tn_book.book_intro
    #         content.append(adjust_book_intro_headings(book_intro_))
    #         content.append(close_direction_html)
    for bc_book in bc_books:
        content.append(bc_book_intro(bc_book))
    # Get unique book codes in usfm_books
    book_codes = {usfm_book.book_code for usfm_book in usfm_books}
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            content.append(book_title(book_code))
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                if chapter_num in tn_book.chapters:
                    content.append(tn_language_direction_html(tn_book))
                    content.append(chapter_intro(tn_book, chapter_num))
                    content.append(close_direction_html)
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                if chapter_num in bc_book.chapters:
                    content.append(chapter_commentary(bc_book, chapter_num))
            # Get lang_code of first USFM so that we can use it later
            # to make sure USFMs of the same language are on the same
            # side of the two column layout.
            lang0_code = zipped_usfm_books[0].lang_code
            # Add the interleaved USFM verses
            for idx, usfm_book in enumerate(zipped_usfm_books):
                # The conditions for beginning a row are a simple
                # result of the fact that we can have between 2 and 4
                # non-None USFM content units in the collection one of which
                # could be a None (due to an earlier use of
                # itertools.zip_longest in the call to
                # ensure_primary_usfm_books_for_different_languages_are_adjacent)
                # in the case when there are 3 non-None items, but 4
                # total counting the None.
                if is_even(idx) or idx == 3:
                    content.append(html_row_begin)
                if usfm_book and chapter_num in usfm_book.chapters:
                    # lang0's USFM content units should always be on the
                    # left and lang1's should always be on the right.
                    if lang0_code == usfm_book.lang_code:
                        content.append(html_column_left_begin)
                    else:
                        content.append(html_column_right_begin)
                    content.append(usfm_language_direction_html(usfm_book))
                    content.append(usfm_book.chapters[chapter_num].content)
                    content.append(close_direction_html)
                content.append(html_column_end)
                if not is_even(
                    idx
                ):  # Non-even indexes signal the end of the current row.
                    content.append(html_row_end)
            # Add the interleaved tn notes, making sure to put lang0
            # notes on the left and lang1 notes on the right.
            tn_verses = None
            for idx, tn_book in enumerate(tn_books):
                tn_verses = tn_chapter_verses(tn_book, chapter_num)
                if tn_verses:
                    if is_even(idx):
                        content.append(html_row_begin)
                    content.append(html_column_begin)
                    content.append(tn_language_direction_html(tn_book))
                    content.append(tn_verses)
                    content.append(close_direction_html)
                    content.append(html_column_end)
            content.append(html_row_end)
            # Add the interleaved tq questions, making sure to put lang0
            # questions on the left and lang1 questions on the right.
            tq_verses = None
            for idx, tq_book in enumerate(tq_books):
                tq_verses = tq_chapter_verses(tq_book, chapter_num)
                if tq_verses:
                    if is_even(idx):
                        content.append(html_row_begin)
                    content.append(html_column_begin)
                    content.append(tq_language_direction_html(tq_book))
                    content.append(tq_verses)
                    content.append(close_direction_html)
                    content.append(html_column_end)
            content.append(html_row_end)
            content.append(html_row_end)
    return "".join(content)
