import re
from typing import Optional

from docx import Document  # type: ignore
from docx.document import Document as DocxDocument  # type: ignore
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT  # type: ignore
from docx.oxml import OxmlElement  # type: ignore
from docx.oxml.ns import qn  # type: ignore
from docx.shared import Pt, RGBColor  # type: ignore
from docx.table import Table, _Cell, _Row  # type: ignore
from docx.text.paragraph import Paragraph  # type: ignore
from htmldocx import HtmlToDocx  # type: ignore


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


def add_header(
    doc: Document,
    source_lang_code: str,
    target_lang_code: str,
    header_text: str = "Spiritual Terms Evaluation Tool (STET)",
) -> Document:
    """
    Add a header with:
    - header_text left.
    - 'source_lang_code/target_lang_code' aligned to the right.
    """
    section = doc.sections[0]
    header = section.header
    header_paragraph = header.add_paragraph()
    header_paragraph.style.font.size = Pt(12)  # Optional: Adjust font size
    # Add the "Spiritual Terms Evaluation Tool" text with grey color
    run1 = header_paragraph.add_run(header_text)
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


def add_highlighted_html_to_docx_for_words(
    html: str, paragraph: Paragraph, keywords: list[str]
) -> None:
    """
    Convert HTML to DOCX and highlight occurrences of keywords in bold.
    :param html: The HTML string to convert.
    :param paragraph: The DOCX paragraph where the content will be added.
    :param keywords: The list of keywords to highlight in bold.
    """
    # Use HtmlToDocx to convert the HTML to a temporary document
    html_to_docx = HtmlToDocx()
    temp_doc = Document()
    html_to_docx.add_html_to_document(html, temp_doc)
    # Create a case-insensitive regex pattern for word-boundary matching
    keyword_pattern = r"\b(" + "|".join(re.escape(kw) for kw in keywords) + r")\b"
    regex = re.compile(keyword_pattern, re.IGNORECASE)
    # Parse through all paragraphs in the temporary document
    for temp_paragraph in temp_doc.paragraphs:
        text = temp_paragraph.text
        start = 0
        # Iterate over matches in the text
        for match in regex.finditer(text):
            # Add text before the match
            if match.start() > start:
                paragraph.add_run(text[start : match.start()])
            # Add the bolded keyword with original casing
            bold_run = paragraph.add_run(text[match.start() : match.end()])
            bold_run.bold = True
            # Move start position forward
            start = match.end()
        # Add any remaining text after the last match
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


def add_footer(doc: Document, date_text: str) -> Document:
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
    date_run = footer_paragraph.add_run(date_text)
    date_run.font.color.rgb = RGBColor(169, 169, 169)  # Grey color for timestamp
    date_run.font.size = Pt(10)  # Optional: Adjust font size for consistency
    return doc
