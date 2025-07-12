from typing import Mapping, Sequence

from doc.config import settings
from doc.domain.assembly_strategies.assembly_strategy_utils import (
    adjust_book_intro_headings,
    bc_book_intro,
    chapter_commentary,
    chapter_intro,
    rg_chapter_verses,
    tn_chapter_verses,
    tq_chapter_verses,
)
from doc.domain.bible_books import BOOK_CHAPTERS, BOOK_NAMES
from doc.domain.model import (
    AssemblyLayoutEnum,
    BCBook,
    ChunkSizeEnum,
    DocumentPart,
    LangDirEnum,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
)
from doc.reviewers_guide.model import RGBook

logger = settings.logger(__name__)

BOOK_NAME_FMT_STR: str = "<h2 style='text-align: center;'>{}</h2>"


def assemble_content_by_book_then_lang(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    assembly_layout_kind: AssemblyLayoutEnum,
    chunk_size: ChunkSizeEnum,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> list[DocumentPart]:
    """
    Assemble by book then by language in alphabetic order before
    delegating more atomic ordering/interleaving to an assembly
    sub-strategy.
    """
    document_parts: list[DocumentPart] = []
    # Sort the books in canonical order so that groupby does what we want.
    book_id_map = dict((id, pos) for pos, id in enumerate(BOOK_NAMES.keys()))
    most_book_codes = max(
        [
            [usfm_book.book_code for usfm_book in usfm_books],
            [tn_book.book_code for tn_book in tn_books],
            [tq_book.book_code for tq_book in tq_books],
            [tw_book.book_code for tw_book in tw_books],
            [bc_book.book_code for bc_book in bc_books],
            [rg_book.book_code for rg_book in rg_books],
        ],
        key=lambda x: len(x),
    )
    for book_code in sorted(
        most_book_codes,
        key=lambda book_code: book_id_map[book_code],
    ):
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
        selected_rg_books = [
            rg_book for rg_book in rg_books if rg_book.book_code == book_code
        ]
        if selected_usfm_books:
            document_parts = assemble_usfm_by_chapter(
                usfm_books,
                tn_books,
                tq_books,
                tw_books,
                bc_books,
                rg_books,
            )
            return document_parts
        elif not selected_usfm_books and selected_tn_books:
            document_parts = assemble_tn_by_chapter(
                usfm_books,
                tn_books,
                tq_books,
                tw_books,
                bc_books,
                rg_books,
            )
            return document_parts
        elif not selected_usfm_books and not selected_tn_books and selected_tq_books:
            document_parts = assemble_tq_by_chapter(
                usfm_books,
                tn_books,
                tq_books,
                tw_books,
                bc_books,
                rg_books,
            )
            return document_parts
        elif (
            not selected_usfm_books
            and not selected_tn_books
            and not selected_tq_books
            and (selected_tw_books or selected_bc_books or selected_rg_books)
        ):
            document_parts = assemble_tw_by_chapter(
                usfm_books,
                tn_books,
                tq_books,
                tw_books,
                bc_books,
                rg_books,
            )
            return document_parts
    return document_parts


def assemble_usfm_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
    show_tn_book_intro: bool = settings.SHOW_TN_BOOK_INTRO,
    fmt_str: str = BOOK_NAME_FMT_STR,
) -> list[DocumentPart]:
    """
    Construct the Docx wherein at least one USFM resource exists, one column
    layout.
    """

    def sort_key(resource: USFMBook) -> str:
        return resource.lang_code

    def tn_sort_key(resource: TNBook) -> str:
        return resource.lang_code

    def tq_sort_key(resource: TQBook) -> str:
        return resource.lang_code

    def bc_sort_key(resource: BCBook) -> str:
        return resource.lang_code

    def rg_sort_key(resource: RGBook) -> str:
        return resource.lang_code

    usfm_books = sorted(usfm_books, key=sort_key)
    tn_books = sorted(tn_books, key=tn_sort_key)
    tq_books = sorted(tq_books, key=tq_sort_key)
    bc_books = sorted(bc_books, key=bc_sort_key)
    rg_books = sorted(rg_books, key=rg_sort_key)
    document_parts: list[DocumentPart] = []
    if show_tn_book_intro:
        for tn_book in tn_books:
            if tn_book.book_intro:
                book_intro_ = tn_book.book_intro
                book_intro_adj = adjust_book_intro_headings(book_intro_)
                document_parts.append(
                    DocumentPart(
                        content=book_intro_adj,
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                    )
                )
    for bc_book in bc_books:
        document_parts.append(DocumentPart(content=bc_book.book_intro))
    book_codes = {usfm_book.book_code for usfm_book in usfm_books}
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                if chapter_num in tn_book.chapters:
                    document_parts.append(
                        DocumentPart(
                            content=chapter_intro(tn_book, chapter_num),
                            is_rtl=tn_book
                            and tn_book.lang_direction == LangDirEnum.RTL,
                        )
                    )
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                if chapter_num in bc_book.chapters:
                    document_parts.append(
                        DocumentPart(content=chapter_commentary(bc_book, chapter_num))
                    )
            for usfm_book in [
                usfm_book
                for usfm_book in usfm_books
                if usfm_book.book_code == book_code
            ]:
                document_parts.append(
                    DocumentPart(
                        content=fmt_str.format(usfm_book.national_book_name),
                        add_hr_p=False,
                    )
                )
                if chapter_num in usfm_book.chapters:
                    document_parts.append(
                        DocumentPart(
                            content=usfm_book.chapters[chapter_num].content,
                            is_rtl=usfm_book
                            and usfm_book.lang_direction == LangDirEnum.RTL,
                        )
                    )
            tn_verses = None
            for tn_book in [
                tn_book
                for tn_book in tn_books
                if tn_book.book_code == usfm_book.book_code
            ]:
                if chapter_num in tn_book.chapters:
                    tn_verses = tn_chapter_verses(tn_book, chapter_num)
                    if tn_verses:
                        document_parts.append(
                            DocumentPart(
                                content=tn_verses,
                                is_rtl=tn_book
                                and tn_book.lang_direction == LangDirEnum.RTL,
                                contained_in_two_column_section=True,
                            )
                        )
            for tq_book in [
                tq_book
                for tq_book in tq_books
                if tq_book.book_code == usfm_book.book_code
            ]:
                if chapter_num in tq_book.chapters:
                    tq_verses = tq_chapter_verses(tq_book, chapter_num)
                    if tq_verses:
                        document_parts.append(
                            DocumentPart(
                                content=tq_verses,
                                is_rtl=tq_book
                                and tq_book.lang_direction == LangDirEnum.RTL,
                                contained_in_two_column_section=True,
                            )
                        )
            for rg_book in [
                rg_book
                for rg_book in rg_books
                if rg_book.book_code == usfm_book.book_code
            ]:
                if chapter_num in rg_book.chapters:
                    document_parts.append(
                        DocumentPart(content=rg_chapter_verses(rg_book, chapter_num))
                    )
            document_parts.append(
                DocumentPart(content="", add_hr_p=False, add_page_break=True)
            )
    return document_parts


