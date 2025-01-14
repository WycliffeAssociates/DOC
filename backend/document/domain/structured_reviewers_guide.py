from pprint import pprint
from collections import defaultdict
import re

# from dataclasses import dataclass, field
from typing import Optional
from docx import Document  # type: ignore
from document.domain.bible_books import BOOK_NAMES
from document.domain.model import (
    RGBook,
    RGChapter,
    LangDirEnum,
    Part1Item,
    Part2Item,
    BibleReference,
    ParsedText,
)

# You can download the en NT Survey reviewer's guide with something like:
# curl -L -o nt_survey.docx https://github.com/WycliffeAssociates/TS-biel-files/blob/master/training/en/Refinement%20and%20Publication/Reviewers'%20Guide/NT%20Survey%20RG%20Files/NT%20Survey%20Reviewers'%20Guide.docx

# Pattern for chapter and verse references after Bible books
CHAPTER_VERSE_PATTERN = re.compile(r"^\d+:\d+(-\d+(:\d+)?)?$")


def get_book_code(book_name: str) -> str:
    return next(key for key, name in BOOK_NAMES.items() if name == book_name)


def parse_bible_reference(
    raw_bible_reference: str, book_names: dict[str, str] = BOOK_NAMES
) -> Optional[BibleReference]:
    bible_reference = None
    bible_reference_components = raw_bible_reference.split()
    if len(bible_reference_components) == 2:
        book_name = bible_reference_components[0]
        book_code = get_book_code(book_name)
        chapter = bible_reference_components[1].split(":")[0]
        verse_ref = bible_reference_components[1].split(":")[1]
        bible_reference = BibleReference(
            book_code=book_code,
            book_name=book_name,
            chapter=int(chapter),
            verse_ref=verse_ref,
        )
    elif len(bible_reference_components) == 3:
        book_name = f"{bible_reference_components[0]} {bible_reference_components[1]}"
        book_code = get_book_code(book_name)
        chapter = bible_reference_components[2].split(":")[0]
        verse_ref = bible_reference_components[2].split(":")[1]
        bible_reference = BibleReference(
            book_code=book_code,
            book_name=book_name,
            chapter=int(chapter),
            verse_ref=verse_ref,
        )
    return bible_reference


def find_bible_references(
    docx_file: str, book_names: list[str] = list(BOOK_NAMES.values())
) -> tuple[list[str], list[str]]:
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
            and (words[0] in book_names or (f"{words[0]} {words[1]}" in book_names))
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


def parse_text(text: str, raw_bible_reference: str) -> ParsedText:
    """
    Parses the in-between text for a Bible passage reference into a structured dataclass.

    Args:
        text (str): The raw in-between text to be parsed.

    Returns:
        ParsedText: A dataclass containing the parsed content.
    """
    # parsed_data = ParsedText()
    bible_reference = parse_bible_reference(raw_bible_reference)
    text = text.replace(f"{raw_bible_reference} continued", "")
    sections = re.split(r"(Background:|Part 1|Part 2|Comment Section:)", text)
    current_section = None
    background = None
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
                background = (
                    section.removesuffix(directive).rstrip() if directive else section
                )
                # parsed_data.directive = directive if directive else None
            elif current_section == "part_1":
                part_1 = []
                part1_directive = get_first_sentence(section)
                bullets = re.findall(
                    r"(.*?)\s+\[(\d+:\d+(?:-\d+)?)\]",
                    section.removeprefix(part1_directive),
                )
                for bullet in bullets:
                    part_1.append(
                        Part1Item(text=bullet[0].strip(), reference=f"[{bullet[1]}]")
                    )
                # parsed_data.part_1_directive = part1_directive
            elif current_section == "part_2":
                part_2 = []
                part2_directive = get_first_sentence(section)
                qa_pattern = re.compile(
                    r"\[((?:\d+:\d+(?:-\d+)?(?:, \d+)*))\]\s+(.*?)\?(.*?)(?=\s*\[\d+:\d+(?:-\d+)?(?:, \d+)*\])"
                )
                questions_answers = qa_pattern.findall(
                    section.removeprefix(part2_directive)
                )
                for qa in questions_answers:
                    part_2.append(
                        Part2Item(
                            reference=f"[{qa[0]}]",
                            question=f"{qa[1].strip()}?",
                            answer=qa[2].strip(),
                        )
                    )
                # parsed_data.part_2_directive = part2_directive
            elif current_section == "comment_section":
                comment_section = None
            else:
                if section and background is None:
                    directive = section

    return ParsedText(
        bible_reference=bible_reference,
        background=background,
        directive=directive,
        part_1=part_1,
        part_1_directive=part1_directive,
        part_2=part_2,
        part_2_directive=part2_directive,
        comment_section=comment_section,
    )


