from itertools import groupby
from re import sub
from typing import Callable, Iterable, Mapping, Optional

from document.config import settings
from document.domain.assembly_strategies.assembly_strategy_utils import (
    bc_book_content_unit,
    book_content_unit_lang_name,
    book_content_unit_resource_code,
    book_intro_commentary,
    book_number,
    chapter_commentary,
    chapter_intro,
    first_usfm_book_content_unit,
    second_usfm_book_content_unit,
    tn_book_content_unit,
    tq_book_content_unit,
    translation_word_links,
    tw_book_content_unit,
    verses_for_chapter_tn,
    verses_for_chapter_tq,
)
from document.domain.bible_books import BOOK_NAMES, BOOK_NUMBERS
from document.domain.model import (
    AssemblyLayoutEnum,
    BCBook,
    BookContent,
    ChunkSizeEnum,
    HtmlContent,
    TNBook,
    TQBook,
    TWBook,
    USFMBook,
    VerseRef,
)

logger = settings.logger(__name__)


def assemble_by_usfm_as_iterator_by_chapter_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML wherein at least one USFM resource (e.g., ulb,
    nav, cuv, etc.) exists, and TN, TQ, TW, and a second USFM (e.g.,
    probably always udb) may exist. If only one USFM exists then it will
    be used as the first USFM resource even if it is of udb resource type.
    Non-USFM resources, e.g., TN, TQ, and TW will reference (and link
    where applicable) the first USFM resource. The second USFM resource is
    displayed last in this interleaving strategy.
    """

    if tn_book_content_unit:
        yield tn_book_content_unit.intro_html

    if bc_book_content_unit:
        yield book_intro_commentary(bc_book_content_unit)

    if usfm_book_content_unit:
        for (
            chapter_num,
            chapter,
        ) in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading
            tn_verses: Optional[dict[VerseRef, HtmlContent]] = None
            tq_verses: Optional[dict[VerseRef, HtmlContent]] = None
            if tn_book_content_unit:
                # Add the translation notes chapter intro.
                yield chapter_intro(tn_book_content_unit, chapter_num)
                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            if bc_book_content_unit:
                yield chapter_commentary(bc_book_content_unit, chapter_num)
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM chapter with its translation notes, translation
            # questions, and translation words if available.
            yield "".join(chapter.content)
            # Here we return the whole chapter's worth of verses for the secondary usfm
            if usfm_book_content_unit2:
                yield "".join(usfm_book_content_unit2.chapters[chapter_num].content)

            # Add TN verse content, if any
            if tn_book_content_unit and tn_verses is not None and tn_verses:
                yield "".join(tn_verses.values())
            # yield from format_tn_verse(
            #     tn_book_content_unit,
            #     chapter_num,
            #     verse_num,
            #     tn_verses[verse_num],
            # )
            # Add TQ verse content, if any
            if tq_book_content_unit and tq_verses:
                yield "".join(tq_verses.values())
                # yield from format_tq_verse(
                #     tq_book_content_unit.resource_type_name,
                #     chapter_num,
                #     verse_num,
                #     tq_verses[verse_num],
                # )

            # TODO
            # if tw_book_content_unit:
            #     # Add the translation words links section.
            #     yield from translation_word_links(
            #         tw_book_content_unit,
            #         chapter_num,
            #         verse_num,
            #         verse,
            #     )

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes

    if not usfm_book_content_unit and usfm_book_content_unit2:
        # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
        for (
            chapter_num_,
            chapter_,
        ) in usfm_book_content_unit2.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter_.content[0]
            yield chapter_heading
            # Now let's interleave USFM chapter verses
            yield "".join(chapter_.content)
