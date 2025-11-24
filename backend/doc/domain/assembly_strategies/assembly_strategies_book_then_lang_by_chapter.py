from typing import Mapping, Sequence

from doc.config import settings
from doc.domain.assembly_strategies.assembly_strategy_utils import (
    adjust_book_intro_headings,
    bc_book_intro,
    chapter_commentary,
    chapter_intro,
    ensure_primary_usfm_books_for_different_languages_are_adjacent,
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
from doc.domain.bible_books import BOOK_CHAPTERS, BOOK_ID_MAP, BOOK_NAMES
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
from doc.utils.number_utils import is_even
from doc.utils.tw_utils import translation_words_for_content


logger = settings.logger(__name__)

HTML_ROW_BEGIN: str = "<div class='row'>"
HTML_ROW_END: str = "</div>"
HTML_COLUMN_BEGIN: str = "<div class='column'>"
HTML_COLUMN_END: str = "</div>"
HTML_COLUMN_LEFT_BEGIN: str = "<div class='column-left'>"
HTML_COLUMN_RIGHT_BEGIN: str = "<div class='column-right'>"


def assemble_content_by_chapter(
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
) -> str:
    content = []
    # Collect and duplicate max number of lang_codes
    # Collect and deduplicate book codes
    all_book_codes = list(
        {usfm_book.book_code for usfm_book in usfm_books}
        .union(tn_book.book_code for tn_book in tn_books)
        .union(tq_book.book_code for tq_book in tq_books)
        .union(bc_book.book_code for bc_book in bc_books)
        .union(rg_book.book_code for rg_book in rg_books)
    )
    # Cache book_id_map lookup
    book_codes_sorted = sorted(
        all_book_codes, key=lambda book_code: book_id_map[book_code]
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
        selected_bc_books = [
            bc_book for bc_book in bc_books if bc_book.book_code == book_code
        ]
        selected_rg_books = [
            rg_book for rg_book in rg_books if rg_book.book_code == book_code
        ]
        if selected_usfm_books and (
            assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN
            or assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN_COMPACT
        ):
            content.extend(
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
        elif (
            not selected_usfm_books
            and selected_tn_books
            and (
                assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN
                or assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN_COMPACT
            )
        ):
            content.extend(
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
        elif (
            not selected_usfm_books
            and not selected_tn_books
            and selected_tq_books
            and (
                assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN
                or assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN_COMPACT
            )
        ):
            content.extend(
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
            and (
                assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN
                or assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN_COMPACT
            )
        ):
            content.extend(
                assemble_tw_by_chapter(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    tw_books,
                    selected_bc_books,
                    selected_rg_books,
                    use_section_visual_separator,
                )
            )
        elif selected_usfm_books and (
            assembly_layout_kind
            == AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT
            or assembly_layout_kind
            == AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT
        ):
            content.extend(
                assemble_usfm_by_chapter_2c_sl_sr(
                    selected_usfm_books,
                    selected_tn_books,
                    selected_tq_books,
                    tw_books,
                    selected_bc_books,
                    selected_rg_books,
                    use_section_visual_separator,
                    use_two_column_layout_for_tn_notes,
                    use_two_column_layout_for_tq_notes,
                )
            )
    return "".join(content)


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
) -> str:
    content = []
    if not usfm_books:  # usfm not provided so versification doesn't apply
        content.extend(
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
    elif usfm_books and (
        assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN
        or assembly_layout_kind == AssemblyLayoutEnum.ONE_COLUMN_COMPACT
    ):
        content.extend(
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
    return "".join(content)


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
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
    hr: str = settings.HR,
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
    fmt_str: str = settings.BOOK_NAME_FMT_STR,
    resource_type_name_fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
    tw_word_list_vertical: bool = settings.TW_WORD_LIST_VERTICAL,
) -> list[str]:
    """
    Construct the HTML wherein at least one USFM resource exists, one column
    layout.
    """
    # Collect and duplicate
    content = []
    if show_tn_book_intro:
        for tn_book in tn_books:
            content.append(tn_language_direction_html(tn_book))
            book_intro_ = tn_book_intro(tn_book, use_section_visual_separator)
            book_intro_adj = adjust_book_intro_headings(book_intro_)
            if book_intro_adj:
                content.append(
                    resource_type_name_fmt_str.format(tn_book.resource_type_name)
                )
                content.append(book_intro_adj)
            content.append(close_direction_html)
    if show_bc_book_intro:
        for bc_book in bc_books:
            bc_book_intro_ = bc_book_intro(bc_book, use_section_visual_separator)
            if bc_book_intro_:
                content.append(
                    resource_type_name_fmt_str.format(bc_book.resource_type_name)
                )
                content.append(bc_book_intro_)
    book_codes = {usfm_book.book_code for usfm_book in usfm_books}
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            if show_tn_chapter_intro:
                for tn_book in [
                    tn_book for tn_book in tn_books if tn_book.book_code == book_code
                ]:
                    tn_chapter_intro_ = chapter_intro(
                        tn_book, chapter_num, use_section_visual_separator
                    )
                    if tn_chapter_intro_:
                        content.append(tn_language_direction_html(tn_book))
                        content.append(
                            resource_type_name_fmt_str.format(
                                tn_book.resource_type_name
                            )
                        )
                        content.append(tn_chapter_intro_)
                        content.append(close_direction_html)
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                chapter_commentary_ = chapter_commentary(
                    bc_book, chapter_num, use_section_visual_separator
                )
                if chapter_commentary_:
                    content.append(
                        resource_type_name_fmt_str.format(bc_book.resource_type_name)
                    )
                    content.append(chapter_commentary_)
            for usfm_book in [
                usfm_book
                for usfm_book in usfm_books
                if usfm_book.book_code == book_code
            ]:
                content.append(fmt_str.format(usfm_book.national_book_name))
                if chapter_num in usfm_book.chapters:
                    content.append(usfm_language_direction_html(usfm_book))
                    content.append(
                        resource_type_name_fmt_str.format(usfm_book.resource_type_name)
                    )
                    content.append(usfm_book.chapters[chapter_num].content)
                    content.append(close_direction_html)
                    if (
                        not has_footnotes(usfm_book.chapters[chapter_num].content)
                        and use_section_visual_separator
                    ):
                        content.append(hr)
                    # Add list of tw words used in chapter
                    if tw_books:
                        tw_book = tw_books[0]
                        words = translation_words_for_content(
                            tw_book, usfm_book.chapters[chapter_num].content
                        )
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
                            logger.debug("tw links html: %s", html)
                            content.append(html)
            # Add the interleaved tn notes
            tn_verses = None
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                tn_verses = tn_chapter_verses(
                    tn_book,
                    chapter_num,
                    use_section_visual_separator,
                    use_two_column_layout_for_tn_notes,
                )
                if tn_verses:
                    content.append(tn_language_direction_html(tn_book))
                    content.append(
                        resource_type_name_fmt_str.format(tn_book.resource_type_name)
                    )
                    content.append(tn_verses)
                    content.append(close_direction_html)
            tq_verses = None
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
                    content.append(tq_language_direction_html(tq_book))
                    content.append(
                        resource_type_name_fmt_str.format(tq_book.resource_type_name)
                    )
                    content.append(tq_verses)
                    content.append(close_direction_html)
            rg_verses = None
            for rg_book in [
                rg_book for rg_book in rg_books if rg_book.book_code == book_code
            ]:
                rg_verses = rg_chapter_verses(
                    rg_book, chapter_num, use_section_visual_separator
                )
                if rg_verses:
                    content.append(rg_language_direction_html(rg_book))
                    content.append(rg_verses)
                    content.append(close_direction_html)
        content.append(end_of_chapter_html)
    return content


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
) -> list[str]:
    content = []
    lang_codes = list(dict.fromkeys(usfm_book.lang_code for usfm_book in usfm_books))
    for lang_code in lang_codes:
        if show_tn_book_intro:
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.lang_code == lang_code
            ]:
                content.append(tn_language_direction_html(tn_book))
                book_intro_ = tn_book_intro(tn_book, use_section_visual_separator)
                book_intro_adj = adjust_book_intro_headings(book_intro_)
                if book_intro_adj:
                    content.append(fmt_str.format(tn_book.resource_type_name))
                    content.append(book_intro_adj)
                content.append(close_direction_html)
        if show_bc_book_intro:
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.lang_code == lang_code
            ]:
                bc_book_intro_ = bc_book_intro(bc_book, use_section_visual_separator)
                if bc_book_intro_:
                    content.append(fmt_str.format(bc_book.resource_type_name))
                    content.append(bc_book_intro_)
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
                        and tn_book.lang_code == lang_code
                    ]:
                        chapter_intro_ = chapter_intro(
                            tn_book, chapter_num, use_section_visual_separator
                        )
                        if chapter_intro_:
                            content.append(tn_language_direction_html(tn_book))
                            content.append(fmt_str.format(tn_book.resource_type_name))
                            content.append(chapter_intro_)
                            content.append(close_direction_html)
                if show_bc_chapter_commentary:
                    for bc_book in [
                        bc_book
                        for bc_book in bc_books
                        if bc_book.book_code == book_code
                        and bc_book.lang_code == lang_code
                    ]:
                        chapter_commentary_ = chapter_commentary(
                            bc_book, chapter_num, use_section_visual_separator
                        )
                        if chapter_commentary_:
                            content.append(fmt_str.format(bc_book.resource_type_name))
                            content.append(chapter_commentary_)
                if show_rg_chapter_commentary:
                    rg_verses = None
                    for rg_book in [
                        rg_book
                        for rg_book in rg_books
                        if rg_book.book_code == book_code
                        and rg_book.lang_code == lang_code
                    ]:
                        rg_verses = rg_chapter_verses(
                            rg_book, chapter_num, use_section_visual_separator
                        )
                        if rg_verses:
                            content.append(rg_language_direction_html(rg_book))
                            content.append(fmt_str.format(rg_book.resource_type_name))
                            content.append(rg_verses)
                            content.append(close_direction_html)
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
                    content.append(usfm_language_direction_html(usfm_book))
                    usfm_chapter.verses = handle_split_chapter_into_verses(
                        usfm_book, usfm_chapter
                    )
                    content.append(fmt_str.format(usfm_book.national_book_name))
                    for verse_ref, verse in usfm_chapter.verses.items():
                        content.append(
                            fmt_str.format(
                                f"{usfm_book.national_book_name} {chapter_num}:{verse_ref}"
                            )
                        )
                        content.append(fmt_str.format(usfm_book.resource_type_name))
                        content.append(verse_span_fmt_str.format(verse))
                        if (
                            selected_tn_books
                            and tn_chapter
                            and tn_chapter.verses
                            and verse_ref in tn_chapter.verses
                        ):
                            content.append(
                                fmt_str.format(selected_tn_books[0].resource_type_name)
                            )
                            content.append(tn_chapter.verses[verse_ref])
                        if (
                            selected_tq_books
                            and tq_chapter
                            and tq_chapter.verses
                            and verse_ref in tq_chapter.verses
                        ):
                            content.append(
                                fmt_str.format(selected_tq_books[0].resource_type_name)
                            )
                            content.append(tq_chapter.verses[verse_ref])
                        if selected_tw_books:
                            tw_book = selected_tw_books[0]
                            words = translation_words_for_content(tw_book, verse)
                            unique_words = unique_list_of_strings(words)
                            if unique_words:
                                content.append(
                                    fmt_str.format(tw_book.resource_type_name)
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
                        if usfm_book2 and usfm_chapter2:
                            content.append(
                                fmt_str.format(usfm_book2.resource_type_name)
                            )
                            usfm_chapter2.verses = handle_split_chapter_into_verses(
                                usfm_book2, usfm_chapter2
                            )
                            if (
                                usfm_chapter2.verses
                                and verse_ref in usfm_chapter2.verses
                            ):
                                content.append(
                                    fmt_str.format(
                                        f"{usfm_book2.national_book_name} {chapter_num}:{verse_ref}"
                                    )
                                )
                                content.append(
                                    verse_span_fmt_str.format(
                                        usfm_chapter2.verses[verse_ref]
                                    )
                                )
                content.append(close_direction_html)
            content.append(end_of_chapter_html)
    return content


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
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
) -> list[str]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tn_books exists.
    """
    content = []
    # TODO Should we use lang_codes again here to ensure order?
    if show_tn_book_intro:
        for tn_book in tn_books:
            content.append(tn_language_direction_html(tn_book))
            book_intro_ = tn_book_intro(tn_book, use_section_visual_separator)
            book_intro_adj = adjust_book_intro_headings(book_intro_)
            if book_intro_adj:
                content.append(fmt_str.format(tn_book.resource_type_name))
                content.append(book_intro_adj)
            content.append(close_direction_html)
    if show_bc_book_intro:
        for bc_book in bc_books:
            bc_book_intro_ = bc_book_intro(bc_book, use_section_visual_separator)
            if bc_book_intro_:
                # TODO add lang direction?
                content.append(fmt_str.format(bc_book.resource_type_name))
                content.append(bc_book_intro_)
                # TODO add lang direction close?
    book_codes = {tn_book.book_code for tn_book in tn_books}
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            if show_tn_chapter_intro:
                for tn_book in [
                    tn_book for tn_book in tn_books if tn_book.book_code == book_code
                ]:
                    tn_chapter_intro = chapter_intro(
                        tn_book, chapter_num, use_section_visual_separator
                    )
                    if tn_chapter_intro:
                        content.append(tn_language_direction_html(tn_book))
                        content.append(fmt_str.format(tn_book.resource_type_name))
                        content.append(tn_chapter_intro)
                        content.append(close_direction_html)
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                chapter_commentary_ = chapter_commentary(
                    bc_book, chapter_num, use_section_visual_separator
                )
                if chapter_commentary_:
                    content.append(fmt_str.format(bc_book.resource_type_name))
                    content.append(chapter_commentary_)
            for tn_book in [
                tn_book for tn_book in tn_books if tn_book.book_code == book_code
            ]:
                tn_verses = tn_chapter_verses(
                    tn_book,
                    chapter_num,
                    use_section_visual_separator,
                    use_two_column_layout_for_tn_notes,
                )
                if tn_verses:
                    content.append(tn_language_direction_html(tn_book))
                    content.append(fmt_str.format(tn_book.resource_type_name))
                    content.append(tn_verses)
                    content.append(close_direction_html)
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
                    content.append(tq_language_direction_html(tq_book))
                    content.append(fmt_str.format(tq_book.resource_type_name))
                    content.append(tq_verses)
                    content.append(close_direction_html)
            for rg_book in [
                rg_book for rg_book in rg_books if rg_book.book_code == book_code
            ]:
                rg_verses = rg_chapter_verses(
                    rg_book, chapter_num, use_section_visual_separator
                )
                if rg_verses:
                    content.append(rg_language_direction_html(rg_book))
                    content.append(fmt_str.format(rg_book.resource_type_name))
                    content.append(rg_verses)
                    content.append(close_direction_html)
            content.append(end_of_chapter_html)
    return content


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
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    close_direction_html: str = "</div>",
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
) -> list[str]:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tq_books exists.
    """
    content = []
    book_codes = {tq_book.book_code for tq_book in tq_books}
    for book_code in book_codes:
        num_chapters = book_chapters[book_code]
        for chapter_num in range(1, num_chapters + 1):
            content.append("Chapter {}".format(chapter_num))
            for bc_book in [
                bc_book for bc_book in bc_books if bc_book.book_code == book_code
            ]:
                chapter_commentary_ = chapter_commentary(
                    bc_book, chapter_num, use_section_visual_separator
                )
                if chapter_commentary_:
                    content.append(fmt_str.format(bc_book.resource_type_name))
                    content.append(chapter_commentary_)
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
                    content.append(tq_language_direction_html(tq_book))
                    content.append(fmt_str.format(tq_book.resource_type_name))
                    content.append(tq_verses)
                    content.append(close_direction_html)
            for rg_book in [
                rg_book for rg_book in rg_books if rg_book.book_code == book_code
            ]:
                rg_verses = rg_chapter_verses(
                    rg_book, chapter_num, use_section_visual_separator
                )
                if rg_verses:
                    content.append(rg_language_direction_html(rg_book))
                    content.append(fmt_str.format(rg_book.resource_type_name))
                    content.append(rg_verses)
                    content.append(close_direction_html)
            content.append(end_of_chapter_html)
    return content


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
    rg_books: Sequence[RGBook],
    use_section_visual_separator: bool,
    end_of_chapter_html: str = settings.END_OF_CHAPTER_HTML,
    fmt_str: str = settings.LEFT_ALIGNED_HEADER_FMT_STR,
) -> list[str]:
    content = []
    for bc_book in bc_books:
        content.append(bc_book_intro(bc_book, use_section_visual_separator))
        for chapter_num, chapter in bc_book.chapters.items():

            chapter_commentary_ = chapter_commentary(
                bc_book, chapter_num, use_section_visual_separator
            )
            if chapter_commentary_:
                content.append(fmt_str.format(bc_book.resource_type_name))
                content.append(chapter_commentary_)
            content.append(end_of_chapter_html)
    return content


