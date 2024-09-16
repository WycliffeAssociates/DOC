import json
import re
from pathlib import Path

import chevron
import jinja2
from document.config import settings
from document.domain.model import DocumentRequest, USFMBook, USFMChapter, VerseRef
from document.domain.bible_books import BOOK_NAMES
from document.stet.model import VerseEntry, WordEntry
from document.utils.file_utils import template_path
from document.stet.util import is_valid_int
from docx import Document  # type: ignore
from htmldocx import HtmlToDocx  # type: ignore
from typing import Sequence

logger = settings.logger(__name__)


def lookup_verse_text(usfm_book: USFMBook, chapter_num: int, verse_ref: str) -> str:
    logger.debug("chapter_num: %s", chapter_num)
    if chapter_num in usfm_book.chapters:
        chapter = usfm_book.chapters[chapter_num]
        if chapter.verses:
            verse = chapter.verses[verse_ref] if verse_ref in chapter.verses else ""
            logger.debug(
                "chapter_num: %s, verse_num: %s, verse: %s",
                chapter_num,
                verse_ref,
                verse,
            )
            return verse
        return ""
    return ""


def split_chapter_into_verses(chapter: USFMChapter) -> dict[str, str]:
    # Sample HTML content with multiple verse elements
    # html_content = '''
    # <span class="verse">
    # <sup class="versemarker">19</sup>
    # For through the law I died to the law, so that I might live for God. I have been crucified with Christ.
    # <sup id="footnote-caller-1" class="caller"><a href="#footnote-target-1">1</a></sup>
    # <div class="sectionhead-5"></div>
    # </span>

    # <span class="verse">
    # <sup class="versemarker">20</sup>
    # I have been crucified with Christ and I no longer live, but Christ lives in me. The life I now live in the body, I live by faith in the Son of God, who loved me and gave himself for me.
    # <sup id="footnote-caller-2" class="caller"><a href="#footnote-target-2">2</a></sup>
    # <div class="sectionhead-5"></div>
    # </span>
    # '''

    verse_dict = {}
    # Find all verse spans
    verse_spans = re.findall(
        r'<span class="verse">(.*?)</span>', chapter.content, re.DOTALL
    )
    for verse_span in verse_spans:
        # Extract the verse number from the versemarker
        verse_number = re.search(r'<sup class="versemarker">(\d+)</sup>', verse_span)
        if verse_number:
            verse_number_ = verse_number.group(1)
            # Remove all <sup> and <div> tags and their content from the verse text
            verse_text = re.sub(r"<sup.*?>.*?</sup>", "", verse_span)
            verse_text = re.sub(r"<div.*?>.*?</div>", "", verse_text)
            # Remove the remaining HTML tags and strip extra spaces
            verse_text = re.sub(r"<.*?>", "", verse_text).strip()
            logger.debug("verse_number: %s, verse_text: %s", verse_number_, verse_text)
            # Add to the dictionary with verse number as the key and verse text as the value
            verse_dict[verse_number_] = verse_text
    return verse_dict


