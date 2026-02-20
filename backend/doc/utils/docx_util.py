import re
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import RGBColor
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from lxml.etree import _Element as Element


def generate_docx_toc(docx_filepath: str) -> str:
    """
    Create subdocument that contains only the code to generate (on
    first open of document) the table of contents.
    """
    toc_path = f"{Path(docx_filepath).with_suffix('')}_toc.docx"
    document = Document()
    paragraph = document.add_paragraph()
    run = paragraph.add_run()
    fldChar = OxmlElement("w:fldChar")
    fldChar.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = (
        r'TOC \o "1-2" \h \z \u'  # change 1-2 depending on heading levels you need
    )
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    fldChar3 = OxmlElement("w:t")
    fldChar3.text = (
        "Right-click to update field (doing so will insert table of contents)."
    )
    fldChar2.append(fldChar3)
    fldChar4 = OxmlElement("w:fldChar")
    fldChar4.set(qn("w:fldCharType"), "end")
    r_element = run._r
    r_element.append(fldChar)
    r_element.append(instrText)
    r_element.append(fldChar2)
    r_element.append(fldChar4)
    document.save(toc_path)
    return str(toc_path)


def preprocess_html_for_internal_docx_links(html: str) -> str:
    """
    Replace internal HTML anchors and headings with markers that survive HTML→DOCX conversion.
    Example:
      <h3 id="intro"> → {{BOOKMARK:intro}}
      <a href="#intro">Christ</a> → {{LINK_START:intro}}Christ{{LINK_END}}
    """
    # Mark bookmarks
    html = re.sub(
        r'<h3\s+id="([^"]+)">',
        r"{{BOOKMARK:\1}}<h3>",
        html,
        flags=re.IGNORECASE,
    )
    # Replace <a href="#id"> links
    html = re.sub(
        r'<a\s+href="#([^"]+)"><span>(.*?)</span></a>',
        r"{{LINK_START:\1}}\2{{LINK_END}}",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html = re.sub(
        r'<a\s+href="#([^"]+)">(.*?)</a>',
        r"{{LINK_START:\1}}\2{{LINK_END}}",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html


def _make_text_run(text: str) -> Element:
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = text
    # Ensure Word preserves leading/trailing spaces
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    return r


def _make_internal_hyperlink_element(text: str, bookmark_name: str) -> Element:
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("w:anchor"), bookmark_name)
    hyperlink.set(qn("w:history"), "1")
    r = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    r_style = OxmlElement("w:rStyle")
    r_style.set(qn("w:val"), "Hyperlink")
    r_pr.append(r_style)
    r.append(r_pr)
    t = OxmlElement("w:t")
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    hyperlink.append(r)
    return hyperlink


def _add_bookmark_to_run(run: Run, bookmark_name: str) -> None:
    """Add a DOCX bookmark around the given run in-place."""
    r = run._r
    p = r.getparent()
    if p is None:
        return
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), "0")
    start.set(qn("w:name"), bookmark_name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), "0")
    idx = p.index(r)
    p.insert(idx, start)
    p.insert(idx + 1, end)


def _replace_runs(para: Paragraph, new_elems: list[Element]) -> None:
    """
    Replace all runs in a paragraph with the provided XML elements.
    (Keeps paragraph element intact and appends supplied elements.)
    """
    for run in list(para.runs):
        p_r = run._r
        p = p_r.getparent()
        if p is not None and p_r in p:
            p.remove(p_r)
    for elem in new_elems:
        para._p.append(elem)


