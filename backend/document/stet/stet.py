import re
from datetime import datetime
from typing import Mapping, Optional, Sequence

import mistune
from celery import current_task
from document.config import settings
from document.domain.bible_books import BOOK_NAMES
from document.domain.model import USFMBook, USFMChapter
from document.domain.parsing import usfm_book_content
from document.domain.resource_lookup import (
    RESOURCE_TYPE_CODES_AND_NAMES,
    prepare_resource_filepath,
    provision_asset_files,
    resource_lookup_dto,
    resource_types,
)
from document.stet.model import VerseEntry, VerseReferenceDto, WordEntry, WordEntryDto
from document.stet.util import is_valid_int
from docx import Document  # type: ignore
from docx.document import Document as DocxDocument  # type: ignore
from docx.text.paragraph import Paragraph  # type: ignore
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT  # type: ignore
from docx.oxml import OxmlElement  # type: ignore
from docx.oxml.ns import qn  # type: ignore
from docx.shared import Pt, RGBColor  # type: ignore
from docx.table import Table, _Cell, _Row  # type: ignore
from htmldocx import HtmlToDocx  # type: ignore

logger = settings.logger(__name__)


def lookup_verse_text(usfm_book: USFMBook, chapter_num: int, verse_ref: str) -> str:
    if chapter_num in usfm_book.chapters:
        chapter = usfm_book.chapters[chapter_num]
        if chapter.verses:
            verse = chapter.verses[verse_ref] if verse_ref in chapter.verses else ""
            logger.debug(
                "book_code: %s, chapter_num: %s, verse_num: %s, verse: %s",
                usfm_book.book_code,
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
            # Remove versemarker
            verse_text = re.sub(r'<sup class="versemarker">.*?</sup>', "", verse_span)
            # Add to the dictionary with verse number as the key and verse text as the value
            verse_dict[verse_number_] = verse_text
    return verse_dict


def get_word_entry_dtos(
    lang0_code: str,
    lang1_code: str,
    book_names: dict[str, str] = BOOK_NAMES,
    stet_dir: str = settings.STET_DIR,
) -> tuple[list[WordEntryDto], list[str]]:
    # Build data from source doc
    word_entry_dtos: list[WordEntryDto] = []
    book_codes_: list[str] = []
    doc = Document(f"{stet_dir}/stet_{lang0_code}.docx")
    for table in doc.tables:
        for row in table.rows:
            # Create entry item
            word_entry_dto = WordEntryDto()
            # Extract data from word field
            match = re.match(r"(.*)(\n)?(.*)?", row.cells[0].text)
            if not match:
                raise ValueError(f"Couldn't parse word: {row.cells[0].text}")
            word = match.group(1)
            word_entry_dto.word = word
            raw_strongs = match.group(3)
            word_entry_dto.strongs_numbers = raw_strongs.strip()
            definition = ""
            previous_paragraph_style_name = ""
            for paragraph in row.cells[1].paragraphs:
                text = paragraph.text.strip()
                if previous_paragraph_style_name not in (paragraph.style.name, ""):
                    definition += "\n"
                if paragraph.style.name == "List Paragraph":
                    if text:
                        definition += f"- {paragraph.text.strip()}\n"
                else:
                    if text:
                        definition += f"{paragraph.text.strip()}\n"
                previous_paragraph_style_name = paragraph.style.name
            word_entry_dto.definition = definition
            # process verse list
            for reference in row.cells[2].text.split("\n"):
                reference_ = reference.strip()
                match = re.match(r"^(.*) (\d+):([0-9,\- ]+)\s?(\(.*\))?$", reference_)
                if not match:
                    logger.warning("Couldn't parse %s", reference_)
                    continue
                if match:
                    # Extract references
                    book_name = match.group(1)
                    book_codes = [
                        book_code
                        for book_code, book_name_ in book_names.items()
                        if book_name_ == book_name
                    ]
                    book_code = book_codes[0] if book_codes else None
                    if book_code:
                        book_codes_.append(book_code)
                    chapter_num = int(match.group(2))
                    verses = match.group(3)
                    comment = match.group(4)
                    if comment:
                        source_reference = (
                            f"{book_name} {chapter_num}:{verses}{comment}"
                        )
                    else:
                        source_reference = f"{book_name} {chapter_num}:{verses}"
                    target_reference = f"{book_name} {chapter_num}:{verses}"
                    verse_refs: list[str] = verses.split(",")
                    valid_verse_refs: list[str] = []
                    for verse_ref in verse_refs:
                        if is_valid_int(verse_ref):
                            valid_verse_refs.append(str(verse_ref))
                            continue
                        match = re.match(r"(\d+)-(\d+)", verse_ref)
                        if match:
                            start_verse = int(match.group(1))
                            end_verse = int(match.group(2))
                            verse_num = start_verse
                            while verse_num <= end_verse:
                                valid_verse_refs.append(str(verse_num))
                                verse_num += 1
                            continue
                        logger.warning("Couldn't parse verse ref: %s", verse_ref)
                    verse_reference_dto = VerseReferenceDto(
                        lang0_code=lang0_code,
                        lang1_code=lang1_code,
                        book_code=book_code,
                        book_name=book_name,
                        chapter_num=chapter_num,
                        source_reference=source_reference,
                        target_reference=target_reference,
                        verse_refs=valid_verse_refs,
                    )
                    word_entry_dto.verse_ref_dtos.append(verse_reference_dto)
            word_entry_dtos.append(word_entry_dto)
    return word_entry_dtos, list(set(book_codes_))


def format_docx_tables(doc: Document) -> Document:
    """
    Programmatically improve table borders and cell text padding.
    """
    # Loop through tables and set borders
    for table in doc.tables:
        tbl = table._element
        tblBorders = OxmlElement("w:tblBorders")
        for border_name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
            border = OxmlElement(f"w:{border_name}")
            border.set(qn("w:val"), "single")
            border.set(qn("w:sz"), "8")  # 1px equivalent in Word (1/8 point units)
            border.set(qn("w:space"), "0")
            border.set(qn("w:color"), "000000")  # Border color
            tblBorders.append(border)
        tbl.tblPr.append(tblBorders)
        # Ensure text in each cell is vertically centered and free of
        # excessive space.
        for row in table.rows:
            for cell in row.cells:
                tc = cell._element
                tcPr = tc.get_or_add_tcPr()
                # Set vertical alignment to center
                vAlign = OxmlElement("w:vAlign")
                vAlign.set(qn("w:val"), "center")
                tcPr.append(vAlign)
                # Optional: Adjust padding/margins if needed
                cell_paragraph = cell.paragraphs[0]
                # cell_paragraph.paragraph_format.left_indent = Pt(
                #     5
                # )  # Slight left padding
                cell_paragraph.paragraph_format.space_after = Pt(
                    0
                )  # Remove extra space after
    return doc


def add_checkbox_column(docx_filepath: str) -> None:
    """
    Add a third column to each table in a DOCX file, with each cell in the new column containing an unchecked checkbox.
    """
    doc: DocxDocument = Document(docx_filepath)
    for table in doc.tables:  # type: Table
        add_column_with_checkboxes(table)
    doc.save(docx_filepath)


def add_column_with_checkboxes(table: Table) -> None:
    """
    Add a new column to the right of a table, with each cell containing an unchecked checkbox.
    """
    for row in table.rows:
        # Append a new cell to the row's XML
        new_cell = add_cell_to_row(row)
        if new_cell:
            add_checkbox_to_cell(new_cell)


def add_cell_to_row(row: _Row) -> Optional[_Cell]:
    """
    Add a new cell to the row by manipulating its XML structure.
    Returns the new cell object.
    """
    tc = OxmlElement("w:tc")  # Create a new table cell element
    tcPr = OxmlElement("w:tcPr")  # Table cell properties
    tc.append(tcPr)  # Append properties to the cell
    row._tr.append(tc)  # Append the new cell to the row's XML
    # Wrap the XML element in a python-docx cell object
    return _Cell(tc, row.table)


def add_checkbox_to_cell(cell: _Cell) -> None:
    """
    Add an unchecked checkbox to a table cell.
    """
    # Create a checkbox element
    checkbox: OxmlElement = OxmlElement("w:sdt")  # Structured document tag
    sdtPr: OxmlElement = OxmlElement("w:sdtPr")
    checkBox: OxmlElement = OxmlElement("w:checkBox")
    sdtPr.append(checkBox)
    checkbox.append(sdtPr)
    sdtContent: OxmlElement = OxmlElement("w:sdtContent")
    p: OxmlElement = OxmlElement("w:p")  # Paragraph
    r: OxmlElement = OxmlElement("w:r")  # Run
    t: OxmlElement = OxmlElement("w:t")  # Text
    t.text = "☐"  # Use a Unicode checkbox character
    r.append(t)
    p.append(r)
    sdtContent.append(p)
    checkbox.append(sdtContent)
    # Add the checkbox to the cell
    if hasattr(cell, "_tc"):  # Ensure cell has '_tc' attribute for safety
        tc: Optional[OxmlElement] = getattr(cell, "_tc", None)
        if tc:
            tc.append(checkbox)


def extract_chapter_and_beyond(text: str) -> Optional[str]:
    # Regular expression to match "<chapter_num>:<verse_num> [comment]"
    match = re.search(r"\d+:\d+(\s*\(\*\*?\))?$", text)
    if match:
        return match.group()
    return None


def generate_docx_document(
    lang0_code: str,
    lang1_code: str,
    document_request_key_: str,
    docx_filepath_: str,
    working_dir: str = settings.WORKING_DIR,
    output_dir: str = settings.DOCUMENT_OUTPUT_DIR,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    resource_type_codes_and_names: Mapping[str, str] = RESOURCE_TYPE_CODES_AND_NAMES,
) -> str:
    """
    Generate the scriptural terms evaluation document.

    >>> from document.stet import generate_markdown_document
    >>> generate_docx_document()
    """
    word_entries: list[WordEntry] = []
    word_entry_dtos, book_codes = get_word_entry_dtos(lang0_code, lang1_code)
    lang0_resource_types = resource_types(lang0_code, ",".join(book_codes))
    lang0_resource_types_ = [
        lang0_resource_type_tuple[0]
        for lang0_resource_type_tuple in lang0_resource_types
    ]
    lang1_resource_types = resource_types(lang1_code, ",".join(book_codes))
    lang1_resource_types_ = [
        lang1_resource_type_tuple[0]
        for lang1_resource_type_tuple in lang1_resource_types
    ]
    lang0_usfm_resource_types = [
        resource_type_
        for resource_type_ in lang0_resource_types_
        if resource_type_ in usfm_resource_types
    ]
    lang1_usfm_resource_types = [
        resource_type_
        for resource_type_ in lang1_resource_types_
        if resource_type_ in usfm_resource_types
    ]
    lang0_ulb_usfm_resource_types = [
        usfm_resource_type_
        for usfm_resource_type_ in lang0_usfm_resource_types
        if "ulb" in usfm_resource_type_
    ]
    lang1_ulb_usfm_resource_types = [
        usfm_resource_type_
        for usfm_resource_type_ in lang1_usfm_resource_types
        if "ulb" in usfm_resource_type_
    ]
    source_usfm_books = []
    target_usfm_books = []
    lang0_usfm_resource_type = ""
    lang1_usfm_resource_type = ""
    if lang0_ulb_usfm_resource_types:  # Prefer ulb if available
        lang0_usfm_resource_type = lang0_ulb_usfm_resource_types[0]
    elif lang0_usfm_resource_types:
        lang0_usfm_resource_type = lang0_usfm_resource_types[0]
    if lang1_ulb_usfm_resource_types:  # Prefer ulb if available
        lang1_usfm_resource_type = lang1_ulb_usfm_resource_types[0]
    elif lang1_usfm_resource_types:
        lang1_usfm_resource_type = lang1_usfm_resource_types[0]
    if lang0_usfm_resource_type and lang1_usfm_resource_type:
        source_usfm_book = None
        target_usfm_book = None
        for book_code in book_codes:
            current_task.update_state(state="Locating assets")
            lang0_resource_lookup_dto_ = resource_lookup_dto(
                lang0_code, lang0_usfm_resource_type, book_code
            )
            if lang0_resource_lookup_dto_ and lang0_resource_lookup_dto_.url:
                current_task.update_state(state="Provisioning asset files")
                lang0_resource_dir = prepare_resource_filepath(
                    lang0_resource_lookup_dto_
                )
                provision_asset_files(
                    lang0_resource_lookup_dto_.url, lang0_resource_dir
                )
                current_task.update_state(state="Parsing asset files")
                source_usfm_book = usfm_book_content(
                    lang0_resource_lookup_dto_,
                    lang0_resource_dir,
                )
                for chapter_num_, chapter_ in source_usfm_book.chapters.items():
                    source_usfm_book.chapters[chapter_num_].verses = (
                        split_chapter_into_verses(chapter_)
                    )
                source_usfm_books.append(source_usfm_book)
            lang1_resource_lookup_dto_ = resource_lookup_dto(
                lang1_code, lang1_usfm_resource_type, book_code
            )
            if lang1_resource_lookup_dto_ and lang1_resource_lookup_dto_.url:
                lang1_resource_dir = prepare_resource_filepath(
                    lang1_resource_lookup_dto_
                )
                provision_asset_files(
                    lang1_resource_lookup_dto_.url, lang1_resource_dir
                )
                target_usfm_book = usfm_book_content(
                    lang1_resource_lookup_dto_,
                    lang1_resource_dir,
                )
                for chapter_num_, chapter_ in target_usfm_book.chapters.items():
                    target_usfm_book.chapters[chapter_num_].verses = (
                        split_chapter_into_verses(chapter_)
                    )
                target_usfm_books.append(target_usfm_book)
    current_task.update_state(state="Assembling content")
    for word_entry_dto in word_entry_dtos:
        source_verse_text = ""
        target_verse_text = ""
        word_entry = WordEntry()
        word_entry.word = word_entry_dto.word
        word_entry.strongs_numbers = word_entry_dto.strongs_numbers
        word_entry.definition = mistune.markdown(word_entry_dto.definition)
        for verse_ref_dto in word_entry_dto.verse_ref_dtos:
            source_selected_usfm_books = [
                usfm_book_
                for usfm_book_ in source_usfm_books
                if usfm_book_.lang_code == lang0_code
                and usfm_book_.book_code == verse_ref_dto.book_code
                and usfm_book_.resource_type_name
                == resource_type_codes_and_names[lang0_usfm_resource_type]
            ]
            target_selected_usfm_books = [
                usfm_book_
                for usfm_book_ in target_usfm_books
                if usfm_book_.lang_code == lang1_code
                and usfm_book_.book_code == verse_ref_dto.book_code
                and usfm_book_.resource_type_name
                == resource_type_codes_and_names[lang1_usfm_resource_type]
            ]
            source_verse_text = ""
            target_verse_text = ""
            source_selected_usfm_book = None
            target_selected_usfm_book = None
            if source_selected_usfm_books:
                source_selected_usfm_book = source_selected_usfm_books[0]
            if target_selected_usfm_books:
                target_selected_usfm_book = target_selected_usfm_books[0]
            for verse_ref in verse_ref_dto.verse_refs:
                if source_selected_usfm_book:
                    source_verse_text = lookup_verse_text(
                        source_selected_usfm_book,
                        verse_ref_dto.chapter_num,
                        verse_ref.strip(),
                    )
                else:
                    source_verse_text = ""
                if target_selected_usfm_book:
                    target_verse_text = lookup_verse_text(
                        target_selected_usfm_book,
                        verse_ref_dto.chapter_num,
                        verse_ref.strip(),
                    )
                else:
                    target_verse_text = ""
            non_book_name_portion_of_source_reference = extract_chapter_and_beyond(
                verse_ref_dto.source_reference
            )
            non_book_name_portion_of_target_reference = extract_chapter_and_beyond(
                verse_ref_dto.target_reference
            )
            nationalized_source_reference = (
                f"{source_selected_usfm_book.national_book_name} {non_book_name_portion_of_source_reference}"
                if source_selected_usfm_book
                and non_book_name_portion_of_source_reference
                else verse_ref_dto.source_reference
            )
            nationalized_target_reference = (
                f"{target_selected_usfm_book.national_book_name} {non_book_name_portion_of_target_reference}"
                if target_selected_usfm_book
                and non_book_name_portion_of_target_reference
                else verse_ref_dto.target_reference
            )
            word_entry.verses.append(
                VerseEntry(
                    source_reference=nationalized_source_reference,
                    source_text=source_verse_text,
                    target_reference=nationalized_target_reference,
                    target_text=target_verse_text,
                )
            )
        word_entries.append(word_entry)
    current_task.update_state(state="Converting to Docx")
    generate_docx(word_entries, docx_filepath_, lang0_code, lang1_code)
    return docx_filepath_


def generate_docx(
    word_entries: list[WordEntry], docx_filepath: str, lang0_code: str, lang1_code: str
) -> None:
    """
    Generates a DOCX document from a list of word entries and saves it to the given file path.
    :param word_entries: A list of word entries containing the word, strongs numbers, definition, and verses.
    :param docx_filepath: The file path where the generated DOCX document will be saved.
    :param lang0_code: Source language code for the document header.
    :param lang1_code: Target language code for the document header.
    """
    doc = Document()
    html_to_docx = HtmlToDocx()
    for word_entry in word_entries:
        # Add the word heading
        heading: str = (
            f"{word_entry.word} ({word_entry.strongs_numbers})"
            if word_entry.strongs_numbers
            else word_entry.word
        )
        doc.add_heading(heading, level=1)
        # Convert the HTML definition to DOCX content
        if word_entry.definition:
            html_to_docx.add_html_to_document(word_entry.definition, doc)
        # Create a table with three columns
        table = doc.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        # Set the header of the table and apply bold formatting
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Source Reference"
        hdr_cells[1].text = "Target Reference"
        hdr_cells[2].text = "Status"
        hdr_cells[2].paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        for hdr_cell in hdr_cells:
            hdr_cell.paragraphs[0].runs[0].bold = True
        # Add verses to the table
        for verse in word_entry.verses:
            # Row for references
            row_cells = table.add_row().cells
            source_run = row_cells[0].paragraphs[0].add_run(verse.source_reference)
            source_run.bold = True
            target_run = row_cells[1].paragraphs[0].add_run(verse.target_reference)
            target_run.bold = True
            status_run = row_cells[2].paragraphs[0].add_run("OK")
            status_run.bold = True
            row_cells[2].paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            # Row for texts
            row_cells = table.add_row().cells
            # Process HTML content in source_text and highlight keyword
            source_paragraph = row_cells[0].paragraphs[0]
            source_paragraph.paragraph_format.line_spacing = 2.0  # Adjust line spacing
            add_highlighted_html_to_docx(
                verse.source_text, source_paragraph, word_entry.word
            )
            # Add target_text with wider line spacing
            target_paragraph = row_cells[1].paragraphs[0]
            target_paragraph.paragraph_format.line_spacing = 2.0  # Adjust line spacing
            add_plain_html_to_docx(verse.target_text, target_paragraph)
            # Vertically centered Unicode checkbox
            checkbox_cell = row_cells[2]
            checkbox_paragraph = checkbox_cell.paragraphs[0]
            checkbox_paragraph.text = "\u2610"
            checkbox_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            # Set vertical alignment to center using XML
            tc = checkbox_cell._tc  # Access the XML element of the table cell
            tcPr = tc.get_or_add_tcPr()  # Get or add the cell properties
            vAlign = OxmlElement("w:vAlign")  # Create the vertical alignment element
            vAlign.set(qn("w:val"), "center")  # Set alignment to "center"
            tcPr.append(vAlign)  # Append the vertical alignment to cell properties
        # Adjust column widths to prioritize the first two columns
        adjust_table_columns(table)
    doc = add_footer(doc)
    doc = add_header(doc, lang0_code, lang1_code)
    doc = add_lined_page_at_end(doc)
    reduce_spacing_around_tables(doc)
    doc.save(docx_filepath)


def add_highlighted_html_to_docx(html: str, paragraph: Paragraph, keyword: str) -> None:
    """
    Convert HTML to DOCX and highlight occurrences of a keyword in bold.
    :param html: The HTML string to convert.
    :param paragraph: The DOCX paragraph where the content will be added.
    :param keyword: The keyword to highlight in bold.
    """
    # Use HtmlToDocx to convert the HTML to a temporary document
    html_to_docx = HtmlToDocx()
    temp_doc = Document()
    html_to_docx.add_html_to_document(html, temp_doc)
    keyword_lower = keyword.lower()
    # Parse through all paragraphs in the temporary document
    for temp_paragraph in temp_doc.paragraphs:
        text = temp_paragraph.text.strip()
        start = 0
        while True:
            # Case-insensitive search for the keyword
            start_idx = text.lower().find(keyword_lower, start)
            if start_idx == -1:
                break
            # Add text before the keyword
            if start_idx > start:
                paragraph.add_run(text[start:start_idx])
            # Add the bold keyword
            bold_run = paragraph.add_run(text[start_idx : start_idx + len(keyword)])
            bold_run.bold = True
            start = start_idx + len(keyword)
        # Add the remaining text
        if start < len(text):
            paragraph.add_run(text[start:])


def add_plain_html_to_docx(html: str, paragraph: Paragraph) -> None:
    """
    Convert HTML to DOCX without highlighting.

    :param html: The HTML string to convert.
    :param paragraph: The DOCX paragraph where content will be added.
    """
    # Use HtmlToDocx to convert the HTML to the target paragraph
    html_to_docx = HtmlToDocx()
    temp_doc = Document()
    html_to_docx.add_html_to_document(html, temp_doc)
    # Add plain text from the temp_doc into the target paragraph
    for temp_paragraph in temp_doc.paragraphs:
        paragraph.add_run(temp_paragraph.text.strip())


def add_lined_page_at_end(doc: Document) -> Document:
    """
    Adds a single page filled with ruled lines to the end of the document for note-taking.
    Each line spans the full page width and is evenly spaced.
    :param doc: The Word document to which the ruled page will be added.
    :return: The modified Word document.
    """
    section = doc.add_section(start_type=1)  # Add a new section for a new page
    section.left_margin = section.right_margin = Pt(72)  # 1-inch margins
    section.top_margin = section.bottom_margin = Pt(72)
    usable_height = section.page_height - section.top_margin - section.bottom_margin
    line_spacing = Pt(18)  # Approx. 1.5x line spacing for handwriting clarity
    num_lines = int(usable_height / line_spacing)
    # Add a single paragraph with blank lines separated by line breaks
    lined_paragraph = doc.add_paragraph()
    lined_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    lined_paragraph.paragraph_format.space_before = Pt(0)
    lined_paragraph.paragraph_format.space_after = Pt(0)
    lined_paragraph.paragraph_format.line_spacing = line_spacing
    for _ in range(num_lines - 3):
        lined_paragraph.add_run("_" * 100)  # Add a visible placeholder for each line
        lined_paragraph.add_run("\n")  # Add a line break to simulate ruled lines
    return doc


def adjust_table_columns(table: Table) -> None:
    """
    Adjusts the table columns so that the last column ('Status') is minimal,
    while the other columns take up the remaining space.
    :param table: The table to adjust.
    """
    # Set widths for each column
    column_widths = [5.5, 5.5, 1.0]  # Adjust widths in inches (example values)
    # Apply widths to the columns
    for col_idx, width in enumerate(column_widths):
        for cell in table.columns[col_idx].cells:
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            tcW = OxmlElement("w:tcW")
            tcW.set(qn("w:w"), str(int(width * 1440)))  # Convert inches to twips
            tcW.set(qn("w:type"), "dxa")
            tcPr.append(tcW)


def reduce_spacing_around_tables(
    doc: Document, before_table_space: int = 0, after_table_space: int = 0
) -> None:
    """
    Reduces the whitespace around tables in a Word document.

    Parameters:
        doc (Document): A `Document` instance from python-docx.
        before_table_space (int): The spacing (in points) to set before a table. Default is 0.
        after_table_space (int): The spacing (in points) to set after a table. Default is 0.
    """

    def set_spacing(
        paragraph: Paragraph, before: Optional[int] = None, after: Optional[int] = None
    ) -> None:
        # Access or create the <w:spacing> element
        pPr = paragraph._element.get_or_add_pPr()
        spacing = pPr.find(qn("w:spacing"))
        if spacing is None:
            spacing = OxmlElement("w:spacing")
            pPr.append(spacing)
        if before is not None:
            spacing.set(qn("w:before"), str(before))
        if after is not None:
            spacing.set(qn("w:after"), str(after))

    # Iterate through all elements in the document
    previous_element = None
    for element in doc.element.body:
        if element.tag.endswith("tbl"):  # Table tag
            # If there's a previous element, adjust its spacing after the element
            if previous_element is not None and previous_element.tag.endswith("p"):
                paragraph = Paragraph(previous_element, doc)
                set_spacing(paragraph, after=before_table_space)
            previous_element = element
        elif element.tag.endswith("p"):  # Paragraph tag
            paragraph = Paragraph(element, doc)
            if previous_element is not None and previous_element.tag.endswith("tbl"):
                # Adjust spacing for the paragraph following a table
                set_spacing(paragraph, before=after_table_space)
            previous_element = element


def add_footer(doc: Document) -> Document:
    """
    Programmatically add page numbers and a date timestamp in the footer.
    Page number will be centered, and the date timestamp will be aligned to the right
    on the same line. The date timestamp will be prepended with 'Generated on ',
    and both will be grey. The timestamp will stay within the right margin.
    """
    section = doc.sections[0]
    footer = section.footer
    # Page width adjustments
    page_width = section.page_width
    left_margin = section.left_margin
    right_margin = section.right_margin
    # Calculate usable content width
    usable_width = page_width - left_margin - right_margin
    # Create or get the footer paragraph
    footer_paragraph = (
        footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    )
    footer_paragraph.alignment = None  # Disable global alignment to use tab stops
    # Configure tab stops
    p_pr = footer_paragraph._p.get_or_add_pPr()  # Access paragraph properties
    tabs = p_pr.find(qn("w:tabs"))  # Find existing 'w:tabs' element if it exists
    if tabs is None:
        tabs = OxmlElement("w:tabs")  # Create the 'w:tabs' element
        p_pr.append(tabs)
    # Add a center tab stop at half of usable content width
    center_position = int(usable_width / 2)  # Center of the usable area
    center_tab = OxmlElement("w:tab")
    center_tab.set(qn("w:val"), "center")
    center_tab.set(qn("w:pos"), str(center_position))
    tabs.append(center_tab)
    # Add a right-aligned tab stop slightly before the right margin
    right_position = int(usable_width)
    right_tab = OxmlElement("w:tab")
    right_tab.set(qn("w:val"), "right")
    right_tab.set(
        qn("w:pos"), str(right_position - 720)
    )  # 720 twips (0.5 inches) padding
    tabs.append(right_tab)
    # Add the page number field
    footer_paragraph.add_run("\t")  # Tab to center position
    field_code = "PAGE"
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), field_code)
    page_run = footer_paragraph.add_run()
    page_run._r.append(field)
    page_run.font.color.rgb = RGBColor(169, 169, 169)  # Grey color for page number
    # Add the "Generated on" text
    footer_paragraph.add_run("\t")  # Tab to right position
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_text = f"Generated on {current_datetime}"
    date_run = footer_paragraph.add_run(date_text)
    date_run.font.color.rgb = RGBColor(169, 169, 169)  # Grey color for timestamp
    date_run.font.size = Pt(10)  # Optional: Adjust font size for consistency
    return doc


