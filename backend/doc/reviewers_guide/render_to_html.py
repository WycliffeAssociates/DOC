"""Functions to render RGBook and its constituent parts to HTML"""

from doc.reviewers_guide.model import (
    BibleReference,
    ParsedText,
    Part1Item,
    Part2Item,
    RGChapter,
)
from doc.utils.template_env import env


def render_part1_item(item: Part1Item) -> str:
    template = env.get_template("html/part1_item.html")
    return template.render(text=item.text, reference=item.reference)


def render_part2_item(item: Part2Item) -> str:
    template = env.get_template("html/part2_item.html")
    return template.render(
        reference=item.reference, question=item.question, answer=item.answer
    )


def render_bible_reference(ref: BibleReference) -> str:
    template = env.get_template("html/bible_reference.html")
    return template.render(
        book_name=ref.book_name,
        start_chapter=ref.start_chapter,
        start_chapter_verse_ref=ref.start_chapter_verse_ref,
        end_chapter=ref.end_chapter,
        end_chapter_verse_ref=ref.end_chapter_verse_ref,
    )


def render_parsed_text(parsed: ParsedText) -> str:
    part1_html = "".join(render_part1_item(item) for item in parsed.part_1)
    part2_html = "".join(render_part2_item(item) for item in parsed.part_2)
    template = env.get_template("html/parsed_text.html")
    return template.render(
        bible_reference=render_bible_reference(parsed.bible_reference),
        background=parsed.background,
        directive=parsed.directive,
        part_1_directive=parsed.part_1_directive,
        part1_html=part1_html,
        part_2_directive=parsed.part_2_directive,
        part2_html=part2_html,
        comment_section=parsed.comment_section,
    )


def render_chapter(chapter: RGChapter) -> str:
    template = env.get_template("html/rg_chapter.html")
    parsed_texts_html = "".join(render_parsed_text(pt) for pt in chapter.content)
    return template.render(parsed_texts_html=parsed_texts_html)