def generate_docx_document(
    document_request_key: str,
    document_request: DocumentRequest,
    usfm_books: Sequence[USFMBook],
    stet_dir: str = settings.STET_DIR,
    working_dir: str = settings.WORKING_DIR,
    book_names: dict[str, str] = BOOK_NAMES,
) -> str:
    """
    Generate the scriptural terms evaluation document.

    >>> from document.stet import generate_document
    >>> generate_document()
    """
    source_usfm_book = [
        usfm_book for usfm_book in usfm_books if usfm_book.lang_code == "en"
    ][0]
    logger.debug("source_usfm_book language: %s", source_usfm_book.lang_code)
    target_usfm_book = [
        usfm_book for usfm_book in usfm_books if usfm_book.lang_code != "en"
    ][0]
    logger.debug("target_usfm_book language: %s", target_usfm_book.lang_code)
    for chapter_num_, chapter_ in source_usfm_book.chapters.items():
        source_usfm_book.chapters[chapter_num_].verses = split_chapter_into_verses(
            chapter_
        )
    for chapter_num_, chapter_ in target_usfm_book.chapters.items():
        target_usfm_book.chapters[chapter_num_].verses = split_chapter_into_verses(
            chapter_
        )
    # Build data from source doc
    data: list[WordEntry] = []
    doc = Document(f"{stet_dir}/stet_en.docx")
    for table in doc.tables:
        for row in table.rows:
            # Create entry item
            word_entry = WordEntry()
            # Extract data from word field
            match = re.match(r"(.*)(\n)?(.*)?", row.cells[0].text)
            # TODO Maybe shouldn't raise an exception here
            if not match:
                raise ValueError(f"Couldn't parse word def: {row.cells[0].text}")
            word = match.group(1)
            word_entry.word = word
            raw_strongs = match.group(3)
            word_entry.strongs_numbers = raw_strongs.strip()
            definition = ""
            previous_paragraph_style_name = ""
            for paragraph in row.cells[1].paragraphs:
                if previous_paragraph_style_name not in (paragraph.style.name, ""):
                    definition += "\n"
                if paragraph.style.name == "List Paragraph":
                    definition += f"- {paragraph.text.strip()}\n"
                else:
                    definition += f"{paragraph.text.strip()}\n"
                previous_paragraph_style_name = paragraph.style.name
            word_entry.definition = definition
            # process verse list
            for reference in row.cells[2].text.split("\n"):
                reference_ = reference.strip()
                match = re.match(r"^(.*) (\d+):([0-9,\- ]+)\s?(\(.*\))?$", reference_)
                if not match:
                    logger.warning("Couldn't parse %s", reference_)
                    continue
                if match:
                    # Extract references
                    book = match.group(1)
                    chapter_num = int(match.group(2))
                    verses = match.group(3)
                    comment = match.group(4)
                    logger.debug(
                        "book: %s, chapter_num: %s, verse_num(s): %s, comment: %s",
                        book,
                        chapter_num,
                        verses,
                        comment,
                    )
                    # Get chapter content for each chapter in source USFMBook and split it into verses
                    # Break apart source tool verses
                    source_verse_text = []
                    target_verse_text = []
                    verse_refs: list[str] = verses.split(",")
                    fixed_verse_refs: list[str] = []
                    for verse_ref in verse_refs:
                        if is_valid_int(verse_ref):
                            fixed_verse_refs.append(str(verse_ref))
                            continue
                        match = re.match(r"(\d+)-(\d+)", verse_ref)
                        if match:
                            start_verse = int(match.group(1))
                            end_verse = int(match.group(2))
                            verse_num = start_verse
                            while verse_num <= end_verse:
                                fixed_verse_refs.append(str(verse_num))
                                verse_num += 1
                            continue
                        logger.warning("Couldn't parse verse ref: %s", verse_ref)
                    verse_refs = fixed_verse_refs
                    # Build up source and target verse text
                    for verse_ref in verse_refs:
                        verse_ref = verse_ref.strip()
                        # verse_ref_ = int(verse_ref)
                        source_verse_text_ = lookup_verse_text(
                            source_usfm_book, chapter_num, verse_ref
                        )
                        logger.debug("source_verse_text_: %s", source_verse_text_)
                        source_verse_text.append(source_verse_text_)
                        target_verse_text_ = lookup_verse_text(
                            target_usfm_book, chapter_num, verse_ref
                        )
                        logger.debug("target_verse_text_: %s", target_verse_text_)
                        target_verse_text.append(target_verse_text_)
                    # Clean up comments
                    if comment:
                        # Replace asterisks with Markdown-compatible asterisks
                        comment = re.sub(r"\*", r"\\*", comment)
                    # Write row to table
                    if comment:
                        source_reference = f"{book} {chapter_num}:{verses}{comment}"
                    else:
                        source_reference = f"{book} {chapter_num}:{verses}"
                    target_book_name = book_names[target_usfm_book.book_code]
                    word_entry.verses.append(
                        VerseEntry(
                            source_reference=source_reference,
                            source_text=" ".join(source_verse_text),
                            target_reference=f"{target_book_name} {chapter_num}:{verses}",
                            target_text=" ".join(target_verse_text),
                        )
                    )
            data.append(word_entry)
    logger.debug("len(words): %s", len(data))
    # Build output doc
    # Create markdown file that you can run pandoc on
    template = Path(template_path("stet")).read_text(encoding="utf-8")
    # markdown_ = chevron.render(template=template, data={"words": data})
    markdown_ = chevron.render(template=template, data=data)  # type: ignore
    markdown_filepath = f"{working_dir}/{document_request_key}.md"
    with open(markdown_filepath, "w", encoding="utf-8") as outfile:
        outfile.write(markdown_)
    return markdown_filepath
    # # Create HTML file and then convert it to Docx with library
    # template_path = "template.html"
    # # Hydrate and render the template
    # with open(template_path, "r") as filepath:
    #     template = filepath.read()
    # env = jinja2.Environment(autoescape=True).from_string(template)
    # full_html = env.render(data=data)
    # with open("output.html", "w", encoding="utf-8") as outfile2:
    #     outfile2.write(full_html)
    # html_to_docx = HtmlToDocx()
    # html_to_docx.parse_html_file("output.html", "stet_output")
    # # doc = html_to_docx.parse_html_string(html)
    # # logger.debug("doc: %s", doc)