def add_header(doc: Document, source_lang_code: str, target_lang_code: str) -> Document:
    """
    Add a header with:
    - 'Spiritual Terms Evaluation Tool' left.
    - 'source_lang_code/target_lang_code' aligned to the right.
    """
    section = doc.sections[0]
    header = section.header
    header_paragraph = header.add_paragraph()
    header_paragraph.style.font.size = Pt(12)  # Optional: Adjust font size
    # Add the "Spiritual Terms Evaluation Tool" text with grey color
    run1 = header_paragraph.add_run("Spiritual Terms Evaluation Tool")
    run1.font.color.rgb = RGBColor(169, 169, 169)  # Grey color
    # Add a tab and the "EN/FR" text with grey color
    header_paragraph.add_run("\t")  # Add a tab for alignment
    run2 = header_paragraph.add_run(
        f"{source_lang_code.upper()}/{target_lang_code.upper()}"
    )
    run2.font.color.rgb = RGBColor(169, 169, 169)  # Grey color
    # Adjust tab stops (tab position must be an integer)
    page_width = section.page_width
    left_margin = section.left_margin
    right_margin = section.right_margin
    usable_width = page_width - left_margin - right_margin
    # Set the tab stop closer to the right margin but within bounds
    tab_position = int(left_margin + (usable_width * 0.75))  # 75% of usable width
    header_paragraph.paragraph_format.tab_stops.add_tab_stop(
        tab_position, alignment=WD_ALIGN_PARAGRAPH.RIGHT
    )
    header_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return doc
