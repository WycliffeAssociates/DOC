import re

import pytest
from doc.domain.parsing import ensure_chapter_label, ensure_chapter_marker


@pytest.mark.focus
def test_ensure_chapter_marker() -> None:
    chapter_num = 5

    # Case 1: Chapter marker already exists (should remain unchanged)
    existing_chapter = "\\c 5\nSome text."
    assert ensure_chapter_marker(existing_chapter, chapter_num) == existing_chapter

    # Case 2: No chapter marker, insert at beginning
    no_chapter_marker = "Some text without a chapter marker."
    expected_output = f"\\c {chapter_num}\nSome text without a chapter marker."
    assert ensure_chapter_marker(no_chapter_marker, chapter_num) == expected_output

    # Case 3: Chapter marker missing, but \cl exists (insert after \cl)
    text_with_cl = "\\cl Chapter Title\nSome text."
    expected_output = f"\\cl Chapter Title\n\\c {chapter_num}\n\nSome text."
    assert ensure_chapter_marker(text_with_cl, chapter_num) == expected_output

    # Case 4: Text with multiple lines, no \c, insert at start
    multiline_text = "Line 1\nLine 2\nLine 3"
    expected_output = f"\\c {chapter_num}\nLine 1\nLine 2\nLine 3"
    assert ensure_chapter_marker(multiline_text, chapter_num) == expected_output

    # Case 5: Text with \cl but no \c, should insert after \cl
    complex_text = "\\id mat\n\\cl Gospel of Matthew\nText starts here."
    expected_output = "\\id mat\n\\cl Gospel of Matthew\n\\c 5\n\nText starts here."
    assert ensure_chapter_marker(complex_text, chapter_num) == expected_output

    # Case 6: Text already has a different chapter number (should remain unchanged)
    existing_different_chapter = "\\c 10\nText continues."
    assert (
        ensure_chapter_marker(existing_different_chapter, chapter_num)
        == existing_different_chapter
    )


@pytest.mark.focus
def test_adds_missing_chapter_label() -> None:
    input_text = "\n\\c 1\n\\v 1 In the beginning..."
    expected_output = "\n\n\\cl Chapter\n\\c 1\n\n\\v 1 In the beginning..."
    actual_output = ensure_chapter_label(input_text, 1)
    print(repr(actual_output))  # Print raw string representation
    print(repr(expected_output))
    assert actual_output == expected_output


@pytest.mark.focus
def test_keeps_existing_chapter_label() -> None:
    input_text = "\n\\cl Chapter\n\\c 1\n\\v 1 In the beginning..."
    assert ensure_chapter_label(input_text, 1) == input_text


@pytest.mark.focus
def test_no_chapter_marker() -> None:
    input_text = "\n\\v 1 In the beginning..."
    assert ensure_chapter_label(input_text, 1) == input_text


if __name__ == "__main__":
    pytest.main()