def assemble_tn_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
    show_tn_book_intro: bool = settings.SHOW_TN_BOOK_INTRO,
) -> list[DocumentPart]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tn_book_content_units exists.
    """

    def tn_sort_key(resource: TNBook) -> str:
        return resource.lang_code

    def tq_sort_key(resource: TQBook) -> str:
        return resource.lang_code

    def bc_sort_key(resource: BCBook) -> str:
        return resource.lang_code

    def rg_sort_key(resource: RGBook) -> str:
        return resource.lang_code

    tn_books = sorted(tn_books, key=tn_sort_key)
    tq_books = sorted(tq_books, key=tq_sort_key)
    bc_books = sorted(bc_books, key=bc_sort_key)
    rg_books = sorted(rg_books, key=rg_sort_key)
    document_parts: list[DocumentPart] = []
    if show_tn_book_intro:
        # Add book intros for each tn_book
        for tn_book in tn_books:
            if tn_book.book_intro:
                book_intro_ = tn_book.book_intro
                book_intro_adj = adjust_book_intro_headings(book_intro_)
                document_parts.append(
                    DocumentPart(
                        content=book_intro_adj,
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                    )
                )
    for bc_book in bc_books:
        document_parts.append(DocumentPart(content=bc_book_intro(bc_book)))
    book_codes = {tn_book.book_code for tn_book in tn_books}
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                one_column_html = []
                # one_column_html.append("Chapter {}".format(chapter_num))
                if chapter_num in tn_book.chapters:
                    # Add the translation notes chapter intro.
                    one_column_html.append(chapter_intro(tn_book, chapter_num))
                    one_column_html_ = "".join(one_column_html)
                    if one_column_html_:
                        document_parts.append(
                            DocumentPart(
                                content=one_column_html_,
                                is_rtl=tn_book
                                and tn_book.lang_direction == LangDirEnum.RTL,
                            )
                        )
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                if chapter_num in bc_book.chapters:
                    # Add the chapter commentary.
                    document_parts.append(
                        DocumentPart(content=chapter_commentary(bc_book, chapter_num))
                    )
            # Add the interleaved tn notes
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                if chapter_num in tn_book.chapters:
                    tn_verses = tn_chapter_verses(tn_book, chapter_num)
                    if tn_verses:
                        document_parts.append(
                            DocumentPart(
                                content=tn_verses,
                                is_rtl=tn_book
                                and tn_book.lang_direction == LangDirEnum.RTL,
                            )
                        )
            # Add the interleaved tq questions
            for tq_book in [
                tq_book for tq_book in tq_books if tq_book.book_code == book_code
            ]:
                tq_verses = tq_chapter_verses(tq_book, chapter_num)
                # Add TQ verse content, if any
                if tq_verses:
                    document_parts.append(
                        DocumentPart(
                            content=tq_verses,
                            is_rtl=tq_book
                            and tq_book.lang_direction == LangDirEnum.RTL,
                            contained_in_two_column_section=True,
                        )
                    )
            for rg_book in [
                rg_book for rg_book in rg_books if rg_book.book_code == book_code
            ]:
                rg_verses = rg_chapter_verses(rg_book, chapter_num)
                if rg_verses:
                    document_parts.append(
                        DocumentPart(
                            content=rg_verses,
                            is_rtl=rg_book
                            and rg_book.lang_direction == LangDirEnum.RTL,
                        )
                    )
            document_parts.append(
                DocumentPart(content="", add_hr_p=False, add_page_break=True)
            )
    return document_parts


def assemble_tq_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
) -> list[DocumentPart]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tq_book_content_units exists.
    """

    def tq_sort_key(resource: TQBook) -> str:
        return resource.lang_code

    def bc_sort_key(resource: BCBook) -> str:
        return resource.lang_code

    def rg_sort_key(resource: RGBook) -> str:
        return resource.lang_code

    tq_books = sorted(tq_books, key=tq_sort_key)
    bc_books = sorted(bc_books, key=bc_sort_key)
    rg_books = sorted(rg_books, key=rg_sort_key)
    document_parts: list[DocumentPart] = []
    book_codes = {tq_book.book_code for tq_book in tq_books}
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            one_column_html = []
            one_column_html.append("Chapter {}".format(chapter_num))
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                one_column_html.append(chapter_commentary(bc_book, chapter_num))
            if one_column_html:
                document_parts.append(DocumentPart(content="".join(one_column_html)))
            # Add the interleaved tq questions
            for tq_book in [
                tq_book
                for tq_book in tq_books
                if tq_book.book_code == tq_book.book_code
            ]:
                tq_verses = tq_chapter_verses(tq_book, chapter_num)
                if tq_verses:
                    document_parts.append(
                        DocumentPart(
                            content=tq_verses,
                            is_rtl=tq_book
                            and tq_book.lang_direction == LangDirEnum.RTL,
                            contained_in_two_column_section=True,
                        )
                    )
            for rg_book in [
                rg_book
                for rg_book in rg_books
                if rg_book.book_code == rg_book.book_code
            ]:
                rg_verses = rg_chapter_verses(rg_book, chapter_num)
                if rg_verses:
                    document_parts.append(
                        DocumentPart(
                            content=rg_verses,
                            is_rtl=rg_book
                            and rg_book.lang_direction == LangDirEnum.RTL,
                        )
                    )
            document_parts.append(
                DocumentPart(content="", add_hr_p=False, add_page_break=True)
            )
    return document_parts


# This function could be a little confusing for newcomers. TW lives at
# the language level not the book level, but this function gets invoked
# at the book level due to how the algorithm works. See
# assemble_content_by_book_then_lang above for the conditional that
# invokes it to see the details. At the book level it is almost a noop
# for TW since that is handled elsewhere in
# document_generator.assemble_docx_content.
def assemble_tw_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
) -> list[DocumentPart]:
    """Construct the HTML for BC and TW."""
    document_parts: list[DocumentPart] = []

    def bc_sort_key(resource: BCBook) -> str:
        return resource.lang_code

    def rg_sort_key(resource: RGBook) -> str:
        return resource.lang_code

    bc_books = sorted(bc_books, key=bc_sort_key)
    rg_books = sorted(rg_books, key=rg_sort_key)
    for bc_book in bc_books:
        document_parts.append(DocumentPart(content=bc_book.book_intro))
        for chapter in bc_book.chapters.values():
            document_parts.append(DocumentPart(content=chapter.commentary))
            document_parts.append(
                DocumentPart(content="", add_hr_p=False, add_page_break=True)
            )
    return document_parts
