import re

import pytest
from doc.domain.parsing import (
    ensure_chapter_label,
    ensure_chapter_marker,
    maybe_localized_book_name,
)
from doc.domain import model, resource_lookup


def test_ensure_chapter_marker_unchanged_if_exists() -> None:
    chapter_num = 5

    # Case 1: Chapter marker already exists (should remain unchanged)
    existing_chapter = "\\c 5\nSome text."
    assert ensure_chapter_marker(existing_chapter, chapter_num) == existing_chapter

    # Case 6: Text already has a different chapter number (should remain unchanged)
    existing_different_chapter = "\\c 10\nText continues."
    assert (
        ensure_chapter_marker(existing_different_chapter, chapter_num)
        == existing_different_chapter
    )


def test_ensure_chapter_marker_inserted_at_beginning() -> None:
    chapter_num = 5
    # Case 2: No chapter marker, insert at beginning
    no_chapter_marker = "Some text without a chapter marker."
    expected_output = f"\\c {chapter_num}\nSome text without a chapter marker."
    actual_output = ensure_chapter_marker(no_chapter_marker, chapter_num)
    print("actual: " + repr(actual_output))  # Print raw string representation
    print("expected: " + repr(expected_output))
    assert actual_output == expected_output

    # Case 4: Text with multiple lines, no \c, insert at start
    multiline_text = "Line 1\nLine 2\nLine 3"
    expected_output = f"\\c {chapter_num}\nLine 1\nLine 2\nLine 3"
    actual_output = ensure_chapter_marker(multiline_text, chapter_num)
    print("actual: " + repr(actual_output))  # Print raw string representation
    print("expected: " + repr(expected_output))
    assert actual_output == expected_output


def test_ensure_chapter_marker_inserted_at_before_chapter_label() -> None:
    chapter_num = 5
    # Case 3: Chapter marker missing, but \cl exists (insert before \cl)
    text_with_cl = "\\cl Chapter Title\nSome text."
    expected_output = f"\n\\c {chapter_num}\n\\cl Chapter Title\nSome text."
    actual_output = ensure_chapter_marker(text_with_cl, chapter_num)
    print("actual: " + repr(actual_output))  # Print raw string representation
    print("expected: " + repr(expected_output))
    assert actual_output == expected_output


def test_ensure_chapter_marker_inserted() -> None:
    chapter_num = 5

    # Case 5: Text with \cl but no \c, should insert before \cl
    complex_text = "\\id mat\n\\cl Gospel of Matthew\nText starts here."
    expected_output = "\\id mat\n\n\\c 5\n\\cl Gospel of Matthew\nText starts here."
    actual_output = ensure_chapter_marker(complex_text, chapter_num)
    print("actual: " + repr(actual_output))  # Print raw string representation
    print("expected: " + repr(expected_output))
    assert actual_output == expected_output


def test_adds_missing_chapter_label() -> None:
    input_text = "\n\\c 1\n\\v 1 In the beginning..."
    expected_output = "\n\n\\c 1\n\\cl Chapter 1\n\n\\v 1 In the beginning..."
    actual_output = ensure_chapter_label(input_text, 1)
    print("actual: " + repr(actual_output))  # Print raw string representation
    print("expected: " + repr(expected_output))
    assert actual_output == expected_output


def test_keeps_existing_chapter_label() -> None:
    input_text = "\n\\c 1\n\\cl Chapter\n\\v 1 In the beginning..."
    expected_output = "\n\\c 1\n\\cl Chapter 1\n\\v 1 In the beginning..."
    assert ensure_chapter_label(input_text, 1) == expected_output


def test_no_chapter_marker() -> None:
    input_text = "\n\\v 1 In the beginning..."
    assert ensure_chapter_label(input_text, 1) == input_text


def test_fr_f10_book_name_lookup_prefs() -> None:
    usfm_metadata = r"""\id JUD
\h ÉPÎTRE DE SAINT JUDE
\toc1 ÉPÎTRE DE SAINT JUDE
\toc2 Épître de Jude
\toc3 Jude
\mt1 ÉPÎTRE DE SAINT JUDE

\s5
"""
    expected = "Épître de Jude"
    localized_book_name = maybe_localized_book_name(usfm_metadata, "fr", "f10")
    assert localized_book_name != "Épître de saint jude"
    assert localized_book_name == expected


if __name__ == "__main__":
    pytest.main()
