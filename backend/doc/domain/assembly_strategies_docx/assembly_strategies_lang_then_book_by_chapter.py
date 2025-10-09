from typing import Mapping, Optional, Sequence

from doc.config import settings
from doc.domain.assembly_strategies.assembly_strategy_utils import (
    chapter_heading,
    chapter_commentary,
    chapter_intro,
    rg_chapter_verses,
    tn_chapter_verses,
    tq_chapter_verses,
)
from doc.domain.bible_books import BOOK_ID_MAP, BOOK_NAMES
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


def assemble_content_by_lang_then_book(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    assembly_layout_kind: AssemblyLayoutEnum,
    chunk_size: ChunkSizeEnum,
    use_section_visual_separator: bool,
    use_two_column_layout_for_tn_notes: bool,
    use_two_column_layout_for_tq_notes: bool,
    book_names: Mapping[str, str] = BOOK_NAMES,
    book_id_map: dict[str, int] = BOOK_ID_MAP,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    all_lang_codes = (
        {usfm_book.lang_code for usfm_book in usfm_books}
        .union(tn_book.lang_code for tn_book in tn_books)
        .union(tq_book.lang_code for tq_book in tq_books)
        .union(tw_book.lang_code for tw_book in tw_books)
        .union(bc_book.lang_code for bc_book in bc_books)
        .union(rg_book.lang_code for rg_book in rg_books)
    )
    most_lang_codes = list(all_lang_codes)
    all_book_codes = (
        {usfm_book.book_code for usfm_book in usfm_books}
        .union(tn_book.book_code for tn_book in tn_books)
        .union(tq_book.book_code for tq_book in tq_books)
        .union(tw_book.book_code for tw_book in tw_books)
        .union(bc_book.book_code for bc_book in bc_books)
        .union(rg_book.book_code for rg_book in rg_books)
    )
    most_book_codes = list(all_book_codes)
    book_codes_sorted = sorted(
        most_book_codes, key=lambda book_code: book_id_map[book_code]
    )
    for lang_code in most_lang_codes:
        for book_code in book_codes_sorted:
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
            # TODO TWBook doesn't really need to have a book_code attribute
            # because TW resources are language centric not book centric.
            # We could do something about that later if desired for
            # design cleanness sake.
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
            selected_rg_books = [
                rg_book
                for rg_book in rg_books
                if rg_book.lang_code == lang_code and rg_book.book_code == book_code
            ]
            rg_book = selected_rg_books[0] if selected_rg_books else None
            if usfm_book is not None:
                document_parts.extend(
                    assemble_usfm_by_book(
                        usfm_book,
                        tn_book,
                        tq_book,
                        tw_book,
                        usfm_book2,
                        bc_book,
                        rg_book,
                        use_section_visual_separator,
                        use_two_column_layout_for_tn_notes,
                        use_two_column_layout_for_tq_notes,
                    )
                )
            elif usfm_book is None and tn_book is not None:
                document_parts.extend(
                    assemble_tn_by_book(
                        usfm_book,
                        tn_book,
                        tq_book,
                        tw_book,
                        usfm_book2,
                        bc_book,
                        rg_book,
                        use_section_visual_separator,
                        use_two_column_layout_for_tn_notes,
                        use_two_column_layout_for_tq_notes,
                    )
                )
            elif usfm_book is None and tn_book is None and tq_book is not None:
                document_parts.extend(
                    assemble_tq_by_book(
                        usfm_book,
                        tn_book,
                        tq_book,
                        tw_book,
                        usfm_book2,
                        bc_book,
                        rg_book,
                        use_section_visual_separator,
                        use_two_column_layout_for_tq_notes,
                    )
                )
            elif (
                usfm_book is None
                and tn_book is None
                and tq_book is None
                and (tw_book is not None or bc_book is not None or rg_book is not None)
            ):
                document_parts.extend(
                    assemble_tw_by_book(
                        usfm_book,
                        tn_book,
                        tq_book,
                        tw_book,
                        usfm_book2,
                        bc_book,
                        rg_book,
                        use_section_visual_separator,
                    )
                )
    return document_parts


def assemble_usfm_by_book(
    usfm_book: Optional[USFMBook],
    tn_book: Optional[TNBook],
    tq_book: Optional[TQBook],
    tw_book: Optional[TWBook],
    usfm_book2: Optional[USFMBook],
    bc_book: Optional[BCBook],
    rg_book: Optional[RGBook],
    use_section_visual_separator: bool,
    use_two_column_layout_for_tn_notes: bool,
    use_two_column_layout_for_tq_notes: bool,
    show_tn_book_intro: bool = settings.SHOW_TN_BOOK_INTRO,
    fmt_str: str = settings.BOOK_NAME_FMT_STR,
) -> list[DocumentPart]:
    """
    Construct the HTML for a 'by book' strategy wherein at least
    usfm_book_content_unit exists.
    """
    document_parts: list[DocumentPart] = []
    if show_tn_book_intro and tn_book and tn_book.book_intro:
        document_parts.append(
            DocumentPart(
                content=tn_book.book_intro,
                is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                use_section_visual_separator=use_section_visual_separator,
            )
        )
    if bc_book:
        if bc_book.book_intro:
            document_parts.append(
                DocumentPart(
                    content=bc_book.book_intro,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
    if usfm_book:
        is_rtl = usfm_book and usfm_book.lang_direction == LangDirEnum.RTL
        # Add book name
        document_parts.append(
            DocumentPart(
                content=fmt_str.format(usfm_book.national_book_name),
                is_rtl=is_rtl,
                add_hr_p=False,
                use_section_visual_separator=use_section_visual_separator,
            )
        )
        for (
            chapter_num,
            chapter,
        ) in usfm_book.chapters.items():
            tn_verses: str = ""
            tq_verses: str = ""
            rg_verses: str = ""
            chapter_intro_ = ""
            chapter_commentary_ = ""
            chapter_intro_ = chapter_intro(
                tn_book, chapter_num, use_section_visual_separator
            )
            tn_verses = tn_chapter_verses(
                tn_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tn_notes,
            )
            chapter_commentary_ = chapter_commentary(
                bc_book, chapter_num, use_section_visual_separator
            )
            tq_verses = tq_chapter_verses(
                tq_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tq_notes,
            )
            rg_verses = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            document_parts.append(
                DocumentPart(
                    content=chapter.content,
                    is_rtl=is_rtl,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
            if chapter_intro_:
                document_parts.append(
                    DocumentPart(
                        content=chapter_intro_,
                        is_rtl=is_rtl,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            if chapter_commentary_:
                document_parts.append(
                    DocumentPart(
                        content=chapter_commentary_,
                        is_rtl=is_rtl,
                        add_hr_p=False,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            if tn_verses:
                document_parts.append(
                    DocumentPart(
                        content=tn_verses,
                        is_rtl=is_rtl,
                        add_hr_p=False,
                        contained_in_two_column_section=use_two_column_layout_for_tn_notes,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content="",
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            if tq_verses:
                document_parts.append(
                    DocumentPart(
                        content=tq_verses,
                        is_rtl=is_rtl,
                        add_hr_p=False,
                        contained_in_two_column_section=use_two_column_layout_for_tq_notes,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content="",
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            if rg_verses:
                document_parts.append(
                    DocumentPart(
                        content=rg_verses,
                        is_rtl=is_rtl,
                        add_hr_p=False,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            if usfm_book2:
                document_parts.append(
                    DocumentPart(
                        content=usfm_book2.chapters[chapter_num].content,
                        is_rtl=usfm_book2
                        and usfm_book2.lang_direction == LangDirEnum.RTL,
                        contained_in_two_column_section=False,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            document_parts.append(
                DocumentPart(
                    content="",
                    add_hr_p=False,
                    add_page_break=True,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
    return document_parts


def assemble_tn_by_book(
    usfm_book: Optional[USFMBook],
    tn_book: Optional[TNBook],
    tq_book: Optional[TQBook],
    tw_book: Optional[TWBook],
    usfm_book2: Optional[USFMBook],
    bc_book: Optional[BCBook],
    rg_book: Optional[RGBook],
    use_section_visual_separator: bool,
    use_two_column_layout_for_tn_notes: bool,
    use_two_column_layout_for_tq_notes: bool,
    show_tn_book_intro: bool = settings.SHOW_TN_BOOK_INTRO,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    if tn_book:
        if show_tn_book_intro and tn_book.book_intro:
            document_parts.append(
                DocumentPart(
                    content=tn_book.book_intro,
                    is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
        if bc_book and bc_book.book_intro:
            document_parts.append(DocumentPart(content=bc_book.book_intro))
        for chapter_num in tn_book.chapters:
            one_column_html = []
            one_column_html.append(chapter_heading(chapter_num))
            one_column_html.append(
                chapter_intro(tn_book, chapter_num, use_section_visual_separator)
            )
            one_column_html_ = "".join(one_column_html)
            if one_column_html_:
                document_parts.append(
                    DocumentPart(
                        content=one_column_html_,
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            if bc_book:
                document_parts.append(
                    DocumentPart(
                        content=chapter_commentary(
                            bc_book, chapter_num, use_section_visual_separator
                        ),
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            tn_verses = tn_chapter_verses(
                tn_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tn_notes,
            )
            if tn_verses:
                document_parts.append(
                    DocumentPart(
                        content=tn_verses,
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                        add_hr_p=False,
                        contained_in_two_column_section=use_two_column_layout_for_tn_notes,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
                document_parts.append(DocumentPart(content=""))
            tq_verses = tq_chapter_verses(
                tq_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tq_notes,
            )
            if tq_book and tq_verses:
                document_parts.append(
                    DocumentPart(
                        content=tq_verses,
                        is_rtl=tq_book and tq_book.lang_direction == LangDirEnum.RTL,
                        contained_in_two_column_section=use_two_column_layout_for_tq_notes,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
                document_parts.append(DocumentPart(content=""))
            rg_verses = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            if rg_book and rg_verses:
                document_parts.append(
                    DocumentPart(
                        content=rg_verses,
                        is_rtl=rg_book and rg_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content="",
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            document_parts.append(
                DocumentPart(
                    content="",
                    add_hr_p=False,
                    add_page_break=True,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
    return document_parts


def assemble_tq_by_book(
    usfm_book: Optional[USFMBook],
    tn_book: Optional[TNBook],
    tq_book: Optional[TQBook],
    tw_book: Optional[TWBook],
    usfm_book2: Optional[USFMBook],
    bc_book: Optional[BCBook],
    rg_book: Optional[RGBook],
    use_section_visual_separator: bool,
    use_two_column_layout_for_tq_notes: bool,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    if tq_book:
        for chapter_num in tq_book.chapters:
            if bc_book:
                document_parts.append(
                    DocumentPart(
                        content=chapter_commentary(
                            bc_book, chapter_num, use_section_visual_separator
                        ),
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            document_parts.append(
                DocumentPart(
                    content=chapter_heading(chapter_num),
                    is_rtl=tq_book and tq_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
            tq_verses = tq_chapter_verses(
                tq_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tq_notes,
            )
            if tq_verses:
                document_parts.append(
                    DocumentPart(
                        content=tq_verses,
                        is_rtl=tq_book and tq_book.lang_direction == LangDirEnum.RTL,
                        contained_in_two_column_section=use_two_column_layout_for_tq_notes,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            rg_verses = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            if rg_book and rg_verses:
                document_parts.append(
                    DocumentPart(
                        content=rg_verses,
                        is_rtl=rg_book and rg_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            document_parts.append(
                DocumentPart(
                    content="",
                    add_hr_p=False,
                    add_page_break=True,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
    return document_parts


def assemble_tw_by_book(
    usfm_book: Optional[USFMBook],
    tn_book: Optional[TNBook],
    tq_book: Optional[TQBook],
    tw_book: Optional[TWBook],
    usfm_book2: Optional[USFMBook],
    bc_book: Optional[BCBook],
    rg_book: Optional[RGBook],
    use_section_visual_separator: bool,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    if bc_book:
        document_parts.append(DocumentPart(content=bc_book.book_intro))
        for chapter in bc_book.chapters.values():
            document_parts.append(
                DocumentPart(
                    content=chapter.commentary,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
            document_parts.append(
                DocumentPart(
                    content="",
                    add_hr_p=False,
                    add_page_break=True,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
    return document_parts
