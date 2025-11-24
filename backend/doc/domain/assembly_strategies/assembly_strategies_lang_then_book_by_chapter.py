from typing import Mapping, Optional, Sequence

from doc.config import settings
from doc.domain.assembly_strategies.assembly_strategy_utils import (
    bc_book_intro,
    chapter_commentary,
    chapter_heading,
    chapter_intro,
    has_footnotes,
    rg_chapter_verses,
    rg_language_direction_html,
    tn_book_intro,
    tn_chapter_verses,
    tn_language_direction_html,
    tq_chapter_verses,
    tq_language_direction_html,
    usfm_language_direction_html,
)
from doc.domain.bible_books import BOOK_ID_MAP, BOOK_NAMES
from doc.domain.model import (
    AssemblyLayoutEnum,
    BCBook,
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
    use_section_visual_separator: bool,
    use_two_column_layout_for_tn_notes: bool,
    use_two_column_layout_for_tq_notes: bool,
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    book_names: Mapping[str, str] = BOOK_NAMES,
    book_id_map: dict[str, int] = BOOK_ID_MAP,
    resource_type_codes_and_names: Mapping[
        str, str
    ] = settings.RESOURCE_TYPE_CODES_AND_NAMES,
) -> list[str]:
    content = []
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
        .union(tw_book.book_code for tw_book in tw_books)
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
            selected_rg_books = [
                rg_book
                for rg_book in rg_books
                if rg_book.lang_code == lang_code and rg_book.book_code == book_code
            ]
            rg_book = selected_rg_books[0] if selected_rg_books else None
            if usfm_book is not None:
                content.extend(
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
                content.extend(
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
                content.extend(
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
                        show_tn_book_intro,
                        show_bc_book_intro,
                        show_tn_chapter_intro,
                    )
                )
            elif (
                usfm_book is None
                and tn_book is None
                and tq_book is None
                and (tw_book is not None or bc_book is not None or rg_book is not None)
            ):
                content.extend(
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
    return content


def assemble_content_by_verse_book_at_a_time(
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
    resource_type_codes_and_names: Mapping[
        str, str
    ] = settings.RESOURCE_TYPE_CODES_AND_NAMES,
) -> list[str]:
    content = []
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
    # Collect and deduplicate book codes
    book_codes = list(
        {usfm_book.book_code for usfm_book in usfm_books}
        .union(tn_book.book_code for tn_book in tn_books)
        .union(tq_book.book_code for tq_book in tq_books)
        .union(tw_book.book_code for tw_book in tw_books)
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
                    logger.info(
                        "inside fr branch for initializing usfm_book and usfm_book2"
                    )
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
            if not usfm_books:
                content.extend(
                    assemble_content_by_book(
                        usfm_books,
                        tn_books,
                        tq_books,
                        tw_books,
                        bc_books,
                        rg_books,
                        assembly_layout_kind,
                        use_section_visual_separator,
                        use_two_column_layout_for_tn_notes,
                        use_two_column_layout_for_tq_notes,
                        show_tn_book_intro,
                        show_bc_book_intro,
                        show_tn_chapter_intro,
                    )
                )
            elif usfm_books and (
                assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN
                or assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN_COMPACT
            ):
                content.extend(
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
                        show_rg_chapter_commentary,
                    )
                )
    return content


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
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = settings.HR,
    close_direction_html: str = "</div>",
    fmt_str: str = settings.BOOK_NAME_FMT_STR,
    resource_type_name_fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
    tw_word_list_vertical: bool = settings.TW_WORD_LIST_VERTICAL,
) -> list[str]:
    content = []
    content.append(usfm_language_direction_html(usfm_book))
    tn_book_intro_ = tn_book_intro(tn_book, use_section_visual_separator)
    if show_tn_book_intro and tn_book and tn_book_intro_:
        content.append(resource_type_name_fmt_str.format(tn_book.resource_type_name))
        content.append(tn_book_intro_)
    bc_book_intro_ = bc_book_intro(bc_book, use_section_visual_separator)
    if show_bc_book_intro and bc_book and bc_book_intro_:
        content.append(resource_type_name_fmt_str.format(bc_book.resource_type_name))
        content.append(bc_book_intro_)
    if usfm_book:
        content.append(fmt_str.format(usfm_book.national_book_name))
        if (
            tn_book is None
            and tq_book is None
            and bc_book is None
            and rg_book is None
            and usfm_book2 is None
        ):
            content.append(
                resource_type_name_fmt_str.format(usfm_book.resource_type_name)
            )
        for (
            chapter_num,
            chapter,
        ) in usfm_book.chapters.items():
            if not (
                tn_book is None
                and tq_book is None
                and bc_book is None
                and rg_book is None
                and usfm_book2 is None
            ):
                content.append(
                    resource_type_name_fmt_str.format(usfm_book.resource_type_name)
                )
            content.append(chapter.content)
            if use_section_visual_separator:
                content.append(hr)
            if tw_book:
                words = translation_words_for_content(tw_book, chapter.content)
                unique_words = unique_list_of_strings(words)
                if unique_words:
                    content.append(
                        resource_type_name_fmt_str.format(tw_book.resource_type_name)
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
                    content.append(html)
            if (
                not has_footnotes(chapter.content)
                and (
                    usfm_book2 is not None
                    or tn_book is not None
                    or tq_book is not None
                    or rg_book is not None
                    or tw_book is not None
                )
                and use_section_visual_separator
            ):
                content.append(hr)
            tn_chapter_intro = chapter_intro(
                tn_book, chapter_num, use_section_visual_separator
            )
            if show_tn_chapter_intro and tn_book and tn_chapter_intro:
                content.append(
                    resource_type_name_fmt_str.format(tn_book.resource_type_name)
                )
                content.append(tn_chapter_intro)
            bc_chapter_commentary = chapter_commentary(
                bc_book, chapter_num, use_section_visual_separator
            )
            if bc_book and bc_chapter_commentary:
                content.append(
                    resource_type_name_fmt_str.format(bc_book.resource_type_name)
                )
                content.append(bc_chapter_commentary)
            tn_verses = tn_chapter_verses(
                tn_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tn_notes,
            )
            if tn_book and tn_verses:
                content.append(
                    resource_type_name_fmt_str.format(tn_book.resource_type_name)
                )
                content.append(tn_verses)
            tq_verses = tq_chapter_verses(
                tq_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tq_notes,
            )
            if tq_book and tq_verses:
                content.append(
                    resource_type_name_fmt_str.format(tq_book.resource_type_name)
                )
                content.append(tq_verses)
            rg_verses = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            if rg_book and rg_verses:
                content.append(
                    resource_type_name_fmt_str.format(rg_book.resource_type_name)
                )
                content.append(rg_verses)
            # If the user chose two USFM resource types for a language. e.g., fr:
            # ulb and f10, then show the second USFM content here
            if usfm_book2:
                if chapter_num in usfm_book2.chapters:
                    content.append(
                        resource_type_name_fmt_str.format(usfm_book2.resource_type_name)
                    )
                    content.append(usfm_book2.chapters[chapter_num].content)
                    if use_section_visual_separator:
                        content.append(hr)
            content.append(end_of_chapter_html)
    content.append(close_direction_html)
    return content


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
    show_rg_chapter_commentary: bool,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    hr: str = settings.HR,
    close_direction_html: str = "</div>",
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
    verse_span_fmt_str: str = settings.VERSE_SPAN_FMT_STR,
    tw_word_list_vertical: bool = settings.TW_WORD_LIST_VERTICAL,
    resource_type_codes_and_names: Mapping[
        str, str
    ] = settings.RESOURCE_TYPE_CODES_AND_NAMES,
) -> list[str]:
    content = []
    content.append(usfm_language_direction_html(usfm_book))
    tn_book_intro_ = tn_book_intro(tn_book, use_section_visual_separator)
    if show_tn_book_intro and tn_book and tn_book_intro_:
        content.append(fmt_str.format(tn_book.resource_type_name))
        content.append(tn_book_intro_)
    bc_book_intro_ = bc_book_intro(bc_book, use_section_visual_separator)
    if show_bc_book_intro and bc_book and bc_book_intro_:
        content.append(fmt_str.format(bc_book.resource_type_name))
        content.append(bc_book_intro_)
    if usfm_book:
        for (
            chapter_num,
            chapter,
        ) in usfm_book.chapters.items():
            chapter.verses = handle_split_chapter_into_verses(usfm_book, chapter)
            tn_chapter = tn_book.chapters[chapter_num] if tn_book else None
            tq_chapter = tq_book.chapters[chapter_num] if tq_book else None
            tn_chapter_intro = chapter_intro(
                tn_book, chapter_num, use_section_visual_separator
            )
            if show_tn_chapter_intro and tn_book and tn_chapter_intro:
                content.append(fmt_str.format(tn_book.resource_type_name))
                content.append(tn_chapter_intro)
            bc_chapter_commentary = chapter_commentary(
                bc_book, chapter_num, use_section_visual_separator
            )
            if show_bc_chapter_commentary and bc_book and bc_chapter_commentary:
                content.append(fmt_str.format(bc_book.resource_type_name))
                content.append(bc_chapter_commentary)
            rg_verses = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            if show_rg_chapter_commentary and rg_book and rg_verses:
                content.append(fmt_str.format(rg_book.resource_type_name))
                content.append(rg_verses)
            if chapter.verses:
                for verse_ref, verse in chapter.verses.items():
                    content.append(
                        fmt_str.format(
                            f"{usfm_book.national_book_name} {chapter_num}:{verse_ref}"
                        )
                    )
                    content.append(fmt_str.format(usfm_book.resource_type_name))
                    content.append(verse_span_fmt_str.format(verse))
                    if (
                        tn_book
                        and tn_chapter
                        and tn_chapter.verses
                        and verse_ref in tn_chapter.verses
                    ):
                        content.append(fmt_str.format(tn_book.resource_type_name))
                        content.append(tn_chapter.verses[verse_ref])
                    if (
                        tq_book
                        and tq_chapter
                        and tq_chapter.verses
                        and verse_ref in tq_chapter.verses
                    ):
                        content.append(fmt_str.format(tq_book.resource_type_name))
                        content.append(tq_chapter.verses[verse_ref])
                    if tw_book:
                        words = translation_words_for_content(tw_book, verse)
                        unique_words = unique_list_of_strings(words)
                        if unique_words:
                            content.append(fmt_str.format(tw_book.resource_type_name))
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
                            content.append(html)
                    # If the user chose two USFM resource types for a language. e.g., fr:
                    # ulb, f10, show the second USFM content here
                    if usfm_book2:
                        usfm_book2_chapter = usfm_book2.chapters[chapter_num]
                        usfm_book2_chapter.verses = handle_split_chapter_into_verses(
                            usfm_book2, usfm_book2_chapter
                        )
                        if usfm_book2_chapter.verses:
                            content.append(
                                fmt_str.format(usfm_book2.resource_type_name)
                            )
                            content.append(
                                verse_span_fmt_str.format(
                                    usfm_book2_chapter.verses[verse_ref]
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
            content.append(end_of_chapter_html)
    content.append(close_direction_html)
    return content


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
    # show_bc_chapter_commentary: bool,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    # show_tn_book_intro: bool = settings.SHOW_TN_BOOK_INTRO,
    # show_tn_chapter_intro: bool = settings.SHOW_TN_CHAPTER_INTRO,
    close_direction_html: str = "</div>",
) -> list[str]:
    content = []
    content.append(tn_language_direction_html(tn_book))
    tn_book_intro_ = tn_book_intro(tn_book, use_section_visual_separator)
    if show_tn_book_intro and tn_book and tn_book_intro_:
        content.append(fmt_str.format(tn_book.resource_type_name))
        content.append(tn_book_intro_)
    if tn_book:
        for chapter_num in tn_book.chapters:
            content.append(chapter_heading(chapter_num))
            tn_chapter_intro_ = chapter_intro(
                tn_book, chapter_num, use_section_visual_separator
            )
            if show_tn_chapter_intro and tn_chapter_intro_:
                content.append(fmt_str.format(tn_book.resource_type_name))
                content.append(tn_chapter_intro_)
            bc_chapter_commentary = chapter_commentary(
                bc_book, chapter_num, use_section_visual_separator
            )
            if bc_book and bc_chapter_commentary:
                content.append(fmt_str.format(bc_book.resource_type_name))
                content.append(bc_chapter_commentary)
            tn_chapter_verses_ = tn_chapter_verses(
                tn_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tn_notes,
            )
            if tn_chapter_verses_:
                content.append(fmt_str.format(tn_book.resource_type_name))
                content.append(tn_chapter_verses_)

            tq_chapter_verses_ = tq_chapter_verses(
                tq_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tq_notes,
            )
            if tq_book and tq_chapter_verses_:
                content.append(fmt_str.format(tq_book.resource_type_name))
                content.append(tq_chapter_verses_)
            rg_chapter_verses_ = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            if rg_book and rg_chapter_verses_:
                content.append(fmt_str.format(rg_book.resource_type_name))
                content.append(rg_chapter_verses_)
                content.append(end_of_chapter_html)
    content.append(close_direction_html)
    return content


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
    show_tn_book_intro: bool,
    show_bc_book_intro: bool,
    show_tn_chapter_intro: bool,
    # show_bc_chapter_commentary: bool,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
) -> list[str]:
    content = []
    content.append(tq_language_direction_html(tq_book))
    if tq_book:
        for chapter_num in tq_book.chapters:

            chapter_commentary_ = chapter_commentary(
                bc_book, chapter_num, use_section_visual_separator
            )
            if bc_book and chapter_commentary_:
                content.append(fmt_str.format(bc_book.resource_type_name))
                content.append(chapter_commentary_)
            content.append(chapter_heading(chapter_num))

            tq_chapter_verses_ = tq_chapter_verses(
                tq_book,
                chapter_num,
                use_section_visual_separator,
                use_two_column_layout_for_tq_notes,
            )
            if tq_chapter_verses_:
                content.append(fmt_str.format(tq_book.resource_type_name))
                content.append(tq_chapter_verses_)
            rg_chapter_verses_ = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            if rg_book and rg_chapter_verses_:
                content.append(fmt_str.format(rg_book.resource_type_name))
                content.append(rg_chapter_verses_)
            content.append(end_of_chapter_html)
    content.append(close_direction_html)
    return content


def assemble_rg_by_chapter(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    use_section_visual_separator: bool,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
) -> list[str]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    rg_books exists.
    """
    content = []

    def bc_sort_key(resource: BCBook) -> str:
        return resource.lang_code

    def rg_sort_key(resource: RGBook) -> str:
        return resource.lang_code

    bc_books = sorted(bc_books, key=bc_sort_key)
    rg_books = sorted(rg_books, key=rg_sort_key)
    for rg_book_ in rg_books:
        for chapter_num, chapter in rg_book_.chapters.items():
            content.append("Chapter {}".format(chapter_num))
            for bc_book in [
                bc_book
                for bc_book in bc_books
                if bc_book.lang_code == rg_book_.lang_code
                and bc_book.book_code == rg_book_.book_code
            ]:

                chapter_commentary_ = chapter_commentary(
                    bc_book, chapter_num, use_section_visual_separator
                )
                if chapter_commentary_:
                    content.append(fmt_str.format(bc_book.resource_type_name))
                    content.append(chapter_commentary_)
            for rg_book in [
                rg_book
                for rg_book in rg_books
                if rg_book.lang_code == rg_book_.lang_code
                and rg_book.book_code == rg_book_.book_code
            ]:
                rg_chapter_verses_ = rg_chapter_verses(
                    rg_book, chapter_num, use_section_visual_separator
                )
                if rg_chapter_verses_:
                    content.append(rg_language_direction_html(rg_book))
                    content.append(fmt_str.format(rg_book.resource_type_name))
                    content.append(rg_chapter_verses_)
                    content.append(close_direction_html)
    return content


# It is possible to request only TW, however TW is handled at a
# higher level.
def assemble_tw_by_book(
    usfm_book: Optional[USFMBook],
    tn_book: Optional[TNBook],
    tq_book: Optional[TQBook],
    tw_book: Optional[TWBook],
    usfm_book2: Optional[USFMBook],
    bc_book: Optional[BCBook],
    rg_book: Optional[RGBook],
    use_section_visual_separator: bool,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
) -> list[str]:
    content = []
    if bc_book:
        for chapter_num in bc_book.chapters:
            chapter_commentary_ = chapter_commentary(
                bc_book, chapter_num, use_section_visual_separator
            )
            if chapter_commentary_:
                # TODO lang direction?
                content.append(fmt_str.format(bc_book.resource_type_name))
                content.append(chapter_commentary_)
                content.append(end_of_chapter_html)
    if rg_book:
        for chapter_num in rg_book.chapters:
            rg_verses = rg_chapter_verses(
                rg_book, chapter_num, use_section_visual_separator
            )
            if rg_verses:
                content.append(fmt_str.format(rg_book.resource_type_name))
                content.append(rg_verses)
                content.append(end_of_chapter_html)
    return content
