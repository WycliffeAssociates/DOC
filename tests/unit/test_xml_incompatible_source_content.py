"""
Source content sometimes contains characters that can't appear in XML,
e.g., NULL bytes in the refinement_malawi nyr and nyu-ML-nyungwe repos,
which made docx generation fail with "ValueError: All strings must be XML
compatible". These tests check that such characters are removed from the
USFM content before it is used.
"""

from glob import glob
from os.path import join
from pathlib import Path

import pytest
from doc.domain import parsing
from doc.domain.model import LangDirEnum, ResourceLookupDto
from doc.domain.parsing import (
    extract_usfm_frontmatter,
    get_book_name,
    read_chapter_label,
    usfm_book_content,
)
from pydantic import HttpUrl

NULLS = "\x00" * 11


def _act_resource_lookup_dto() -> ResourceLookupDto:
    return ResourceLookupDto(
        lang_code="nyr",
        lang_name="Nyiha, Malawi",
        localized_lang_name="Nyiha, Malawi",
        resource_type="reg",
        resource_type_name="Regular",
        book_code="act",
        lang_direction=LangDirEnum.LTR,
        url=HttpUrl(
            "https://content.bibletranslationtools.org/refinement_malawi/nyr_act_text_reg"
        ),
    )


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_extract_usfm_frontmatter_empty_h_does_not_capture_next_line() -> None:
    # Before the fix, an empty \h captured the following "\c 1" line as
    # the book name.
    assert extract_usfm_frontmatter("\\ide UTF-8\n\\h \n\n\\c 1\n\\v 1 Paulo") == {}


def test_get_book_name_falls_back_to_english_for_null_only_title(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "front" / "title.txt", "\x00" * 6)
    assert get_book_name(str(tmp_path), _act_resource_lookup_dto()) == "Acts"


def test_get_book_name_removes_null_bytes(tmp_path: Path) -> None:
    # Pattern from refinement_malawi/nyr_1co_text_reg/front/title.txt
    _write(tmp_path / "front" / "title.txt", f"{NULLS}1  Vakolinti")
    assert get_book_name(str(tmp_path), _act_resource_lookup_dto()) == "1 Vakolinti"


def test_read_chapter_label_removes_null_bytes(tmp_path: Path) -> None:
    # Pattern from refinement_malawi/nyr_luk_text_reg/18/title.txt
    title_file = tmp_path / "18" / "title.txt"
    _write(title_file, f"{NULLS}Chaputa 18")
    assert read_chapter_label(str(title_file)) == "Chaputa"


def test_read_chapter_label_null_only_title_is_none(tmp_path: Path) -> None:
    title_file = tmp_path / "18" / "title.txt"
    _write(title_file, NULLS)
    assert read_chapter_label(str(title_file)) is None


@pytest.mark.parametrize("use_chapter_labels", [False, True])
def test_usfm_book_content_removes_null_bytes_from_verses_and_titles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    use_chapter_labels: bool,
) -> None:
    # Mimic the layout of refinement_malawi/nyr_act_text_reg, whose
    # 15/12.txt is "\v 12 " followed by NULL bytes.
    resource_dir = tmp_path / "nyr_act_text_reg"
    _write(resource_dir / "front" / "title.txt", NULLS)
    _write(resource_dir / "15" / "title.txt", f"{NULLS}Chaputa 15")
    _write(resource_dir / "15" / "01.txt", "\\c 15 \\v 1 Vantu vamo")
    _write(resource_dir / "15" / "12.txt", f"\\v 12 {NULLS * 15}")
    working_dir = tmp_path / "working"
    working_dir.mkdir()
    # The USFM to HTML conversion is done by a separate service which
    # isn't available in unit tests; the chapter USFM it would be given
    # is written to working_dir and checked below.
    monkeypatch.setattr(
        parsing, "convert_usfm_chapter_to_html", lambda *args, **kwargs: None
    )

    usfm_book = usfm_book_content(
        _act_resource_lookup_dto(),
        str(resource_dir),
        use_chapter_labels,
        working_dir=str(working_dir),
        use_localized_book_name=True,
    )

    assert usfm_book.national_book_name == "Acts"
    chapter_usfm_files = glob(join(str(working_dir), "*.usfm"))
    assert chapter_usfm_files
    for chapter_usfm_file in chapter_usfm_files:
        chapter_usfm = Path(chapter_usfm_file).read_text(encoding="utf-8")
        assert "\x00" not in chapter_usfm
        assert "\\v 12" in chapter_usfm
        if use_chapter_labels:
            assert "\\cl Chaputa 15" in chapter_usfm
