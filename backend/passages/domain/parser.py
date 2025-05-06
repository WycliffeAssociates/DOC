from typing import Mapping
from passages.domain.model import PassageReferenceDto
from doc.domain.parsing import lookup_verse_text
from doc.domain.model import USFMBook
from doc.domain.bible_books import BOOK_CHAPTER_VERSES
from doc.config import settings

logger = settings.logger(__name__)


def verse_text_html(
    passage_ref_dto: PassageReferenceDto,
    usfm_book: USFMBook,
    book_chapter_verses: Mapping[str, Mapping[str, str]] = BOOK_CHAPTER_VERSES,
) -> str:
    verse_text = []
    if (
        passage_ref_dto.end_chapter_num
        and passage_ref_dto.end_chapter_num > 0
        and passage_ref_dto.end_chapter_verse_reference
    ):  # chapter boundary traversal
        start_chapter_lower_verse = int(passage_ref_dto.start_chapter_verse_reference)
        start_chapter_upper_verse = int(
            book_chapter_verses[passage_ref_dto.book_code][
                str(passage_ref_dto.start_chapter_num)
            ]
        )
        for idx in range(start_chapter_lower_verse, start_chapter_upper_verse + 1):
            start_chapter_verse_text = lookup_verse_text(
                usfm_book,
                passage_ref_dto.start_chapter_num,
                str(idx),
            )
            if start_chapter_verse_text:
                verse_text.append(
                    f'<span class="verse"><sup class="versemarker">{str(idx)}</sup>{start_chapter_verse_text}</span>'
                )
        end_chapter_lower_verse = 1
        end_chapter_upper_verse = int(passage_ref_dto.end_chapter_verse_reference)
        for idx in range(end_chapter_lower_verse, end_chapter_upper_verse):
            end_chapter_verse_text = lookup_verse_text(
                usfm_book,
                passage_ref_dto.end_chapter_num,
                str(idx),
            )
            if end_chapter_verse_text:
                verse_text.append(
                    f'<span class="verse"><sup class="versemarker">{str(idx)}</sup>{end_chapter_verse_text}</span>'
                )
    else:
        if "," in passage_ref_dto.start_chapter_verse_reference:
            verse_range_components = (
                passage_ref_dto.start_chapter_verse_reference.split(",")
            )
            for verse_ in verse_range_components:
                if "-" in verse_:
                    verse__range_components = verse_.split("-")
                    lower_verse_ = int(verse__range_components[0])
                    upper_verse_ = int(verse__range_components[1])
                    for idx in range(lower_verse_, upper_verse_ + 1):
                        verse_text__ = lookup_verse_text(
                            usfm_book,
                            passage_ref_dto.start_chapter_num,
                            str(idx),
                        )
                        if verse_text__:
                            verse_text.append(
                                f'<span class="verse"><sup class="versemarker">{str(idx)}</sup>{verse_text__}</span>'
                            )
                else:
                    verse_text__ = lookup_verse_text(
                        usfm_book,
                        passage_ref_dto.start_chapter_num,
                        verse_,
                    )
                    if verse_text__:
                        verse_text.append(
                            f'<span class="verse"><sup class="versemarker">{verse_}</sup>{verse_text__}</span>'
                        )
        elif "-" in passage_ref_dto.start_chapter_verse_reference:
            verse_range_components = (
                passage_ref_dto.start_chapter_verse_reference.split("-")
            )
            lower_verse = int(verse_range_components[0])
            upper_verse = int(verse_range_components[1])
            for idx in range(lower_verse, upper_verse + 1):
                verse_text_ = lookup_verse_text(
                    usfm_book,
                    passage_ref_dto.start_chapter_num,
                    str(idx),
                )
                if verse_text_:
                    verse_text.append(
                        f'<span class="verse"><sup class="versemarker">{str(idx)}</sup>{verse_text_}</span>'
                    )
        else:
            verse_text___ = lookup_verse_text(
                usfm_book,
                passage_ref_dto.start_chapter_num,
                passage_ref_dto.start_chapter_verse_reference.strip(),
            )
            if verse_text___:
                verse_text.append(
                    f'<span class="verse"><sup class="versemarker">{passage_ref_dto.start_chapter_verse_reference.strip()}</sup>{verse_text___}</span>'
                )
    return "".join(verse_text)