def books(parsed_objects: list[ParsedText]) -> set[str]:
    return {po.bible_reference.book_code for po in parsed_objects if po.bible_reference}


def book(parsed_objects: list[ParsedText], book_code: str) -> set[ParsedText]:

    # Print only references for a particular book
    return {
        po
        for po in parsed_objects
        if po.bible_reference and po.bible_reference.book_code == book_code
    }


def chapter(parsed_objects: list[ParsedText], book_code: str) -> set[int]:
    # Print only references for a particular book
    return {
        po.bible_reference.chapter
        for po in parsed_objects
        if po.bible_reference
        and po.bible_reference.chapter
        and po.bible_reference.book_code == book_code
    }


def create_rgbooks_from_parsed_texts(
    parsed_texts: list[ParsedText],
    lang_code: str,
    lang_name: str,
    resource_type_name: str,
    lang_direction: LangDirEnum,
) -> list[RGBook]:
    # Group ParsedText by book_code and then by chapter
    books: dict[str, dict[int, list[ParsedText]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for parsed_text in parsed_texts:
        if parsed_text.bible_reference:
            book_code = parsed_text.bible_reference.book_code
            chapter = parsed_text.bible_reference.chapter
            books[book_code][chapter].append(parsed_text)

    # Create RGBook instances
    rgbooks: list[RGBook] = []

    for book_code, chapters_dict in books.items():
        chapters = {
            chapter_num: RGChapter(
                content=ParsedText(
                    bible_reference=chapter_texts[
                        0
                    ].bible_reference,  # Assuming one reference per chapter
                    background=" ".join(pt.background or "" for pt in chapter_texts),
                    directive=" ".join(pt.directive or "" for pt in chapter_texts),
                    part_1=[item for pt in chapter_texts for item in pt.part_1],
                    part_1_directive=" ".join(
                        pt.part_1_directive or "" for pt in chapter_texts
                    ),
                    part_2=[item for pt in chapter_texts for item in pt.part_2],
                    part_2_directive=" ".join(
                        pt.part_2_directive or "" for pt in chapter_texts
                    ),
                    comment_section=" ".join(
                        pt.comment_section or "" for pt in chapter_texts
                    ),
                )
            )
            for chapter_num, chapter_texts in chapters_dict.items()
        }

        rgbook = RGBook(
            lang_code=lang_code,
            lang_name=lang_name,
            book_code=book_code,
            resource_type_name=resource_type_name,
            chapters=chapters,
            lang_direction=lang_direction,
        )
        rgbooks.append(rgbook)

    return rgbooks


def get_rg_books(
    docx_file_path: str,
    lang_code: str,
    lang_name: str,
    resource_type_name: str,
    lang_direction: LangDirEnum,
) -> list[RGBook]:
    between_texts, bible_references = find_bible_references(docx_file_path)
    parsed_objects = [
        parse_text(text, ref) for text, ref in zip(between_texts, bible_references)
    ]
    rg_books = create_rgbooks_from_parsed_texts(
        parsed_objects, lang_code, lang_name, resource_type_name, lang_direction
    )
    return rg_books


if __name__ == "__main__":
    docx_file_path = "en_rg_nt_survey.docx"
    rg_books = get_rg_books(
        docx_file_path, "en", "English", "Reviewers' Guide NT Survey", LangDirEnum.LTR
    )
    for rg_book in rg_books:
        pprint(rg_book)

    # print("Bible References:")
    # for i, ref in enumerate(bible_references, 1):
    #     print(f"{i}: {ref}")

    # for i, parsed in enumerate(parsed_objects, 1):
    #     print(parsed.bible_reference)
    #     # print(f"Parsed Text {i}:\n{parsed}")
    #     pprint(parsed)
    #     print("\n")

    # Get all the books found in the reviewer's guide
    # print(books(parsed_objects))

    # Print only ParsedText instances for a particular book
    # for parsed in [
    #     po
    #     for po in parsed_objects
    #     if po.bible_reference and po.bible_reference.book_code == "mat"
    # ]:
    #     pprint(parsed)

    # mat_parsed_objects = book(parsed_objects, "mat")
    # pprint(mat_parsed_objects)

    # TODO Partition by chapter number
    # get the unique (set) chapter numbers then iterate by chapter
    # chapters = chapter(parsed_objects, "mat")
    # print("chapters ", chapters)

    # print("matthew chapter 6 parsed objects")
    # pprint(
    #     [
    #         po
    #         for po in book(parsed_objects, "mat")
    #         if po.bible_reference and po.bible_reference.chapter == 6
    #     ],
    # )

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
