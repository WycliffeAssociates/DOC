from datetime import datetime
from typing import cast, Optional, TYPE_CHECKING

from docx import Document
from docx.enum.section import WD_SECTION
from docx.document import Document as DocxDocument
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.oxml.table import CT_Tc
from docx.shared import Pt, RGBColor
from docx.table import Table
from docx.text.paragraph import Paragraph
from html4docx import HtmlToDocx  # type: ignore


from docx.table import _Cell, _Row

if TYPE_CHECKING:
    from typing import TypeAlias

    Cell: TypeAlias = _Cell
    Row: TypeAlias = _Row
else:
    Cell = _Cell
    Row = _Row


def format_docx_tables(doc: DocxDocument) -> DocxDocument:
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
        new_cell = _append_cell(row)
        if new_cell:
            add_checkbox_to_cell(new_cell)


def _append_cell(row: Row) -> Optional[Cell]:
    tc = OxmlElement("w:tc")
    tc.append(OxmlElement("w:tcPr"))
    row._tr.append(tc)
    return Cell(cast(CT_Tc, tc), row.table)


def add_checkbox_to_cell(cell: Cell) -> None:
    """
    Add an unchecked checkbox to a table cell.
    """
    # Create a checkbox element
    checkbox = OxmlElement("w:sdt")  # Structured document tag
    sdtPr = OxmlElement("w:sdtPr")
    checkBox = OxmlElement("w:checkBox")
    sdtPr.append(checkBox)
    checkbox.append(sdtPr)
    sdtContent = OxmlElement("w:sdtContent")
    p = OxmlElement("w:p")  # Paragraph
    r = OxmlElement("w:r")  # Run
    t = OxmlElement("w:t")  # Text
    t.text = "☐"  # Use a Unicode checkbox character
    r.append(t)
    p.append(r)
    sdtContent.append(p)
    checkbox.append(sdtContent)
    # Add the checkbox to the cell
    if hasattr(cell, "_tc"):  # Ensure cell has '_tc' attribute for safety
        tc = getattr(cell, "_tc", None)
        if tc:
            tc.append(checkbox)


def add_header(
    doc: DocxDocument,
    lang0_name: str,
    lang1_name: Optional[str],
    header_text: str = "Passages",
) -> DocxDocument:
    """
    Add a header with:
    - header_text left.
    """
    section = doc.sections[0]
    header = section.header
    header_paragraph = header.add_paragraph()
    header_paragraph.style = doc.styles["Header"]
    header_paragraph.style.font.size = Pt(12)  # Optional: Adjust font size
    if lang1_name:
        # Add the header text with grey color
        run1 = header_paragraph.add_run(
            header_text + ": " + lang0_name + "/" + lang1_name
        )
        run1.font.color.rgb = RGBColor(169, 169, 169)  # Grey color
    else:
        # Add the header text with grey color
        run1 = header_paragraph.add_run(header_text + ": " + lang0_name)
        run1.font.color.rgb = RGBColor(169, 169, 169)  # Grey color
    return doc


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


def add_lined_page_at_end(doc: DocxDocument) -> DocxDocument:
    """
    Adds a single page filled with ruled lines to the end of the document for note-taking.
    Each line spans the full page width and is evenly spaced.
    :param doc: The Word document to which the ruled page will be added.
    :return: The modified Word document.
    """
    section = doc.add_section(start_type=WD_SECTION.NEW_PAGE)
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
    doc: DocxDocument, before_table_space: int = 0, after_table_space: int = 0
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


def add_footer(doc: DocxDocument) -> DocxDocument:
    section = doc.sections[0]
    footer = section.footer
    # Calculate usable content width
    assert section.page_width is not None
    assert section.left_margin is not None
    assert section.right_margin is not None
    usable_width = section.page_width - section.left_margin - section.right_margin
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
