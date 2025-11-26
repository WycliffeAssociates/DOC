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
from doc.domain.bible_books import BOOK_CHAPTERS, BOOK_ID_MAP, BOOK_NAMES
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
from doc.domain.parsing import handle_split_chapter_into_verses
from doc.reviewers_guide.model import RGBook
from doc.utils.list_utils import unique_list_of_strings
from doc.utils.tw_utils import translation_words_for_content


logger = settings.logger(__name__)


def assemble_content_by_chapter(
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
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    book_names: Mapping[str, str] = BOOK_NAMES,
    book_id_map: dict[str, int] = BOOK_ID_MAP,
) -> list[DocumentPart]:
    """
    Assemble by book in canonical bible book order then by language in
    alphabetic order before delegating more atomic ordering/interleaving
    to an assembly sub-strategy.
    """
    document_parts: list[DocumentPart] = []
    most_book_codes = max(
        [
            [usfm_book.book_code for usfm_book in usfm_books],
            [tn_book.book_code for tn_book in tn_books],
            [tq_book.book_code for tq_book in tq_books],
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
        selected_bc_books = [
            bc_book for bc_book in bc_books if bc_book.book_code == book_code
        ]
        selected_rg_books = [
            rg_book for rg_book in rg_books if rg_book.book_code == book_code
        ]
        if selected_usfm_books:
            document_parts.extend(
                assemble_usfm_by_chapter(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    tw_books,
                    selected_bc_books,
                    selected_rg_books,
                    use_section_visual_separator,
                    use_two_column_layout_for_tn_notes,
                    use_two_column_layout_for_tq_notes,
                    show_tn_book_intro,
                    show_bc_book_intro,
                    show_tn_chapter_intro,
                )
            )
        elif not selected_usfm_books and selected_tn_books:
            document_parts.extend(
                assemble_tn_by_chapter(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    tw_books,
                    selected_bc_books,
                    selected_rg_books,
                    use_section_visual_separator,
                    use_two_column_layout_for_tn_notes,
                    use_two_column_layout_for_tq_notes,
                    show_tn_book_intro,
                    show_bc_book_intro,
                    show_tn_chapter_intro,
                )
            )
        elif not selected_usfm_books and not selected_tn_books and selected_tq_books:
            document_parts.extend(
                assemble_tq_by_chapter(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    tw_books,
                    selected_bc_books,
                    selected_rg_books,
                    use_section_visual_separator,
                    use_two_column_layout_for_tq_notes,
                    show_tn_book_intro,
                    show_bc_book_intro,
                    show_tn_chapter_intro,
                )
            )
        elif (
            not selected_usfm_books
            and not selected_tn_books
            and not selected_tq_books
            and (tw_books or selected_bc_books or selected_rg_books)
        ):
            document_parts.extend(
                assemble_tw_by_chapter(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    tw_books,
                    selected_bc_books,
                    selected_rg_books,
                    use_section_visual_separator,
                    show_bc_book_intro,
                )
            )
    return document_parts


def assemble_content_by_verse_chapter_at_a_time(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    assembly_layout_kind: AssemblyLayoutEnum,
    use_section_visual_separator: bool,
    use_two_column_layout_for_tn_notes: bool,
    use_two_column_layout_for_tq_notes: bool,
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    show_bc_chapter_commentary: bool,
    show_rg_chapter_commentary: bool,
    book_names: Mapping[str, str] = BOOK_NAMES,
    book_id_map: dict[str, int] = BOOK_ID_MAP,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    if usfm_books:
        document_parts.extend(
            assemble_usfm_by_verse_chapter_at_a_time(
                usfm_books,
                tn_books,
                tq_books,
                tw_books,
                bc_books,
                rg_books,
                use_section_visual_separator,
                use_two_column_layout_for_tn_notes,
                use_two_column_layout_for_tq_notes,
                show_tn_book_intro,
                show_bc_book_intro,
                show_tn_chapter_intro,
                show_bc_chapter_commentary,
                show_rg_chapter_commentary,
            )
        )
    else:  # usfm not provided so versification doesn't apply
        document_parts.extend(
            assemble_usfm_by_chapter(
                usfm_books,
                tn_books,
                tq_books,
                tw_books,
                bc_books,
                rg_books,
                use_section_visual_separator,
                use_two_column_layout_for_tn_notes,
                use_two_column_layout_for_tq_notes,
                show_tn_book_intro,
                show_bc_book_intro,
                show_tn_chapter_intro,
                # show_bc_chapter_commentary,
            )
        )
    return document_parts


def assemble_usfm_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    use_section_visual_separator: bool,
    use_two_column_layout_for_tn_notes: bool,
    use_two_column_layout_for_tq_notes: bool,
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
    fmt_str: str = settings.BOOK_NAME_FMT_STR,
    resource_type_name_fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
) -> list[DocumentPart]:
    """
    Construct the Docx wherein at least one USFM resource exists, one column
    layout.
    """
    document_parts: list[DocumentPart] = []
    for tn_book in tn_books:
        if show_tn_book_intro and tn_book.book_intro:
            document_parts.append(
                DocumentPart(
                    content=resource_type_name_fmt_str.format(
                        tn_book.resource_type_name
                    ),
                    is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=False,
                )
            )
            book_intro_adj = adjust_book_intro_headings(tn_book.book_intro)
            document_parts.append(
                DocumentPart(
                    content=book_intro_adj,
                    is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
    for bc_book in bc_books:
        if show_bc_book_intro and bc_book.book_intro:
            document_parts.append(
                DocumentPart(
                    content=resource_type_name_fmt_str.format(
                        bc_book.resource_type_name
                    ),
                    is_rtl=bc_book and bc_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=False,
                )
            )
            document_parts.append(
                DocumentPart(
                    content=bc_book.book_intro,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
    book_codes = {usfm_book.book_code for usfm_book in usfm_books}
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                tn_chapter_intro = chapter_intro(
                    tn_book, chapter_num, use_section_visual_separator
                )
                if show_tn_chapter_intro and tn_chapter_intro:
                    document_parts.append(
                        DocumentPart(
                            content=resource_type_name_fmt_str.format(
                                tn_book.resource_type_name
                            ),
                            is_rtl=tn_book
                            and tn_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=tn_chapter_intro,
                            is_rtl=tn_book
                            and tn_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=use_section_visual_separator,
                        )
                    )
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                chapter_commentary_ = chapter_commentary(
                    bc_book, chapter_num, use_section_visual_separator
                )
                if chapter_commentary_:
                    document_parts.append(
                        DocumentPart(
                            content=resource_type_name_fmt_str.format(
                                bc_book.resource_type_name
                            ),
                            is_rtl=bc_book
                            and bc_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=chapter_commentary_,
                            use_section_visual_separator=use_section_visual_separator,
                        )
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
                        use_section_visual_separator=False,
                    )
                )
                if chapter_num in usfm_book.chapters:
                    document_parts.append(
                        DocumentPart(
                            content=resource_type_name_fmt_str.format(
                                usfm_book.resource_type_name
                            ),
                            is_rtl=usfm_book
                            and usfm_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=usfm_book.chapters[chapter_num].content,
                            is_rtl=usfm_book
                            and usfm_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=use_section_visual_separator,
                        )
                    )
            tn_verses = None
            for tn_book in [
                tn_book
                for tn_book in tn_books
                if tn_book.book_code == usfm_book.book_code
            ]:
                tn_verses = tn_chapter_verses(
                    tn_book,
                    chapter_num,
                    use_section_visual_separator,
                    use_two_column_layout_for_tn_notes,
                )
                if tn_verses:
                    document_parts.append(
                        DocumentPart(
                            content=resource_type_name_fmt_str.format(
                                tn_book.resource_type_name
                            ),
                            is_rtl=tn_book
                            and tn_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=tn_verses,
                            is_rtl=tn_book
                            and tn_book.lang_direction == LangDirEnum.RTL,
                            contained_in_two_column_section=use_two_column_layout_for_tn_notes,
                            add_hr_p=False,
                            use_section_visual_separator=False,
                        )
                    )
                    # This is a trick to make an hr after a two column section by tricking
                    # the html to docx parser into keeping this part using an HTML space
                    # rather than an empty string.
                    document_parts.append(
                        DocumentPart(
                            content="&nbsp;",
                            use_section_visual_separator=use_section_visual_separator,
                        )
                    )
            for tq_book in [
                tq_book
                for tq_book in tq_books
                if tq_book.book_code == usfm_book.book_code
            ]:
                tq_verses = tq_chapter_verses(
                    tq_book,
                    chapter_num,
                    use_section_visual_separator,
                    use_two_column_layout_for_tq_notes,
                )
                if tq_verses:
                    document_parts.append(
                        DocumentPart(
                            content=resource_type_name_fmt_str.format(
                                tq_book.resource_type_name
                            ),
                            is_rtl=tq_book
                            and tq_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=tq_verses,
                            is_rtl=tq_book
                            and tq_book.lang_direction == LangDirEnum.RTL,
                            contained_in_two_column_section=use_two_column_layout_for_tq_notes,
                            use_section_visual_separator=False,
                        )
                    )
                    # This is a trick to make an hr after a two column section by tricking
                    # the html to docx parser into keeping this part using an HTML space
                    # rather than an empty string.
                    document_parts.append(
                        DocumentPart(
                            content="&nbsp;",
                            use_section_visual_separator=use_section_visual_separator,
                        )
                    )
            for rg_book in [
                rg_book
                for rg_book in rg_books
                if rg_book.book_code == usfm_book.book_code
            ]:
                rg_verses = rg_chapter_verses(
                    rg_book, chapter_num, use_section_visual_separator
                )
                if rg_verses:
                    document_parts.append(
                        DocumentPart(
                            content=resource_type_name_fmt_str.format(
                                rg_book.resource_type_name
                            ),
                            is_rtl=rg_book
                            and rg_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=rg_verses,
                            use_section_visual_separator=use_section_visual_separator,
                        ),
                    )
            # document_parts.append(
            #     DocumentPart(
            #         content="",
            #         add_hr_p=False,
            #         add_page_break=True,
            #         use_section_visual_separator=use_section_visual_separator,
            #     )
            # )
    return document_parts


def assemble_usfm_by_verse_chapter_at_a_time(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    use_section_visual_separator: bool,
    use_two_column_layout_for_tn_notes: bool,
    use_two_column_layout_for_tq_notes: bool,
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    show_bc_chapter_commentary: bool,
    show_rg_chapter_commentary: bool,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
    hr: str = settings.HR,
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
    verse_span_fmt_str: str = settings.VERSE_SPAN_FMT_STR,
    tw_word_list_vertical: bool = settings.TW_WORD_LIST_VERTICAL,
    resource_type_codes_and_names: Mapping[
        str, str
    ] = settings.RESOURCE_TYPE_CODES_AND_NAMES,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    lang_codes = list(dict.fromkeys(usfm_book.lang_code for usfm_book in usfm_books))
    for tn_book in tn_books:
        if show_tn_book_intro and tn_book.book_intro:
            book_intro_adj = adjust_book_intro_headings(tn_book.book_intro)
            document_parts.append(
                DocumentPart(
                    content=fmt_str.format(tn_book.resource_type_name),
                    is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=False,
                )
            )
            document_parts.append(
                DocumentPart(
                    content=book_intro_adj,
                    is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
    for bc_book in bc_books:
        if show_bc_book_intro and bc_book.book_intro:
            document_parts.append(
                DocumentPart(
                    content=fmt_str.format(bc_book.resource_type_name),
                    is_rtl=bc_book and bc_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=False,
                )
            )
            document_parts.append(
                DocumentPart(
                    content=bc_book.book_intro,
                    is_rtl=bc_book and bc_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
    book_codes = list(dict.fromkeys(usfm_book.book_code for usfm_book in usfm_books))
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            for lang_code in lang_codes:
                if show_tn_chapter_intro:
                    for tn_book in [
                        tn_book
                        for tn_book in tn_books
                        if tn_book.book_code == book_code
                    ]:
                        tn_chapter_intro = chapter_intro(
                            tn_book,
                            chapter_num,
                            use_section_visual_separator,
                        )
                        if tn_chapter_intro:
                            document_parts.append(
                                DocumentPart(
                                    content=fmt_str.format(tn_book.resource_type_name),
                                    is_rtl=tn_book
                                    and tn_book.lang_direction == LangDirEnum.RTL,
                                    use_section_visual_separator=False,
                                )
                            )
                            document_parts.append(
                                DocumentPart(
                                    content=tn_chapter_intro,
                                    is_rtl=tn_book
                                    and tn_book.lang_direction == LangDirEnum.RTL,
                                    use_section_visual_separator=use_section_visual_separator,
                                )
                            )
                if show_bc_chapter_commentary:
                    for bc_book in [
                        bc_book
                        for bc_book in bc_books
                        if bc_book.book_code == book_code
                    ]:
                        bc_chapter_commentary = chapter_commentary(
                            bc_book, chapter_num, False
                        )
                        if bc_chapter_commentary:
                            document_parts.append(
                                DocumentPart(
                                    content=fmt_str.format(bc_book.resource_type_name),
                                    is_rtl=bc_book
                                    and bc_book.lang_direction == LangDirEnum.RTL,
                                    use_section_visual_separator=False,
                                )
                            )
                            document_parts.append(
                                DocumentPart(
                                    content=bc_chapter_commentary,
                                    is_rtl=bc_book
                                    and bc_book.lang_direction == LangDirEnum.RTL,
                                    use_section_visual_separator=use_section_visual_separator,
                                )
                            )
                if show_rg_chapter_commentary:
                    rg_verses = None
                    for rg_book in [
                        rg_book
                        for rg_book in rg_books
                        if rg_book.book_code == book_code
                    ]:
                        rg_verses = rg_chapter_verses(
                            rg_book, chapter_num, use_section_visual_separator
                        )
                        if rg_verses:
                            document_parts.append(
                                DocumentPart(
                                    content=fmt_str.format(rg_book.resource_type_name),
                                    is_rtl=rg_book
                                    and rg_book.lang_direction == LangDirEnum.RTL,
                                    use_section_visual_separator=False,
                                )
                            )
                            document_parts.append(
                                DocumentPart(
                                    content=rg_verses,
                                    is_rtl=rg_book
                                    and rg_book.lang_direction == LangDirEnum.RTL,
                                    use_section_visual_separator=use_section_visual_separator,
                                )
                            )
                selected_usfm_books = [
                    usfm_book
                    for usfm_book in usfm_books
                    if usfm_book.book_code == book_code
                    and usfm_book.lang_code == lang_code
                ]
                selected_tn_books = [
                    tn_book
                    for tn_book in tn_books
                    if tn_book.book_code == book_code and tn_book.lang_code == lang_code
                ]
                selected_tq_books = [
                    tq_book
                    for tq_book in tq_books
                    if tq_book.book_code == book_code and tq_book.lang_code == lang_code
                ]
                selected_tw_books = [
                    tw_book for tw_book in tw_books if tw_book.lang_code == lang_code
                ]
                usfm_book = None
                usfm_book2 = None
                usfm_chapter = None
                usfm_chapter2 = None
                if len(selected_usfm_books) == 1:
                    usfm_book = selected_usfm_books[0]
                    usfm_chapter = (
                        usfm_book.chapters[chapter_num]
                        if chapter_num in usfm_book.chapters
                        else None
                    )
                elif len(selected_usfm_books) == 2:  # Second USFM chosen, e.g., fr f10
                    # TODO Later we might do resources types by clicked order at which point we would likely
                    # just use the else clause below.
                    # Assuming f10 should be treated as secondary to ulb for fr
                    if selected_usfm_books[0].resource_type_name in [
                        resource_type_codes_and_names.get("f10", ""),
                        resource_type_codes_and_names.get("udb", ""),
                    ]:
                        usfm_book2 = selected_usfm_books[0]
                        usfm_chapter2 = (
                            usfm_book2.chapters[chapter_num]
                            if chapter_num in usfm_book2.chapters
                            else None
                        )
                        usfm_book = selected_usfm_books[1]
                        usfm_chapter = (
                            usfm_book.chapters[chapter_num]
                            if chapter_num in usfm_book.chapters
                            else None
                        )
                    else:
                        usfm_book = selected_usfm_books[0]
                        usfm_chapter = (
                            usfm_book.chapters[chapter_num]
                            if chapter_num in usfm_book.chapters
                            else None
                        )
                        usfm_book2 = selected_usfm_books[1]
                        usfm_chapter2 = (
                            usfm_book2.chapters[chapter_num]
                            if chapter_num in usfm_book2.chapters
                            else None
                        )
                tn_chapter = (
                    selected_tn_books[0].chapters[chapter_num]
                    if selected_tn_books
                    else None
                )
                tq_chapter = (
                    selected_tq_books[0].chapters[chapter_num]
                    if selected_tq_books
                    else None
                )
                if usfm_book and usfm_chapter:
                    usfm_chapter.verses = handle_split_chapter_into_verses(
                        usfm_book, usfm_chapter
                    )
                    document_parts.append(
                        DocumentPart(
                            content=fmt_str.format(usfm_book.resource_type_name),
                            is_rtl=usfm_book
                            and usfm_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    for verse_ref, verse in usfm_chapter.verses.items():
                        document_parts.append(
                            DocumentPart(
                                content=fmt_str.format(
                                    f"{usfm_book.national_book_name} {chapter_num}:{verse_ref}"
                                ),
                                is_rtl=usfm_book
                                and usfm_book.lang_direction == LangDirEnum.RTL,
                                use_section_visual_separator=False,
                            )
                        )
                        document_parts.append(
                            DocumentPart(
                                content=verse_span_fmt_str.format(verse),
                                is_rtl=usfm_book
                                and usfm_book.lang_direction == LangDirEnum.RTL,
                                use_section_visual_separator=use_section_visual_separator,
                            )
                        )
                        if (
                            selected_tn_books
                            and tn_chapter
                            and tn_chapter.verses
                            and verse_ref in tn_chapter.verses
                        ):
                            document_parts.append(
                                DocumentPart(
                                    content=fmt_str.format(
                                        selected_tn_books[0].resource_type_name
                                    ),
                                    is_rtl=selected_tn_books[0]
                                    and selected_tn_books[0].lang_direction
                                    == LangDirEnum.RTL,
                                    use_section_visual_separator=False,
                                )
                            )
                            document_parts.append(
                                DocumentPart(
                                    content=tn_chapter.verses[verse_ref],
                                    is_rtl=selected_tn_books[0]
                                    and selected_tn_books[0].lang_direction
                                    == LangDirEnum.RTL,
                                    use_section_visual_separator=use_section_visual_separator,
                                )
                            )
                        if (
                            selected_tq_books
                            and tq_chapter
                            and tq_chapter.verses
                            and verse_ref in tq_chapter.verses
                        ):
                            document_parts.append(
                                DocumentPart(
                                    content=fmt_str.format(
                                        selected_tq_books[0].resource_type_name
                                    ),
                                    is_rtl=selected_tq_books[0]
                                    and selected_tq_books[0].lang_direction
                                    == LangDirEnum.RTL,
                                    use_section_visual_separator=False,
                                )
                            )
                            document_parts.append(
                                DocumentPart(
                                    content=tq_chapter.verses[verse_ref],
                                    is_rtl=selected_tq_books[0]
                                    and selected_tq_books[0].lang_direction
                                    == LangDirEnum.RTL,
                                    use_section_visual_separator=use_section_visual_separator,
                                )
                            )
                        if selected_tw_books:
                            tw_book = selected_tw_books[0]
                            words = translation_words_for_content(tw_book, verse)
                            unique_words = unique_list_of_strings(words)
                            if unique_words:
                                document_parts.append(
                                    DocumentPart(
                                        content=fmt_str.format(
                                            tw_book.resource_type_name
                                        ),
                                        is_rtl=tw_book
                                        and tw_book.lang_direction == LangDirEnum.RTL,
                                        use_section_visual_separator=False,
                                    )
                                )
                                if tw_word_list_vertical:
                                    html = (
                                        "<ul>\n"
                                        + "\n".join(
                                            [
                                                f"<li><a href='#{tw_book.lang_code}-{word}'>{localized_word}</a></li>"
                                                for localized_word, word in unique_words
                                            ]
                                        )
                                        + "</ul>"
                                    )
                                else:
                                    html = ", ".join(
                                        [
                                            f"<span><a href='#{tw_book.lang_code}-{word}'>{localized_word}</a></span>"
                                            for localized_word, word in unique_words
                                        ]
                                    )
                                logger.debug("tw links html: %s", html)
                                document_parts.append(
                                    DocumentPart(
                                        content=html,
                                        is_rtl=tw_book
                                        and tw_book.lang_direction == LangDirEnum.RTL,
                                        use_section_visual_separator=use_section_visual_separator,
                                    )
                                )
                        if usfm_book2 and usfm_chapter2:
                            document_parts.append(
                                DocumentPart(
                                    content=fmt_str.format(
                                        usfm_book2.resource_type_name
                                    ),
                                    is_rtl=usfm_book2
                                    and usfm_book2.lang_direction == LangDirEnum.RTL,
                                    use_section_visual_separator=False,
                                )
                            )
                            usfm_chapter2.verses = handle_split_chapter_into_verses(
                                usfm_book2, usfm_chapter2
                            )
                            if (
                                usfm_chapter2.verses
                                and verse_ref in usfm_chapter2.verses
                            ):
                                document_parts.append(
                                    DocumentPart(
                                        content=fmt_str.format(
                                            f"{usfm_book2.national_book_name} {chapter_num}:{verse_ref}"
                                        ),
                                        is_rtl=usfm_book2
                                        and usfm_book2.lang_direction
                                        == LangDirEnum.RTL,
                                        use_section_visual_separator=False,
                                    )
                                )
                                document_parts.append(
                                    DocumentPart(
                                        content=verse_span_fmt_str.format(
                                            usfm_chapter2.verses[verse_ref]
                                        ),
                                        is_rtl=usfm_book2
                                        and usfm_book2.lang_direction
                                        == LangDirEnum.RTL,
                                        use_section_visual_separator=use_section_visual_separator,
                                    )
                                )
    return document_parts


def assemble_tn_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    use_section_visual_separator: bool,
    use_two_column_layout_for_tn_notes: bool,
    use_two_column_layout_for_tq_notes: bool,
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
) -> list[DocumentPart]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tn_book_content_units exists.
    """
    document_parts: list[DocumentPart] = []
    if show_tn_book_intro:
        for tn_book in tn_books:
            if tn_book.book_intro:
                book_intro_adj = adjust_book_intro_headings(tn_book.book_intro)
                document_parts.append(
                    DocumentPart(
                        content=fmt_str.format(tn_book.resource_type_name),
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=book_intro_adj,
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
    if show_bc_book_intro:
        for bc_book in bc_books:
            bc_book_intro_ = bc_book_intro(bc_book, use_section_visual_separator)
            if bc_book_intro_:
                document_parts.append(
                    DocumentPart(
                        content=fmt_str.format(bc_book.resource_type_name),
                        is_rtl=bc_book and bc_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=bc_book_intro_,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
    book_codes = {tn_book.book_code for tn_book in tn_books}
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            if show_tn_chapter_intro:
                for tn_book in [
                    tn_book for tn_book in tn_books if tn_book.book_code == book_code
                ]:
                    one_column_html = []
                    if chapter_num in tn_book.chapters:
                        one_column_html.append(
                            chapter_intro(
                                tn_book, chapter_num, use_section_visual_separator
                            )
                        )
                        one_column_html_ = "".join(one_column_html)
                        if one_column_html_:
                            document_parts.append(
                                DocumentPart(
                                    content=fmt_str.format(tn_book.resource_type_name),
                                    is_rtl=tn_book
                                    and tn_book.lang_direction == LangDirEnum.RTL,
                                    use_section_visual_separator=False,
                                )
                            )
                            document_parts.append(
                                DocumentPart(
                                    content=one_column_html_,
                                    is_rtl=tn_book
                                    and tn_book.lang_direction == LangDirEnum.RTL,
                                    use_section_visual_separator=use_section_visual_separator,
                                )
                            )
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                bc_chapter_commentary = chapter_commentary(
                    bc_book, chapter_num, use_section_visual_separator
                )
                if bc_chapter_commentary:
                    document_parts.append(
                        DocumentPart(
                            content=fmt_str.format(bc_book.resource_type_name),
                            is_rtl=bc_book
                            and bc_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=bc_chapter_commentary,
                            use_section_visual_separator=use_section_visual_separator,
                        )
                    )
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                if chapter_num in tn_book.chapters:
                    tn_verses = tn_chapter_verses(
                        tn_book,
                        chapter_num,
                        use_section_visual_separator,
                        use_two_column_layout_for_tn_notes,
                    )
                    if tn_verses:
                        document_parts.append(
                            DocumentPart(
                                content=fmt_str.format(tn_book.resource_type_name),
                                is_rtl=tn_book
                                and tn_book.lang_direction == LangDirEnum.RTL,
                                use_section_visual_separator=False,
                            )
                        )
                        document_parts.append(
                            DocumentPart(
                                content=tn_verses,
                                is_rtl=tn_book
                                and tn_book.lang_direction == LangDirEnum.RTL,
                                contained_in_two_column_section=use_two_column_layout_for_tn_notes,
                                add_hr_p=False,
                                use_section_visual_separator=False,
                            )
                        )
                        # This is a trick to make an hr after a two column section by tricking
                        # the html to docx parser into keeping this part using an HTML space
                        # rather than an empty string.
                        document_parts.append(
                            DocumentPart(
                                content="&nbsp;",
                                use_section_visual_separator=use_section_visual_separator,
                            )
                        )
            for tq_book in [
                tq_book for tq_book in tq_books if tq_book.book_code == book_code
            ]:
                tq_verses = tq_chapter_verses(
                    tq_book,
                    chapter_num,
                    use_section_visual_separator,
                    use_two_column_layout_for_tq_notes,
                )
                if tq_verses:
                    document_parts.append(
                        DocumentPart(
                            content=fmt_str.format(tq_book.resource_type_name),
                            is_rtl=tq_book
                            and tq_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=tq_verses,
                            is_rtl=tq_book
                            and tq_book.lang_direction == LangDirEnum.RTL,
                            contained_in_two_column_section=use_two_column_layout_for_tq_notes,
                            add_hr_p=False,
                            use_section_visual_separator=False,
                        )
                    )
                    # This is a trick to make an hr after a two column section by tricking
                    # the html to docx parser into keeping this part using an HTML space
                    # rather than an empty string.
                    document_parts.append(
                        DocumentPart(
                            content="&nbsp;",
                            use_section_visual_separator=use_section_visual_separator,
                        )
                    )
            for rg_book in [
                rg_book for rg_book in rg_books if rg_book.book_code == book_code
            ]:
                rg_verses = rg_chapter_verses(
                    rg_book, chapter_num, use_section_visual_separator
                )
                if rg_verses:
                    document_parts.append(
                        DocumentPart(
                            content=fmt_str.format(rg_book.resource_type_name),
                            is_rtl=rg_book
                            and rg_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=rg_verses,
                            is_rtl=rg_book
                            and rg_book.lang_direction == LangDirEnum.RTL,
                            contained_in_two_column_section=True,
                            add_hr_p=False,
                            use_section_visual_separator=use_section_visual_separator,
                        )
                    )
            # document_parts.append(
            #     DocumentPart(
            #         content="",
            #         add_hr_p=False,
            #         add_page_break=True,
            #         use_section_visual_separator=use_section_visual_separator,
            #     )
            # )
    return document_parts


def assemble_tq_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    use_section_visual_separator: bool,
    use_two_column_layout_for_tq_notes: bool,
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
) -> list[DocumentPart]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tq_book_content_units exists.
    """
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
                chapter_commentary_ = chapter_commentary(
                    bc_book, chapter_num, use_section_visual_separator
                )
                if chapter_commentary_:
                    document_parts.append(
                        DocumentPart(
                            content=fmt_str.format(bc_book.resource_type_name),
                            is_rtl=bc_book
                            and bc_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    one_column_html.append(chapter_commentary_)
            if one_column_html:
                document_parts.append(DocumentPart(content="".join(one_column_html)))
            for tq_book in [
                tq_book
                for tq_book in tq_books
                if tq_book.book_code == book_code
            ]:
                tq_verses = tq_chapter_verses(
                    tq_book,
                    chapter_num,
                    use_section_visual_separator,
                    use_two_column_layout_for_tq_notes,
                )
                if tq_verses:
                    document_parts.append(
                        DocumentPart(
                            content=fmt_str.format(tq_book.resource_type_name),
                            is_rtl=tq_book
                            and tq_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=tq_verses,
                            is_rtl=tq_book
                            and tq_book.lang_direction == LangDirEnum.RTL,
                            contained_in_two_column_section=use_two_column_layout_for_tq_notes,
                            add_hr_p=False,
                            use_section_visual_separator=False,
                        )
                    )
                    # This is a trick to make an hr after a two column section by tricking
                    # the html to docx parser into keeping this part using an HTML space
                    # rather than an empty string.
                    document_parts.append(
                        DocumentPart(
                            content="&nbsp;",
                            use_section_visual_separator=use_section_visual_separator,
                        )
                    )
            for rg_book in [
                rg_book
                for rg_book in rg_books
                if rg_book.book_code == book_code
            ]:
                rg_verses = rg_chapter_verses(
                    rg_book, chapter_num, use_section_visual_separator
                )
                if rg_verses:
                    document_parts.append(
                        DocumentPart(
                            content=fmt_str.format(rg_book.resource_type_name),
                            is_rtl=rg_book
                            and rg_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=False,
                        )
                    )
                    document_parts.append(
                        DocumentPart(
                            content=rg_verses,
                            is_rtl=rg_book
                            and rg_book.lang_direction == LangDirEnum.RTL,
                        )
                    )
            # document_parts.append(
            #     DocumentPart(content="", add_hr_p=False, add_page_break=True)
            # )
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
    use_section_visual_separator: bool,
    show_bc_book_intro: bool,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
) -> list[DocumentPart]:
    """Construct the HTML for BC and TW."""
    document_parts: list[DocumentPart] = []
    for bc_book in bc_books:
        if show_bc_book_intro and bc_book.book_intro:
            document_parts.append(
                DocumentPart(
                    content=fmt_str.format(bc_book.resource_type_name),
                    is_rtl=bc_book and bc_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=False,
                )
            )
            document_parts.append(
                DocumentPart(
                    content=bc_book.book_intro,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
        for chapter in bc_book.chapters.values():
            document_parts.append(
                DocumentPart(
                    content=chapter.commentary,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
            # document_parts.append(
            #     DocumentPart(
            #         content="",
            #         add_hr_p=False,
            #         add_page_break=True,
            #         use_section_visual_separator=use_section_visual_separator,
            #     )
            # )
    return document_parts
