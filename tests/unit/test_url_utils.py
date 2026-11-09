from pathlib import Path

from doc.utils.url_utils import get_book_name_from_title_file


def _write_title_file(resource_dir: Path, content: bytes) -> None:
    front_dir = resource_dir / "front"
    front_dir.mkdir(parents=True)
    (front_dir / "title.txt").write_bytes(content)


def test_get_book_name_from_title_file_with_only_null_bytes(tmp_path: Path) -> None:
    # Reproduces refinement_malawi/nyu-ML-nyungwe_eph_text_reg whose
    # front/title.txt contained nothing but NULL bytes which caused
    # python-docx to raise a ValueError when writing the book name.
    _write_title_file(tmp_path, b"\x00" * 6)
    book_name = get_book_name_from_title_file(
        str(tmp_path), "nyu-ML-nyungwe", ["nyu-ML-nyungwe", "eph", "text", "reg"]
    )
    assert book_name == ""


def test_get_book_name_from_title_file_strips_null_bytes_and_whitespace(
    tmp_path: Path,
) -> None:
    _write_title_file(tmp_path, b"Aefeso\x00\n")
    book_name = get_book_name_from_title_file(
        str(tmp_path), "nyu-ML-nyungwe", ["nyu-ML-nyungwe", "eph", "text", "reg"]
    )
    assert book_name == "Aefeso"


def test_get_book_name_from_title_file_with_valid_name(tmp_path: Path) -> None:
    _write_title_file(tmp_path, "Mabasa ya atumwi\n".encode("utf-8"))
    book_name = get_book_name_from_title_file(
        str(tmp_path), "nyu-ML-nyungwe", ["nyu-ML-nyungwe", "act", "text", "reg"]
    )
    assert book_name == "Mabasa ya atumwi"


def test_get_book_name_from_title_file_missing_file(tmp_path: Path) -> None:
    book_name = get_book_name_from_title_file(
        str(tmp_path), "nyu-ML-nyungwe", ["nyu-ML-nyungwe", "eph", "text", "reg"]
    )
    assert book_name == ""
