from pprint import pprint
import re
from dataclasses import dataclass, field
from typing import Optional
from docx import Document

# You can download the en NT Survey reviewer's guide with something like:
# curl -L -o nt_survey.docx https://github.com/WycliffeAssociates/TS-biel-files/blob/master/training/en/Refinement%20and%20Publication/Reviewers'%20Guide/NT%20Survey%20RG%20Files/NT%20Survey%20Reviewers'%20Guide.docx

# List of Bible book names to recognize Bible references
BIBLE_BOOKS = {
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Proverbs",
    "Ecclesiastes",
    "Song of Songs",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation",
}

# Pattern for chapter and verse references after Bible books
CHAPTER_VERSE_PATTERN = re.compile(r"^\d+:\d+(-\d+(:\d+)?)?$")


@dataclass
class Part1Item:
    text: str
    reference: str


@dataclass
class Part2Item:
    reference: str
    question: str
    answer: str


@dataclass
class ParsedText:
    bible_reference: Optional[str] = None
    background: Optional[str] = None
    directive: Optional[str] = None
    part_1: list[Part1Item] = field(default_factory=list)
    part_1_directive: Optional[str] = None
    part_2: list[Part2Item] = field(default_factory=list)
    part_2_directive: Optional[str] = None
    comment_section: Optional[str] = None


def find_bible_references(docx_file: str) -> tuple[list[str], list[str]]:
    """
    Identifies Bible passage references and text between references.

    Bible passage references:
        - Start with a Bible book name.
        - Are followed by a valid chapter and verse reference, e.g., "3:16-17".
        - Do not end with the word "continued".

    Args:
        docx_file (str): Path to the Word (.docx) file.

    Returns:
        tuple[list[str], list[str]]:
            - The first list contains text found between Bible references.
            - The second list contains the Bible references themselves.
    """
    doc = Document(docx_file)

    between_texts: list[str] = []
    bible_references: list[str] = []
    current_text: list[str] = []
    inside_bible_reference: bool = False

    for paragraph in doc.paragraphs:
        # Check if the paragraph is a potential Bible reference
        paragraph_text = paragraph.text.strip()
        # print("paragraph_text: ", paragraph_text)
        words = paragraph_text.split()
        if (
            words
            and len(words) > 1
            and len(words) < 5
            and (words[0] in BIBLE_BOOKS or (f"{words[0]} {words[1]}" in BIBLE_BOOKS))
        ):
            if (
                paragraph_text.endswith("continued") or "\t" in paragraph_text
            ):  # \t is in paragraph_text when it is a TOC entry
                # print("paragraph_text: ", paragraph_text)
                continue
            if inside_bible_reference:
                if current_text:
                    between_texts.append(" ".join(current_text))
                    current_text = []
            bible_references.append(paragraph_text)
            # print("bible reference: ", paragraph_text)
            inside_bible_reference = True
            continue
        if inside_bible_reference:
            current_text.append(paragraph_text)
    if current_text:
        between_texts.append(" ".join(current_text))
    return between_texts, bible_references


def get_last_sentence(text: str) -> str:
    # Use regex to match sentences instead of splitting, so punctuation is preserved
    sentences = re.findall(r"[^\s].*?[.?!](?=\s|$)", text.strip())
    # Return the last sentence if any are found, or an empty string otherwise
    return sentences[-1] if sentences else ""


def get_first_sentence(text: str) -> str:
    # Use regex to match sentences instead of splitting, so punctuation is preserved
    sentences = re.findall(r"[^\s].*?[.?!](?=\s|$)", text.strip())
    # Return the last sentence if any are found, or an empty string otherwise
    return sentences[0] if sentences else ""


def parse_text(text: str, bible_reference: str) -> ParsedText:
    """
    Parses the in-between text for a Bible passage reference into a structured dataclass.

    Args:
        text (str): The raw in-between text to be parsed.

    Returns:
        ParsedText: A dataclass containing the parsed content.
    """
    parsed_data = ParsedText()
    parsed_data.bible_reference = bible_reference
    text = text.replace(f"{bible_reference} continued", "")
    sections = re.split(r"(Background:|Part 1|Part 2|Comment Section:)", text)
    current_section = None
    for section in sections:
        section = section.strip()
        if section == "Background:":
            current_section = "background"
        elif section == "Part 1":
            current_section = "part_1"
        elif section == "Part 2":
            current_section = "part_2"
        elif section == "Comment Section:":
            current_section = "comment_section"
        else:
            if current_section == "background":
                directive = get_last_sentence(section)
                parsed_data.background = (
                    section.removesuffix(directive).rstrip() if directive else section
                )
                parsed_data.directive = directive if directive else None
            elif current_section == "part_1":
                part1_directive = get_first_sentence(section)
                bullets = re.findall(
                    r"(.*?)\s+\[(\d+:\d+(?:-\d+)?)\]",
                    section.removeprefix(part1_directive),
                )
                for bullet in bullets:
                    parsed_data.part_1.append(
                        Part1Item(text=bullet[0].strip(), reference=f"[{bullet[1]}]")
                    )
                parsed_data.part_1_directive = part1_directive
            elif current_section == "part_2":
                part2_directive = get_first_sentence(section)
                qa_pattern = re.compile(
                    r"\[((?:\d+:\d+(?:-\d+)?(?:, \d+)*))\]\s+(.*?)\?(.*?)(?=\s*\[\d+:\d+(?:-\d+)?(?:, \d+)*\])"
                )
                questions_answers = qa_pattern.findall(
                    section.removeprefix(part2_directive)
                )
                for qa in questions_answers:
                    parsed_data.part_2.append(
                        Part2Item(
                            reference=f"[{qa[0]}]",
                            question=f"{qa[1].strip()}?",
                            answer=qa[2].strip(),
                        )
                    )
                parsed_data.part_2_directive = part2_directive
            elif current_section == "comment_section":
                parsed_data.comment_section = None
            else:
                if section and parsed_data.background is None:
                    parsed_data.directive = section
    return parsed_data


if __name__ == "__main__":
    docx_file_path = "NT Survey Reviewers' Guide.docx"
    between_texts, bible_references = find_bible_references(docx_file_path)
    # print("Bible References:")
    # for i, ref in enumerate(bible_references, 1):
    #     print(f"{i}: {ref}")

    # print("\nParsed In-Between Texts:")
    parsed_objects = [
        parse_text(text, ref) for text, ref in zip(between_texts, bible_references)
    ]
    for i, parsed in enumerate(parsed_objects, 1):
        print(parsed.bible_reference)
        # print(f"Parsed Text {i}:\n{parsed}")
        pprint(parsed)
        print("\n")

    # print("len(bible_references)", len(bible_references))
    # print("len(between_texts)", len(between_texts))

    # for parsed in parsed_objects:
    #     print("parsed: ", parsed)

    # print("\nDirective:")
    # print(directive if directive else "No directive found.")

    # text1 = "Hello world! How are you doing today? This is the final sentence."
    # assert get_last_sentence(text1) == "This is the final sentence."

    # text2 = "Another example sentence without issues."
    # assert get_last_sentence(text2) == "Another example sentence without issues."

    # text3 = "No punctuation here"
    # assert get_last_sentence(text3) == ""

    # text4 = "Single word."
    # assert get_last_sentence(text4) == "Single word."

    # text5 = "Empty input:"
    # assert get_last_sentence("") == ""

    # text6 = "End with whitespace?   "
    # assert get_last_sentence(text6) == "End with whitespace?"

    # part1_directive = get_first_sentence(
    #     "This is a directive. I think you can see what I mean."
    # )
    # assert part1_directive == "This is a directive."