def add_internal_docx_links(doc: DocxDocument) -> None:
    """
    Convert {{BOOKMARK:name}} markers into bookmarks, and
    convert {{LINK_START:name}}...{{LINK_END}} sequences into internal links.
    Operates paragraph-by-paragraph using paragraph text aggregated
    from runs so punctuation/spaces are preserved.
    """
    bookmark_map: dict[str, str] = {}
    # Pass 1 — find and create bookmarks inside runs (remove marker text)
    bookmark_pattern = re.compile(r"\{\{BOOKMARK:([^}]+)\}\}")
    for para in doc.paragraphs:
        for run in para.runs:
            m = bookmark_pattern.search(run.text)
            if not m:
                continue
            name = m.group(1)
            # remove marker from run text
            run.text = bookmark_pattern.sub("", run.text).strip()
            # add bookmark around this run
            _add_bookmark_to_run(run, name)
            bookmark_map[name] = name
    # Pass 2 — replace LINK_START/LINK_END sequences at paragraph level
    # pattern matches sequences like {{LINK_START:name}}...{{LINK_END}}
    link_pattern = re.compile(
        r"\{\{LINK_START:([^}]+)\}\}(.*?)\{\{LINK_END\}\}", flags=re.DOTALL
    )
    for para in doc.paragraphs:
        # combine paragraph text from runs to preserve exact punctuation/spacing
        combined_text = "".join(run.text for run in para.runs)
        if "{{LINK_START:" not in combined_text:
            # nothing to do for this paragraph
            continue
        new_elements: list[Element] = []
        cursor = 0
        for m in link_pattern.finditer(combined_text):
            start, end = m.span()
            target = m.group(1)
            link_text = m.group(2)
            # add literal text before this link (commas, spaces, etc.)
            if start > cursor:
                literal = combined_text[cursor:start]
                if literal:
                    new_elements.append(_make_text_run(literal))
            # add hyperlink element or fallback to plain text if bookmark missing
            if target in bookmark_map:
                new_elements.append(_make_internal_hyperlink_element(link_text, target))
            else:
                new_elements.append(_make_text_run(link_text))
            cursor = end
        # trailing text after last link
        if cursor < len(combined_text):
            tail = combined_text[cursor:]
            if tail:
                new_elements.append(_make_text_run(tail))
        # replace the paragraph's runs with our constructed elements
        if new_elements:
            _replace_runs(para, new_elements)


def style_superscripts(
    doc: DocxDocument,
    *,
    lift_half_points: int = 2,
    color: RGBColor = RGBColor(0x66, 0x66, 0x66),
) -> None:
    """
    lift_half_points:
        2 = +1pt
        4 = +2pt
        6 = +3pt

    color:
        RGBColor for superscripts (e.g. light gray)
    """
    for para in doc.paragraphs:
        for run in para.runs:
            if run.font.superscript:
                # --- Color ---
                run.font.color.rgb = color
                # --- Vertical position ---
                rPr = run._r.get_or_add_rPr()
                position = OxmlElement("w:position")
                position.set(qn("w:val"), str(lift_half_points))
                rPr.append(position)


def _ensure_character_style_based_on_default(
    doc: DocxDocument,
    name: str,
    *,
    color: RGBColor | None = None,
    italic: bool | None = None,
) -> None:
    styles = doc.styles
    if name in styles:
        return
    style = styles.add_style(name, WD_STYLE_TYPE.CHARACTER)
    # ---- Base on Default Paragraph Font ----
    style_elm = style._element
    based_on = OxmlElement("w:basedOn")
    based_on.set(qn("w:val"), "DefaultParagraphFont")
    style_elm.insert(0, based_on)
    # ---- Only override what is explicitly requested ----
    font = style.font
    if color is not None:
        font.color.rgb = color
    if italic is not None:
        font.italic = italic


def ensure_reference_styles(
    doc: DocxDocument,
    *,
    available_color: RGBColor | None = None,
    unavailable_color: RGBColor,
) -> None:
    """
    Create semantic character styles for passage references.

    AvailableReference:
        - Based on Default Paragraph Font
        - Usually no overrides (inherits document defaults)

    UnavailableReference:
        - Based on Default Paragraph Font
        - Lighter color + italics to signal intentional absence
    """
    _ensure_character_style_based_on_default(
        doc,
        "AvailableReference",
        color=available_color,  # usually None
    )
    _ensure_character_style_based_on_default(
        doc,
        "UnavailableReference",
        color=unavailable_color,
        italic=True,
    )
