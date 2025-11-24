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
from doc.domain.parsing import handle_split_chapter_into_verses
from doc.reviewers_guide.model import RGBook
from doc.utils.list_utils import unique_list_of_strings
from doc.utils.tw_utils import translation_words_for_content


logger = settings.logger(__name__)


def assemble_content_by_book(
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
    show_bc_chapter_commentary: bool,
    book_names: Mapping[str, str] = BOOK_NAMES,
    book_id_map: dict[str, int] = BOOK_ID_MAP,
    resource_type_codes_and_names: Mapping[
        str, str
    ] = settings.RESOURCE_TYPE_CODES_AND_NAMES,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    # Collect and duplicate max number of lang_codes
    lang_codes = list(
        dict.fromkeys(
            [
                *[usfm_book.lang_code for usfm_book in usfm_books],
                *[tn_book.lang_code for tn_book in tn_books],
                *[tq_book.lang_code for tq_book in tq_books],
                *[tw_book.lang_code for tw_book in tw_books],
                *[bc_book.lang_code for bc_book in bc_books],
                *[rg_book.lang_code for rg_book in rg_books],
            ]
        )
    )
    all_book_codes = (
        {usfm_book.book_code for usfm_book in usfm_books}
        .union(tn_book.book_code for tn_book in tn_books)
        .union(tq_book.book_code for tq_book in tq_books)
        .union(bc_book.book_code for bc_book in bc_books)
        .union(rg_book.book_code for rg_book in rg_books)
    )
    book_codes = list(all_book_codes)
    book_codes_sorted = sorted(book_codes, key=lambda book_code: book_id_map[book_code])
    for lang_code in lang_codes:
        for book_code in book_codes_sorted:
            selected_usfm_books = [
                usfm_book
                for usfm_book in usfm_books
                if usfm_book.lang_code == lang_code and usfm_book.book_code == book_code
            ]
            usfm_book = None
            usfm_book2 = None
            if len(selected_usfm_books) == 1:
                usfm_book = selected_usfm_books[0]
            elif (
                len(selected_usfm_books) == 2
            ):  # Second USFM chosen, e.g., fr f10. Assuming f10 should be treated as secondary to ulb for fr
                # TODO Later we might do resources types by clicked order at which point we would likely
                # just use the body of the else clause below.
                if selected_usfm_books[0].resource_type_name in [
                    resource_type_codes_and_names.get("f10", ""),
                    resource_type_codes_and_names.get("udb", ""),
                ]:
                    usfm_book = selected_usfm_books[1]
                    usfm_book2 = selected_usfm_books[0]
                else:
                    usfm_book = selected_usfm_books[0]
                    usfm_book2 = selected_usfm_books[1]
            selected_tn_books = [
                tn_book
                for tn_book in tn_books
                if tn_book.lang_code == lang_code and tn_book.book_code == book_code
            ]
            # TODO en tn and tn-condensed exist, so we need to admit the possibility
            # of two tn_books not just one for en
            tn_book = selected_tn_books[0] if selected_tn_books else None
            selected_tq_books = [
                tq_book
                for tq_book in tq_books
                if tq_book.lang_code == lang_code and tq_book.book_code == book_code
            ]
            tq_book = selected_tq_books[0] if selected_tq_books else None
            selected_tw_books = [
                tw_book for tw_book in tw_books if tw_book.lang_code == lang_code
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
                        show_tn_book_intro,
                        show_bc_book_intro,
                        show_tn_chapter_intro,
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
                        show_tn_book_intro,
                        show_bc_book_intro,
                        show_tn_chapter_intro,
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
                        show_bc_book_intro,
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
                        show_bc_book_intro,
                    )
                )
    return document_parts


