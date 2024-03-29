from typing import Iterable, Sequence

from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    adjust_book_intro_headings,
    book_intro,
    chapter_commentary,
    chapter_intro,
    tn_chapter_verses,
    tq_chapter_verses,
)
from document.domain.assembly_strategies_docx.assembly_strategy_utils import (
    add_one_column_section,
    add_two_column_section,
    add_page_break,
    create_docx_subdoc,
)
from document.domain.model import (
    BCBook,
    BookContent,
    HtmlContent,
    LangDirEnum,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
)

from docx import Document  # type: ignore
from htmldocx import HtmlToDocx  # type: ignore
from docxcompose.composer import Composer  # type: ignore

logger = settings.logger(__name__)


def assemble_usfm_by_chapter(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Composer:
    """
    Construct the Docx wherein at least one USFM resource exists, one column
    layout.
    """

    ldebug = logger.debug
    lexception = logger.exception

    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    html_to_docx = HtmlToDocx()
    doc = Document()
    composer = Composer(doc)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        if tn_book_content_unit.book_intro:
            book_intro_ = tn_book_content_unit.book_intro
            book_intro_adj = adjust_book_intro_headings(book_intro_)
            subdoc = create_docx_subdoc(
                book_intro_adj,
                tn_book_content_unit.lang_code,
                tn_book_content_unit
                and tn_book_content_unit.lang_direction == LangDirEnum.RTL,
            )
            composer.append(subdoc)
    for bc_book_content_unit in bc_book_content_units:
        # Add the commentary book intro
        subdoc = create_docx_subdoc(
            "".join(bc_book_content_unit.book_intro), bc_book_content_unit.lang_code
        )
        composer.append(subdoc)

    # Use the usfm_book_content_unit that has the most chapters as a
    # chapter_num pump to realize the most amount of content displayed
    # to the user.
    usfm_with_most_chapters = max(
        usfm_book_content_units,
        key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters.keys(),
    )
    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        add_one_column_section(doc)
        # Add chapter intro for each language
        for tn_book_content_unit2 in tn_book_content_units:
            subdoc = create_docx_subdoc(
                "".join(chapter_intro(tn_book_content_unit2, chapter_num)),
                tn_book_content_unit2.lang_code,
                tn_book_content_unit2
                and tn_book_content_unit2.lang_direction == LangDirEnum.RTL,
            )
            composer.append(subdoc)
        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            subdoc = create_docx_subdoc(
                "".join(chapter_commentary(bc_book_content_unit, chapter_num)),
                bc_book_content_unit.lang_code,
            )
            composer.append(subdoc)
        # Add the interleaved USFM chapters
        for usfm_book_content_unit in usfm_book_content_units:
            if chapter_num in usfm_book_content_unit.chapters:
                add_one_column_section(doc)
                # fmt: off
                is_rtl = usfm_book_content_unit and usfm_book_content_unit.lang_direction == LangDirEnum.RTL
                # fmt: on
                subdoc = create_docx_subdoc(
                    "".join(usfm_book_content_unit.chapters[chapter_num].content),
                    usfm_book_content_unit.lang_code,
                    is_rtl,
                )
                composer.append(subdoc)
                try:
                    chapter_footnotes = usfm_book_content_unit.chapters[
                        chapter_num
                    ].footnotes
                    if chapter_footnotes:
                        add_one_column_section(doc)

                        subdoc = create_docx_subdoc(
                            "{}{}".format(footnotes_heading, chapter_footnotes),
                            usfm_book_content_unit.lang_code,
                            is_rtl,
                        )
                        composer.append(subdoc)
                except KeyError:
                    ldebug(
                        "usfm_book_content_unit: %s, does not have chapter: %s",
                        usfm_book_content_unit,
                        chapter_num,
                    )
                    lexception("Caught exception:")
        # Add the interleaved tn notes
        tn_verses = None
        for tn_book_content_unit3 in tn_book_content_units:
            tn_verses = list(tn_chapter_verses(tn_book_content_unit3, chapter_num))
            if tn_verses:
                add_two_column_section(doc)
                subdoc = create_docx_subdoc(
                    "".join(tn_verses),
                    tn_book_content_unit3.lang_code,
                    tn_book_content_unit3
                    and tn_book_content_unit3.lang_direction == LangDirEnum.RTL,
                )
                composer.append(subdoc)
        # Add the interleaved tq questions
        for tq_book_content_unit in tq_book_content_units:
            tq_verses = list(tq_chapter_verses(tq_book_content_unit, chapter_num))
            # Add TQ verse content, if any
            if tq_verses:
                add_two_column_section(doc)
                subdoc = create_docx_subdoc(
                    "".join(tq_verses),
                    tq_book_content_unit.lang_code,
                    tq_book_content_unit
                    and tq_book_content_unit.lang_direction == LangDirEnum.RTL,
                )
                composer.append(subdoc)

        add_page_break(doc)
    return composer


def assemble_tn_by_chapter(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Composer:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tn_book_content_units exists.
    """

    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    html_to_docx = HtmlToDocx()
    doc = Document()
    composer = Composer(doc)
    add_one_column_section(doc)
    for tn_book_content_unit in tn_book_content_units:
        if tn_book_content_unit.book_intro:
            book_intro_ = tn_book_content_unit.book_intro
            book_intro_adj = adjust_book_intro_headings(book_intro_)
            subdoc = create_docx_subdoc(
                book_intro_adj,
                tn_book_content_unit.lang_code,
                tn_book_content_unit
                and tn_book_content_unit.lang_direction == LangDirEnum.RTL,
            )
            composer.append(subdoc)
    for bc_book_content_unit in bc_book_content_units:
        subdoc = create_docx_subdoc(
            "".join(book_intro(bc_book_content_unit)),
            bc_book_content_unit.lang_code,
        )
        composer.append(subdoc)
    # Use the tn_book_content_unit that has the most chapters as a
    # chapter_num pump to realize the most amount of content displayed
    # to user.
    tn_with_most_chapters = max(
        tn_book_content_units,
        key=lambda tn_book_content_unit: tn_book_content_unit.chapters.keys(),
    )
    for chapter_num in tn_with_most_chapters.chapters.keys():
        add_one_column_section(doc)
        one_column_html = []
        one_column_html.append("Chapter {}".format(chapter_num))
        for tn_book_content_unit in tn_book_content_units:
            # Add the translation notes chapter intro.
            one_column_html.append(
                "".join(chapter_intro(tn_book_content_unit, chapter_num))
            )
            one_column_html_ = "".join(one_column_html)
            if one_column_html_:
                subdoc = create_docx_subdoc(
                    one_column_html_,
                    tn_book_content_unit.lang_code,
                    tn_book_content_unit
                    and tn_book_content_unit.lang_direction == LangDirEnum.RTL,
                )
                composer.append(subdoc)
        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            subdoc = create_docx_subdoc(
                "".join(chapter_commentary(bc_book_content_unit, chapter_num)),
                bc_book_content_unit.lang_code,
            )
            composer.append(subdoc)
        # Add the interleaved tn notes
        for tn_book_content_unit in tn_book_content_units:
            tn_verses = list(tn_chapter_verses(tn_book_content_unit, chapter_num))
            if tn_verses:
                add_two_column_section(doc)
                subdoc = create_docx_subdoc(
                    "".join(tn_verses),
                    tn_book_content_unit.lang_code,
                    tn_book_content_unit
                    and tn_book_content_unit.lang_direction == LangDirEnum.RTL,
                )
                composer.append(subdoc)
        # Add the interleaved tq questions
        for tq_book_content_unit in tq_book_content_units:
            tq_verses = list(tq_chapter_verses(tq_book_content_unit, chapter_num))
            # Add TQ verse content, if any
            if tq_verses:
                add_two_column_section(doc)
                subdoc = create_docx_subdoc(
                    "".join(tq_verses),
                    tq_book_content_unit.lang_code,
                    tq_book_content_unit
                    and tq_book_content_unit.lang_direction == LangDirEnum.RTL,
                )
                composer.append(subdoc)
        add_page_break(doc)
    return composer


def assemble_tq_by_chapter(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    tq_heading_and_questions_fmt_str: str = settings.TQ_HEADING_AND_QUESTIONS_FMT_STR,
) -> Composer:
    """
    Construct the HTML for a 'by chapter' strategy wherein at least
    tq_book_content_units exists.
    """

    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    html_to_docx = HtmlToDocx()
    doc = Document()
    composer = Composer(doc)
    # Use the tq_book_content_unit that has the most chapters as a
    # chapter_num pump to realize the most amount of content displayed to user.
    tq_with_most_chapters = max(
        tq_book_content_units,
        key=lambda tq_book_content_unit: tq_book_content_unit.chapters.keys(),
    )
    for chapter_num in tq_with_most_chapters.chapters.keys():
        one_column_html = []
        one_column_html.append("Chapter {}".format(chapter_num))
        for bc_book_content_unit in bc_book_content_units:
            one_column_html.append(
                "".join(chapter_commentary(bc_book_content_unit, chapter_num))
            )
        if one_column_html:
            add_one_column_section(doc)
            subdoc = create_docx_subdoc(
                "".join(one_column_html), tq_with_most_chapters.lang_code
            )
            composer.append(subdoc)
        # Add the interleaved tq questions
        for tq_book_content_unit in tq_book_content_units:
            tq_verses = list(tq_chapter_verses(tq_book_content_unit, chapter_num))
            if tq_verses:
                add_two_column_section(doc)
                subdoc = create_docx_subdoc(
                    "".join(tq_verses),
                    tq_book_content_unit.lang_code,
                    tq_book_content_unit
                    and tq_book_content_unit.lang_direction == LangDirEnum.RTL,
                )
                composer.append(subdoc)
        add_page_break(doc)
    return composer


def assemble_tw_by_chapter(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Composer:
    """Construct the HTML for BC and TW."""
    html_to_docx = HtmlToDocx()
    doc = Document()
    composer = Composer(doc)

    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)
    for bc_book_content_unit in bc_book_content_units:
        subdoc = create_docx_subdoc(
            bc_book_content_unit.book_intro, bc_book_content_unit.lang_code
        )
        composer.append(subdoc)
        for chapter in bc_book_content_unit.chapters.values():
            subdoc = create_docx_subdoc(
                chapter.commentary, bc_book_content_unit.lang_code
            )
            composer.append(subdoc)
            add_page_break(doc)
    return composer