def assemble_usfm_by_chapter_2c_sl_sr(
    usfm_books: Sequence[USFMBook],
    tn_books: Sequence[TNBook],
    tq_books: Sequence[TQBook],
    tw_books: Sequence[TWBook],
    bc_books: Sequence[BCBook],
    rg_books: Sequence[RGBook],
    use_section_visual_separator: bool,
    use_two_column_layout_for_tn_notes: bool,
    use_two_column_layout_for_tq_notes: bool,
    html_row_begin: str = HTML_ROW_BEGIN,
    html_column_begin: str = HTML_COLUMN_BEGIN,
    html_column_left_begin: str = HTML_COLUMN_LEFT_BEGIN,
    html_column_right_begin: str = HTML_COLUMN_RIGHT_BEGIN,
    html_column_end: str = HTML_COLUMN_END,
    html_row_end: str = HTML_ROW_END,
    close_direction_html: str = "</div>",
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS,
    fmt_str: str = settings.BOOK_NAME_FMT_STR,
    show_tn_book_intro: bool = settings.SHOW_TN_BOOK_INTRO,
) -> list[str]:
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

    # Order USFM book content units so that they are in language pairs
    # for side by side display.
    zipped_usfm_books = ensure_primary_usfm_books_for_different_languages_are_adjacent(
        usfm_books
    )
    # Content team doesn't want TN book intros: https://github.com/WycliffeAssociates/DOC/issues/121
    # Update Dec 6th, 2024: Content team wanted them put back in.
    # Add book intros for each tn_book
    if show_tn_book_intro:
        for tn_book in tn_books:
            if tn_book.book_intro:
                content.append(tn_language_direction_html(tn_book))
                book_intro_ = tn_book.book_intro
                content.append(adjust_book_intro_headings(book_intro_))
                content.append(close_direction_html)
    for bc_book in bc_books:
        content.append(bc_book_intro(bc_book, use_section_visual_separator))
    for usfm_book in usfm_books:
        for chapter_num, chapter in usfm_book.chapters.items():
            content.append(fmt_str.format(usfm_book.national_book_name))
            for tn_book in [
                tn_book
                for tn_book in tn_books
                if tn_book.book_code == usfm_book.book_code
            ]:
                if chapter_num in tn_book.chapters:
                    content.append(tn_language_direction_html(tn_book))
                    content.append(
                        chapter_intro(
                            tn_book, chapter_num, use_section_visual_separator
                        )
                    )
                    content.append(close_direction_html)
            for bc_book in [
                bc_book
                for bc_book in bc_books
                if bc_book.book_code == usfm_book.book_code
            ]:
                if chapter_num in bc_book.chapters:
                    content.append(
                        chapter_commentary(
                            bc_book, chapter_num, use_section_visual_separator
                        )
                    )
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
                tn_verses = tn_chapter_verses(
                    tn_book,
                    chapter_num,
                    use_section_visual_separator,
                    use_two_column_layout_for_tn_notes,
                )
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
                tq_verses = tq_chapter_verses(
                    tq_book,
                    chapter_num,
                    use_section_visual_separator,
                    use_two_column_layout_for_tq_notes,
                )
                if tq_verses:
                    if is_even(idx):
                        content.append(html_row_begin)
                    content.append(html_column_begin)
                    content.append(tq_language_direction_html(tq_book))
                    content.append(tq_verses)
                    content.append(close_direction_html)
                    content.append(html_column_end)
            for idx, rg_book in enumerate(
                [
                    rg_book
                    for rg_book in rg_books
                    if rg_book.book_code == usfm_book.book_code
                ]
            ):
                rg_verses = rg_chapter_verses(
                    rg_book, chapter_num, use_section_visual_separator
                )
                if rg_verses:
                    if is_even(idx):
                        content.append(html_row_begin)
                    content.append(html_column_begin)
                    content.append(rg_language_direction_html(rg_book))
                    content.append(rg_verses)
                    content.append(close_direction_html)
                    content.append(html_column_end)
            content.append(html_row_end)
            content.append(html_row_end)
    return content
