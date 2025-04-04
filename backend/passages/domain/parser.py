from passages.domain.model import PassageReferenceDto
from doc.domain.parsing import lookup_verse_text
from doc.domain.model import USFMBook


def verse_text_html(passage_ref_dto: PassageReferenceDto, usfm_book: USFMBook) -> str:
    verse_text = []
    if "," in passage_ref_dto.verse_reference:
        verse_range_components = passage_ref_dto.verse_reference.split(",")
        for verse_ in verse_range_components:
            if "-" in verse_:
                verse__range_components = verse_.split("-")
                lower_verse_ = int(verse__range_components[0])
                upper_verse_ = int(verse__range_components[1])
                for idx in range(lower_verse_, upper_verse_ + 1):
                    verse_text__ = lookup_verse_text(
                        usfm_book,
                        passage_ref_dto.chapter_num,
                        str(idx),
                    )
                    if verse_text__:
                        verse_text.append(
                            f'<span class="verse"><sup class="versemarker">{str(idx)}</sup>{verse_text__}</span>'
                        )
            else:
                verse_text__ = lookup_verse_text(
                    usfm_book,
                    passage_ref_dto.chapter_num,
                    verse_,
                )
                if verse_text__:
                    verse_text.append(
                        f'<span class="verse"><sup class="versemarker">{verse_}</sup>{verse_text__}</span>'
                    )
    elif "-" in passage_ref_dto.verse_reference:
        verse_range_components = passage_ref_dto.verse_reference.split("-")
        lower_verse = int(verse_range_components[0])
        upper_verse = int(verse_range_components[1])
        for idx in range(lower_verse, upper_verse + 1):
            verse_text_ = lookup_verse_text(
                usfm_book,
                passage_ref_dto.chapter_num,
                str(idx),
            )
            if verse_text_:
                verse_text.append(
                    f'<span class="verse"><sup class="versemarker">{str(idx)}</sup>{verse_text_}</span>'
                )
    else:
        verse_text___ = lookup_verse_text(
            usfm_book,
            passage_ref_dto.chapter_num,
            passage_ref_dto.verse_reference.strip(),
        )
        if verse_text___:
            verse_text.append(
                f'<span class="verse"><sup class="versemarker">{passage_ref_dto.verse_reference.strip()}</sup>{verse_text___}</span>'
            )
    return "".join(verse_text)