def assemble_content_by_verse_book_at_a_time(
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
    show_bc_chapter_commentary: bool,
    show_rg_chapter_commentary: bool,
    book_names: Mapping[str, str] = BOOK_NAMES,
    book_id_map: dict[str, int] = BOOK_ID_MAP,
    resource_type_codes_and_names: Mapping[
        str, str
    ] = settings.RESOURCE_TYPE_CODES_AND_NAMES,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    # Collect and duplicate max number of lang_codes
    lang_codes = list(
        dict.fromkeys(
            [
                *[usfm_book.lang_code for usfm_book in usfm_books],
                *[tn_book.lang_code for tn_book in tn_books],
                *[tq_book.lang_code for tq_book in tq_books],
                *[tw_book.lang_code for tw_book in tw_books],
                *[bc_book.lang_code for bc_book in bc_books],
                *[rg_book.lang_code for rg_book in rg_books],
            ]
        )
    )
    book_codes = list(
        {usfm_book.book_code for usfm_book in usfm_books}
        .union(tn_book.book_code for tn_book in tn_books)
        .union(tq_book.book_code for tq_book in tq_books)
        .union(bc_book.book_code for bc_book in bc_books)
        .union(rg_book.book_code for rg_book in rg_books)
    )
    book_codes_sorted = sorted(book_codes, key=lambda book_code: book_id_map[book_code])
    for lang_code in lang_codes:
        for book_code in book_codes_sorted:
            selected_usfm_books = [
                usfm_book
                for usfm_book in usfm_books
                if usfm_book.lang_code == lang_code and usfm_book.book_code == book_code
            ]
            usfm_book = None
            usfm_book2 = None
            if len(selected_usfm_books) == 1:
                usfm_book = selected_usfm_books[0]
            elif len(selected_usfm_books) == 2:  # Second USFM chosen, e.g., fr f10
                # TODO Later we might do resources types by clicked order at which point we would likely
                # just use the else clause below.
                # Assuming f10 should be treated as secondary to ulb for fr
                if selected_usfm_books[0].resource_type_name in [
                    resource_type_codes_and_names.get("f10", ""),
                    resource_type_codes_and_names.get("udb", ""),
                ]:
                    usfm_book = selected_usfm_books[1]
                    usfm_book2 = selected_usfm_books[0]
                else:
                    usfm_book = selected_usfm_books[0]
                    usfm_book2 = selected_usfm_books[1]
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
                tw_book for tw_book in tw_books if tw_book.lang_code == lang_code
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
            if usfm_book:
                document_parts.extend(
                    assemble_usfm_by_verse_book_at_a_time(
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
                        show_tn_book_intro,
                        show_bc_book_intro,
                        show_tn_chapter_intro,
                        show_bc_chapter_commentary,
                    )
                )
            else:
                document_parts.extend(
                    assemble_content_by_book(
                        usfm_books,
                        tn_books,
                        tq_books,
                        tw_books,
                        bc_books,
                        rg_books,
                        assembly_layout_kind,
                        chunk_size,
                        use_section_visual_separator,
                        use_two_column_layout_for_tn_notes,
                        use_two_column_layout_for_tq_notes,
                        show_tn_book_intro,
                        show_bc_book_intro,
                        show_tn_chapter_intro,
                        show_bc_chapter_commentary,
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
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    fmt_str: str = settings.BOOK_NAME_FMT_STR,
    resource_type_name_fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
    tw_word_list_vertical: bool = settings.TW_WORD_LIST_VERTICAL,
) -> list[DocumentPart]:
    """
    Construct the HTML for a 'by book' strategy wherein at least
    usfm_book_content_unit exists.
    """
    document_parts: list[DocumentPart] = []
    if show_tn_book_intro and tn_book and tn_book.book_intro:
        document_parts.append(
            DocumentPart(
                content=resource_type_name_fmt_str.format(tn_book.resource_type_name),
                is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                use_section_visual_separator=False,
            )
        )
        document_parts.append(
            DocumentPart(
                content=tn_book.book_intro,
                is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                use_section_visual_separator=use_section_visual_separator,
            )
        )
    if show_bc_book_intro and bc_book and bc_book.book_intro:
        document_parts.append(
            DocumentPart(
                content=resource_type_name_fmt_str.format(bc_book.resource_type_name),
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
    if usfm_book:
        is_rtl = usfm_book and usfm_book.lang_direction == LangDirEnum.RTL
        # Add book name
        document_parts.append(
            DocumentPart(
                content=fmt_str.format(usfm_book.national_book_name),
                is_rtl=is_rtl,
                add_hr_p=False,
                use_section_visual_separator=False,
            )
        )
        for (
            chapter_num,
            chapter,
        ) in usfm_book.chapters.items():
            chapter_intro_ = chapter_intro(
                tn_book, chapter_num, use_section_visual_separator
            )
            if chapter_intro_ and tn_book:
                document_parts.append(
                    DocumentPart(
                        content=resource_type_name_fmt_str.format(
                            tn_book.resource_type_name
                        ),
                        is_rtl=usfm_book
                        and usfm_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=chapter_intro_,
                        is_rtl=is_rtl,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            chapter_commentary_ = chapter_commentary(bc_book, chapter_num, False)
            if chapter_commentary_ and bc_book:
                document_parts.append(
                    DocumentPart(
                        content=resource_type_name_fmt_str.format(
                            bc_book.resource_type_name
                        ),
                        is_rtl=usfm_book
                        and usfm_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=chapter_commentary_,
                        is_rtl=is_rtl,
                        # add_hr_p=False,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            document_parts.append(
                DocumentPart(
                    content=resource_type_name_fmt_str.format(
                        usfm_book.resource_type_name
                    ),
                    is_rtl=usfm_book and usfm_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=False,
                )
            )
            document_parts.append(
                DocumentPart(
                    content=chapter.content,
                    is_rtl=is_rtl,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
            if tw_book:
                words = translation_words_for_content(tw_book, chapter.content)
                unique_words = unique_list_of_strings(words)
                if unique_words:
                    document_parts.append(
                        DocumentPart(
                            content=resource_type_name_fmt_str.format(
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
                    document_parts.append(
                        DocumentPart(
                            content=html,
                            is_rtl=tw_book
                            and tw_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=use_section_visual_separator,
                        )
                    )
            tn_verses = tn_chapter_verses(
                tn_book,
                chapter_num,
                False,
                use_two_column_layout_for_tn_notes,
            )
            if tn_book and tn_verses:
                document_parts.append(
                    DocumentPart(
                        content=resource_type_name_fmt_str.format(
                            tn_book.resource_type_name
                        ),
                        is_rtl=usfm_book
                        and usfm_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=tn_verses,
                        is_rtl=is_rtl,
                        contained_in_two_column_section=use_two_column_layout_for_tn_notes,
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
            tq_verses = tq_chapter_verses(
                tq_book,
                chapter_num,
                False,
                use_two_column_layout_for_tq_notes,
            )
            if tq_verses and tq_book:
                document_parts.append(
                    DocumentPart(
                        content=resource_type_name_fmt_str.format(
                            tq_book.resource_type_name
                        ),
                        is_rtl=usfm_book
                        and usfm_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=tq_verses,
                        is_rtl=is_rtl,
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
            rg_verses = rg_chapter_verses(rg_book, chapter_num, False)
            if rg_verses and rg_book:
                document_parts.append(
                    DocumentPart(
                        content=resource_type_name_fmt_str.format(
                            rg_book.resource_type_name
                        ),
                        is_rtl=usfm_book
                        and usfm_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
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
                        content=resource_type_name_fmt_str.format(
                            usfm_book2.resource_type_name
                        ),
                        is_rtl=usfm_book
                        and usfm_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=usfm_book2.chapters[chapter_num].content,
                        is_rtl=usfm_book2
                        and usfm_book2.lang_direction == LangDirEnum.RTL,
                        contained_in_two_column_section=False,
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


def assemble_usfm_by_verse_book_at_a_time(
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
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    show_bc_chapter_commentary: bool,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
    verse_span_fmt_str: str = settings.VERSE_SPAN_FMT_STR,
    tw_word_list_vertical: bool = settings.TW_WORD_LIST_VERTICAL,
    resource_type_codes_and_names: Mapping[
        str, str
    ] = settings.RESOURCE_TYPE_CODES_AND_NAMES,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    if show_tn_book_intro and tn_book and tn_book.book_intro:
        document_parts.append(
            DocumentPart(
                content=fmt_str.format(tn_book.resource_type_name),
                is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                use_section_visual_separator=False,
            )
        )
        document_parts.append(
            DocumentPart(
                content=tn_book.book_intro,
                is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                use_section_visual_separator=use_section_visual_separator,
            )
        )
    if show_bc_book_intro and bc_book and bc_book.book_intro:
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
    if usfm_book:
        for (
            chapter_num,
            chapter,
        ) in usfm_book.chapters.items():
            chapter.verses = handle_split_chapter_into_verses(usfm_book, chapter)
            tn_chapter = tn_book.chapters[chapter_num] if tn_book else None
            tq_chapter = tq_book.chapters[chapter_num] if tq_book else None
            tn_chapter_intro = chapter_intro(tn_book, chapter_num, False)
            if show_tn_chapter_intro and tn_book and tn_chapter_intro:
                document_parts.append(
                    DocumentPart(
                        content=fmt_str.format(tn_book.resource_type_name),
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=tn_chapter_intro,
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            chapter_commentary_ = chapter_commentary(
                bc_book, chapter_num, use_section_visual_separator
            )
            if show_bc_chapter_commentary and bc_book and chapter_commentary_:
                document_parts.append(
                    DocumentPart(
                        content=fmt_str.format(bc_book.resource_type_name),
                        is_rtl=bc_book and bc_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=chapter_commentary_,
                        is_rtl=bc_book and bc_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            rg_verses = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            if rg_book and rg_verses:
                document_parts.append(
                    DocumentPart(
                        content=fmt_str.format(rg_book.resource_type_name),
                        is_rtl=rg_book and rg_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=rg_verses,
                        is_rtl=rg_book and rg_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            if chapter.verses:
                for verse_ref, verse in chapter.verses.items():
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
                            content=fmt_str.format(usfm_book.resource_type_name),
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
                        tn_book
                        and tn_chapter
                        and tn_chapter.verses
                        and verse_ref in tn_chapter.verses
                    ):
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
                                content=tn_chapter.verses[verse_ref],
                                is_rtl=tn_book
                                and tn_book.lang_direction == LangDirEnum.RTL,
                                use_section_visual_separator=use_section_visual_separator,
                            )
                        )
                    if (
                        tq_book
                        and tq_chapter
                        and tq_chapter.verses
                        and verse_ref in tq_chapter.verses
                    ):
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
                                content=tq_chapter.verses[verse_ref],
                                is_rtl=tq_book
                                and tq_book.lang_direction == LangDirEnum.RTL,
                                use_section_visual_separator=use_section_visual_separator,
                            )
                        )
                    if tw_book:
                        words = translation_words_for_content(tw_book, verse)
                        unique_words = unique_list_of_strings(words)
                        if unique_words:
                            document_parts.append(
                                DocumentPart(
                                    content=fmt_str.format(tw_book.resource_type_name),
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
                    # If the user chose two USFM resource types for a language. e.g., fr:
                    # ulb, f10, show the second USFM content here
                    if usfm_book2:
                        usfm_book2_chapter = usfm_book2.chapters[chapter_num]
                        usfm_book2_chapter.verses = handle_split_chapter_into_verses(
                            usfm_book2, usfm_book2_chapter
                        )
                        if usfm_book2_chapter.verses:
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
                            document_parts.append(
                                DocumentPart(
                                    content=verse_span_fmt_str.format(
                                        usfm_book2_chapter.verses[verse_ref]
                                    ),
                                    is_rtl=usfm_book2
                                    and usfm_book2.lang_direction == LangDirEnum.RTL,
                                    use_section_visual_separator=use_section_visual_separator,
                                )
                            )
            # TODO How should we handle footnotes in a versified output?
            # if (
            #     not has_footnotes(chapter.content)
            #     and (
            #         usfm_book2 is not None
            #         or tn_book is not None
            #         or tq_book is not None
            #         or rg_book is not None
            #         or tw_book is not None
            #     )
            #     and use_section_visual_separator
            # ):
            #     content.append(hr)
            # content.append(end_of_chapter_html)
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
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    # show_tn_book_intro: bool = settings.SHOW_TN_BOOK_INTRO,
    resource_type_name_fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    if tn_book:
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
            document_parts.append(
                DocumentPart(
                    content=tn_book.book_intro,
                    is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=use_section_visual_separator,
                )
            )
        if show_bc_book_intro and bc_book and bc_book.book_intro:
            document_parts.append(
                DocumentPart(
                    content=resource_type_name_fmt_str.format(
                        bc_book.resource_type_name
                    ),
                    is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=False,
                )
            )
            document_parts.append(DocumentPart(content=bc_book.book_intro))
        for chapter_num in tn_book.chapters:
            if show_tn_chapter_intro:
                one_column_html = []
                one_column_html.append(chapter_heading(chapter_num))
                one_column_html.append(
                    chapter_intro(tn_book, chapter_num, use_section_visual_separator)
                )
                one_column_html_ = "".join(one_column_html)
                if one_column_html_:
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
                            content=one_column_html_,
                            is_rtl=tn_book
                            and tn_book.lang_direction == LangDirEnum.RTL,
                            use_section_visual_separator=use_section_visual_separator,
                        )
                    )
            chapter_commentary_ = chapter_commentary(
                bc_book, chapter_num, use_section_visual_separator
            )
            if bc_book and chapter_commentary_:
                document_parts.append(
                    DocumentPart(
                        content=resource_type_name_fmt_str.format(
                            bc_book.resource_type_name
                        ),
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=chapter_commentary_,
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
                        content=resource_type_name_fmt_str.format(
                            tn_book.resource_type_name
                        ),
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=tn_verses,
                        is_rtl=tn_book and tn_book.lang_direction == LangDirEnum.RTL,
                        add_hr_p=False,
                        contained_in_two_column_section=use_two_column_layout_for_tn_notes,
                        use_section_visual_separator=False,
                    )
                )
                # document_parts.append(DocumentPart(content=""))
                # This is a trick to make an hr after a two column section by tricking
                # the html to docx parser into keeping this part using an HTML space
                # rather than an empty string.
                document_parts.append(
                    DocumentPart(
                        content="&nbsp;",
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            tq_verses = tq_chapter_verses(
                tq_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tq_notes,
            )
            if tq_book and tq_verses:
                document_parts.append(
                    DocumentPart(
                        content=resource_type_name_fmt_str.format(
                            tq_book.resource_type_name
                        ),
                        is_rtl=tq_book and tq_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=tq_verses,
                        is_rtl=tq_book and tq_book.lang_direction == LangDirEnum.RTL,
                        contained_in_two_column_section=use_two_column_layout_for_tq_notes,
                        use_section_visual_separator=False,
                    )
                )
                # document_parts.append(DocumentPart(content=""))
                # This is a trick to make an hr after a two column section by tricking
                # the html to docx parser into keeping this part using an HTML space
                # rather than an empty string.
                document_parts.append(
                    DocumentPart(
                        content="&nbsp;",
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            rg_verses = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            if rg_book and rg_verses:
                document_parts.append(
                    DocumentPart(
                        content=resource_type_name_fmt_str.format(
                            rg_book.resource_type_name
                        ),
                        is_rtl=rg_book and rg_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=rg_verses,
                        is_rtl=rg_book and rg_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
                # document_parts.append(
                #     DocumentPart(
                #         content="",
                #         use_section_visual_separator=use_section_visual_separator,
                #     )
                # )
            # document_parts.append(
            #     DocumentPart(
            #         content="",
            #         add_hr_p=False,
            #         add_page_break=True,
            #         use_section_visual_separator=use_section_visual_separator,
            #     )
            # )
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
    show_bc_book_intro: bool,
    resource_type_name_fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    if tq_book:
        for chapter_num in tq_book.chapters:

            chapter_commentary_ = chapter_commentary(
                bc_book, chapter_num, use_section_visual_separator
            )
            if bc_book and chapter_commentary_:
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
                        content=chapter_commentary_,
                        use_section_visual_separator=use_section_visual_separator,
                    )
                )
            document_parts.append(
                DocumentPart(
                    content=resource_type_name_fmt_str.format(
                        tq_book.resource_type_name
                    ),
                    is_rtl=tq_book and tq_book.lang_direction == LangDirEnum.RTL,
                    use_section_visual_separator=False,
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
                        content=resource_type_name_fmt_str.format(
                            tq_book.resource_type_name
                        ),
                        is_rtl=tq_book and tq_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=tq_verses,
                        is_rtl=tq_book and tq_book.lang_direction == LangDirEnum.RTL,
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
            rg_verses = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            if rg_book and rg_verses:
                document_parts.append(
                    DocumentPart(
                        content=resource_type_name_fmt_str.format(
                            rg_book.resource_type_name
                        ),
                        is_rtl=rg_book and rg_book.lang_direction == LangDirEnum.RTL,
                        use_section_visual_separator=False,
                    )
                )
                document_parts.append(
                    DocumentPart(
                        content=rg_verses,
                        is_rtl=rg_book and rg_book.lang_direction == LangDirEnum.RTL,
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


def assemble_tw_by_book(
    usfm_book: Optional[USFMBook],
    tn_book: Optional[TNBook],
    tq_book: Optional[TQBook],
    tw_book: Optional[TWBook],
    usfm_book2: Optional[USFMBook],
    bc_book: Optional[BCBook],
    rg_book: Optional[RGBook],
    use_section_visual_separator: bool,
    show_bc_book_intro: bool,
    resource_type_name_fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
) -> list[DocumentPart]:
    document_parts: list[DocumentPart] = []
    if bc_book:
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
            document_parts.append(DocumentPart(content=bc_book.book_intro))
        for chapter in bc_book.chapters.values():
            if chapter.commentary:
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
