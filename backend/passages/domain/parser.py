from typing import Mapping

from doc.config import settings
from doc.domain.bible_books import BOOK_CHAPTER_VERSES
from doc.domain.model import USFMBook
from doc.domain.parsing import lookup_verse_text
from passages.domain.model import BibleReference


logger = settings.logger(__name__)


def verse_text_html(
    bible_reference: BibleReference,
    usfm_book: USFMBook,
    book_chapter_verses: Mapping[str, Mapping[str, str]] = BOOK_CHAPTER_VERSES,
) -> str:
    verse_text = []
    if (
        bible_reference.end_chapter
        and bible_reference.end_chapter > 0
        and bible_reference.end_chapter_verse_ref
    ):  # chapter boundary traversal
        start_chapter_lower_verse = int(bible_reference.start_chapter_verse_ref)
        start_chapter_upper_verse = int(
            book_chapter_verses[bible_reference.book_code][
                str(bible_reference.start_chapter)
            ]
        )
        for idx in range(start_chapter_lower_verse, start_chapter_upper_verse + 1):
            start_chapter_verse_text = lookup_verse_text(
                usfm_book,
                bible_reference.start_chapter,
                str(idx),
            )
            if start_chapter_verse_text:
                verse_text.append(
                    f'<span class="verse"><sup class="versemarker">{str(idx)}</sup>{start_chapter_verse_text}</span>'
                )
        end_chapter_lower_verse = 1
        end_chapter_upper_verse = int(bible_reference.end_chapter_verse_ref)
        for idx in range(end_chapter_lower_verse, end_chapter_upper_verse + 1):
            end_chapter_verse_text = lookup_verse_text(
                usfm_book,
                bible_reference.end_chapter,
                str(idx),
            )
            if end_chapter_verse_text:
                verse_text.append(
                    f'<span class="verse"><sup class="versemarker">{str(idx)}</sup>{end_chapter_verse_text}</span>'
                )
    else:
        if "," in bible_reference.start_chapter_verse_ref:
            verse_range_components = bible_reference.start_chapter_verse_ref.split(",")
            for verse_ in verse_range_components:
                if "-" in verse_:
                    verse__range_components = verse_.split("-")
                    lower_verse_ = int(verse__range_components[0])
                    upper_verse_ = int(verse__range_components[1])
                    for idx in range(lower_verse_, upper_verse_ + 1):
                        verse_text__ = lookup_verse_text(
                            usfm_book,
                            bible_reference.start_chapter,
                            str(idx),
                        )
                        if verse_text__:
                            verse_text.append(
                                f'<span class="verse"><sup class="versemarker">{str(idx)}</sup>{verse_text__}</span>'
                            )
                else:
                    verse_text__ = lookup_verse_text(
                        usfm_book,
                        bible_reference.start_chapter,
                        verse_,
                    )
                    if verse_text__:
                        verse_text.append(
                            f'<span class="verse"><sup class="versemarker">{verse_}</sup>{verse_text__}</span>'
                        )
        elif "-" in bible_reference.start_chapter_verse_ref:
            verse_range_components = bible_reference.start_chapter_verse_ref.split("-")
            lower_verse = int(verse_range_components[0])
            upper_verse = int(verse_range_components[1])
            for idx in range(lower_verse, upper_verse + 1):
                verse_text_ = lookup_verse_text(
                    usfm_book,
                    bible_reference.start_chapter,
                    str(idx),
                )
                if verse_text_:
                    verse_text.append(
                        f'<span class="verse"><sup class="versemarker">{str(idx)}</sup>{verse_text_}</span>'
                    )
        else:
            verse_text___ = lookup_verse_text(
                usfm_book,
                bible_reference.start_chapter,
                bible_reference.start_chapter_verse_ref.strip(),
            )
            if verse_text___:
                verse_text.append(
                    f'<span class="verse"><sup class="versemarker">{bible_reference.start_chapter_verse_ref.strip()}</sup>{verse_text___}</span>'
                )
    return "".join(verse_text)
