"""
This module provides an API for parsing content.
"""

import re
import subprocess
import time
from glob import glob
from os import getenv, scandir, walk, DirEntry
from os.path import exists, join, split
from pathlib import Path
from typing import Mapping, Optional, Sequence

import mistune
from doc.config import settings
from doc.domain.assembly_strategies.assembly_strategy_utils import (
    adjust_commentary_headings,
)
from doc.domain.bible_books import BOOK_NAMES
from doc.domain.exceptions import MissingChapterMarkerError
from doc.domain.model import (
    BC_RESOURCE_TYPE,
    EN_TN_CONDENSED_RESOURCE_TYPE,
    RG_RESOURCE_TYPE,
    TN_RESOURCE_TYPE,
    TQ_RESOURCE_TYPE,
    TW_RESOURCE_TYPE,
    BCBook,
    BCChapter,
    ChapterNum,
    ResourceLookupDto,
    ResourceRequest,
    TNBook,
    TNChapter,
    TQBook,
    TQChapter,
    TWBook,
    TWNameContentPair,
    USFMBook,
    USFMChapter,
    VerseRef,
)
from doc.domain.usfm_error_detection_and_fixes import (
    RESOURCES_WITH_USFM_DEFECTS,
    fix_usfm,
)
from doc.markdown_transforms import markdown_transformer
from doc.reviewers_guide.model import RGBook
from doc.reviewers_guide.parser import get_rg_books
from doc.utils.file_utils import read_file
from doc.utils.text_utils import (
    chapter_label_numeric_part,
    chapter_label_sans_numeric_part,
    normalize_localized_book_name,
)
from doc.utils.tw_utils import (
    localized_translation_word,
    translation_word_filepaths,
    translation_words_dict,
    tw_resource_dir,
)

logger = settings.logger(__name__)

H1, H2, H3, H4, H5 = "h1", "h2", "h3", "h4", "h5"

# fmt: off
BC_ARTICLE_URL_FMT_STR: str = "https://content.bibletranslationtools.org/WycliffeAssociates/en_bc/src/branch/master/{}"
# fmt: on


# CHAPTER_LABEL_REGEX = r"\\cl\s+.*"
CHAPTER_LABEL_REGEX = re.compile(r"\\cl\s+[^\n]+")
CHAPTER_LABEL_REGEX2 = re.compile(r"\\cl\s+(.+)")
CHAPTER_REGEX = re.compile(r"\\c\s+\d+")
CHAPTER_CAPTURE_REGEX = re.compile(r"(\\c\s+\d+)")
CHAPTER_CAPTURE_REGEX2 = re.compile(r"\\c\s+(\d+)")


def find_usfm_files(
    resource_dir: str,
    usfm_glob_fmt_str: str = "{}**/*.usfm",
    usfm_ending_in_txt_glob_fmt_str: str = "{}**/*.txt",
    usfm_ending_in_txt_in_subdirectory_glob_fmt_str: str = "{}**/**/*.txt",
) -> list[str]:
    usfm_files = glob(usfm_glob_fmt_str.format(resource_dir))
    if not usfm_files:
        # USFM files sometimes have txt suffix instead of usfm
        usfm_files = glob(usfm_ending_in_txt_glob_fmt_str.format(resource_dir))
        # Sometimes the txt USFM files live at another location
        if not usfm_files:
            usfm_files = glob(
                usfm_ending_in_txt_in_subdirectory_glob_fmt_str.format(resource_dir)
            )
    # Exclude "title.txt" from the results
    usfm_files = [
        filepath for filepath in usfm_files if not filepath.endswith("title.txt")
    ]
    return usfm_files


def filter_usfm_files(
    content_files: list[str],
    book_code: str,
    usfm_suffix: str = ".usfm",
    txt_suffix: str = ".txt",
) -> list[str]:
    suffix_of_content_files = str(Path(content_files[0]).suffix)
    if suffix_of_content_files == usfm_suffix:
        return [
            content_file
            for content_file in content_files
            if book_code.lower() in str(Path(content_file).stem).lower()
        ]
    elif suffix_of_content_files == txt_suffix:
        return [
            content_file
            for content_file in content_files
            if book_code.lower() in str(content_file).lower()
        ]
    return []


def write_usfm_content_to_file(content: str, filepath_sans_suffix: str) -> str:
    filepath = f"{filepath_sans_suffix}.usfm"
    with open(filepath, "w") as fp:
        fp.write(content)
    return filepath


def print_directory_contents(directory: str) -> None:
    """
    Useful for debugging layout on Github Action virtual machine
    """
    for root, dirs, files in walk(directory):
        logger.debug("Directory: %s", root)
        for file in files:
            logger.debug("  File: %s", file)
        for dir in dirs:
            logger.debug("  Subdirectory: %s", dir)


def convert_usfm_chapter_to_html(
    content: str,
    resource_filepath_sans_suffix: str,
) -> None:
    """
    Invoke the dotnet USFM parser to parse the USFM file, if it exists,
    and render it into HTML and store on disk.
    """
    content_file = write_usfm_content_to_file(content, resource_filepath_sans_suffix)
    logger.info("About to convert USFM to HTML")
    dll_path = "/app/USFMParserDriver/bin/Release/net8.0/USFMParserDriver.dll"
    if not exists(f"{getenv('DOTNET_ROOT')}/dotnet"):
        logger.info("dotnet cli not found!")
        raise Exception("dotnet cli not found")
    if not exists(dll_path):
        logger.info("dotnet parser executable not found!")
        # print_directory_contents("/app/USFMParserDriver")
        raise Exception("dotnet parser executable not found!")
    if not exists(content_file):
        logger.info("dotnet parser expects %s to exist, but it does not!", content_file)
    command = [
        f"{getenv('DOTNET_ROOT')}/dotnet",
        dll_path,
        f"/app/{content_file}",
        f"/app/{resource_filepath_sans_suffix}.html",
    ]
    logger.info("dotnet command: %s", " ".join(command))
    subprocess.run(
        command,
        check=True,
        text=True,
    )


def usfm_asset_file(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    usfm_glob_fmt_str: str = "{}**/*.usfm",
    usfm_ending_in_txt_glob_fmt_str: str = "{}**/*.txt",
    usfm_ending_in_txt_in_subdirectory_glob_fmt_str: str = "{}**/**/*.txt",
) -> Optional[str]:
    """
    Find the USFM asset and return its path as string or
    None if path not found.
    """
    usfm_files = find_usfm_files(resource_dir)
    filtered_usfm_files: list[str] = []
    if usfm_files:
        filtered_usfm_files = filter_usfm_files(
            usfm_files, resource_lookup_dto.book_code
        )
    if filtered_usfm_files:
        logger.debug("filtered_usfm_files: %s", filtered_usfm_files)
        # A USFM git repo can have each USFM chapter in a separate directory and
        # each verse span in a separate file in that directory. We concatenate the
        # book's USFM files into one USFM file.
        if len(filtered_usfm_files) > 1:
            return combine_usfm_files(resource_dir, resource_lookup_dto)
        else:
            return filtered_usfm_files[0]
    return None


def usfm_chapter_html(
    content: str,
    resource_lookup_dto: ResourceLookupDto,
    chapter_num: int,
    working_dir: str = settings.WORKING_DIR,
) -> Optional[str]:
    resource_filepath_sans_suffix = f"{working_dir}/{resource_lookup_dto.lang_code}_{resource_lookup_dto.resource_type}_{resource_lookup_dto.book_code}_{chapter_num}"
    t0 = time.time()
    convert_usfm_chapter_to_html(content, resource_filepath_sans_suffix)
    t1 = time.time()
    logger.info(
        "Time to convert USFM to HTML for %s-%s-%s: %s",
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_lookup_dto.book_code,
        t1 - t0,
    )
    html_content_filepath = f"{resource_filepath_sans_suffix}.html"
    if exists(html_content_filepath):
        html_content = read_file(html_content_filepath)
        return html_content
    return None


def remove_links(html: str) -> str:
    """
    Turn HTML links into spans
    """
    html = html.replace("<a ", "<span ").replace("</a>", "</span>")
    return html


def split_usfm_by_chapters(
    lang_code: str,
    resource_type: str,
    book_code: str,
    usfm_text: str,
    chapter_regex: re.Pattern[str] = CHAPTER_REGEX,
    # chapter_label_regex: re.Pattern[str] = CHAPTER_LABEL_REGEX,
    resources_with_usfm_defects: Sequence[
        tuple[str, str, str]
    ] = RESOURCES_WITH_USFM_DEFECTS,
    check_usfm: bool = settings.CHECK_USFM,
    check_all_books_for_language: bool = settings.CHECK_ALL_BOOKS_FOR_LANGUAGE,
) -> tuple[str, list[str], list[str]]:
    r"""
    Split the USFM text into chapters
    """
    chapter_markers = []
    chapters = []
    chapter_markers = re.findall(chapter_regex, usfm_text)
    chapters = re.split(chapter_regex, usfm_text)
    frontmatter = chapters.pop(0).strip()
    logger.debug("chapter_markers: %s", chapter_markers)

    def needs_fixing() -> bool:
        """
        Determine if a chapter needs fixing based on configuration.
        """
        if check_all_books_for_language:
            return lang_code in [
                resource[0] for resource in resources_with_usfm_defects
            ]
        return (
            lang_code,
            resource_type,
            book_code,
        ) in resources_with_usfm_defects

    updated_chapters = []
    for marker, chapter in zip(chapter_markers, chapters):
        stripped_chapter = chapter.lstrip()
        # logger.debug("stripped_chapter[0:60]: %s", stripped_chapter[0:60])
        if stripped_chapter:
            if check_usfm and needs_fixing():
                stripped_chapter = fix_usfm(
                    stripped_chapter, lang_code, resource_type, book_code
                )
                # updated_chapter = marker + "\n" + stripped_chapter
                # logger.debug("updated_chapter[0:60]: %s", updated_chapter[0:60])
            updated_chapters.append(marker + "\n" + stripped_chapter)
    return frontmatter, chapter_markers, updated_chapters


def ensure_chapter_label(
    chapter_usfm_text: str,
    chapter_num: int,
    # chapter_label_regex: re.Pattern[str] = CHAPTER_LABEL_REGEX,
    # chapter_regex: re.Pattern[str] = CHAPTER_REGEX,
) -> str:
    r"""
    Modify USFM source to insert an English chapter label if it does not have one.
    Ensure that the chapter label includes the chapter number.
    """
    # if not re.search(chapter_label_regex, chapter_usfm_text):
    if not re.search(r"\\cl\s+[^\n]+", chapter_usfm_text):
        # if re.search(chapter_regex, chapter_usfm_text):
        if re.search(r"\\c\s+\d+", chapter_usfm_text):
            chapter_usfm_text = re.sub(
                r"(\\c\s+\d+)",
                "\n" + r"\1" + "\n" + r"\\cl Chapter " + f"{chapter_num}" + "\n",
                chapter_usfm_text,
            )
            return chapter_usfm_text
    # Ensure chapter label contains the chapter number
    match = re.search(r"\\cl\s+(.+)", chapter_usfm_text)
    if match:
        label_text = match.group(1)
        if str(chapter_num) not in label_text:
            updated_label = f"{label_text} {chapter_num}"
            chapter_usfm_text = re.sub(
                r"\\cl\s+(.+)",  # <--- FIXED
                rf"\\cl {updated_label}",
                chapter_usfm_text,
            )
            return chapter_usfm_text
    logger.debug(
        "Chapter label already existed and contained the chapter number, didn't modify it"
    )
    return chapter_usfm_text


# def ensure_chapter_label(
#     chapter_usfm_text: str,
#     chapter_num: int,
#     chapter_label_regex: re.Pattern[str] = CHAPTER_LABEL_REGEX,
#     chapter_capture_regex: re.Pattern[str] = CHAPTER_CAPTURE_REGEX,
# ) -> str:
#     r"""
#     Modify USFM source to insert a chapter label, \cl Chapter <chapter_num>, if it does not have one.
#     Ensures consistent newline formatting.
#     """
#     if not re.search(chapter_label_regex, chapter_usfm_text):
#         match = re.search(chapter_capture_regex, chapter_usfm_text)
#         if match:
#             chapter_marker = match.group(1)
#             updated_text = re.sub(
#                 # chapter_capture_regex,
#                 r"(\\c\s+\d+)",
#                 rf"\n\n\cl Chapter\n{chapter_marker}\n",
#                 chapter_usfm_text,
#             )
#             return updated_text.strip("\n")  # Ensures no extra newlines at start or end
#     logger.debug("chapter label already existed, didn't add one")
#     return chapter_usfm_text


def ensure_no_chapter_labels(
    chapter_usfm_text: str,
    chapter_label_regex: re.Pattern[str] = CHAPTER_LABEL_REGEX,
) -> str:
    r"""
    Modify USFM source to remove all chapter labels, \cl.
    """
    if re.search(chapter_label_regex, chapter_usfm_text):
        updated_chapter_usfm_text = re.sub(
            chapter_label_regex,
            "",
            chapter_usfm_text,
        )
        return updated_chapter_usfm_text
    return chapter_usfm_text


def get_chapter_num(
    chapter_usfm_text: str,
    chapter_regex: re.Pattern[str] = CHAPTER_CAPTURE_REGEX2,
) -> int:
    """Get the chapter number from the USFM chapter source text."""
    if match := re.search(chapter_regex, chapter_usfm_text):
        chapter_num = match.group(1)
        return int(chapter_num)
    return -1  # return sentinal


def remove_null_bytes_and_control_characters(html_content: Optional[str]) -> str:
    """
    Remove any NULL bytes and all control characters.

    Some languages' accidentally have ASCI control characters in their
    USFM. We strip those out as well as the possibility of ASCII NULL
    bytes.
    """
    return re.sub(r"[\x00-\x1F]+", "", html_content) if html_content else ""


def extract_usfm_frontmatter(frontmatter: str) -> dict[str, str]:
    # Define the regex patterns to match \h, \mt, and \toc
    patterns = {
        "h": r"\\h\s+(.*?)(?=\s+\\|\n|$)",
        "mt": r"\\mt\s+(.*?)(?=\s+\\|\n|$)",
        "toc1": r"\\toc1\s+(.*?)(?=\s+\\|\n|$)",
        "toc2": r"\\toc2\s+(.*?)(?=\s+\\|\n|$)",
    }
    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, frontmatter, re.MULTILINE)
        if match:
            extracted_data[key] = match.group(1).strip()
    return extracted_data


def maybe_localized_book_name(frontmatter: str) -> str:
    r"""
    Rule for obtaining localized book name:

    In USFM:

    1. Look to see if the \h marker is present — if so, use that value.
    2. Else look to see if the \mt1 marker is present — if so, use that value.
    3. Else look to see if the \toc1 marker is present - if so, use that value.
    4. Else look to see if the \toc2 marker is present - if so, use that value.

    Outside USFM:

    5. Else use the book name from the source language if available.
    6. Otherwise use the English book name.

    Steps 5 and 6 happen outside this function.
    """
    # logger.debug("frontmatter: %s", frontmatter)
    frontmatter_data = extract_usfm_frontmatter(frontmatter)
    localized_book_name = (
        frontmatter_data.get("h")
        or frontmatter_data.get("mt")
        or frontmatter_data.get("toc1")
        or frontmatter_data.get("toc2")
        or ""
    )
    localized_book_name = normalize_localized_book_name(localized_book_name)
    return localized_book_name


# def ensure_chapter_marker(
#     chapter_usfm_text: str,
#     chapter_num: int,
#     chapter_regex: str = CHAPTER_CAPTURE_REGEX,
# ) -> str:
#     r"""
#     Modify USFM source to insert a chapter marker, \c <chapter_num>, if it does not have one.
#     """
#     if not re.search(chapter_regex, chapter_usfm_text):
#         logger.debug("chapter marker is missing, adding one...")
#         updated_chapter_usfm_text = re.sub(
#             r"(\\cl\s+[^\n]+)",
#             r"\1" + "\n" + rf" \\c {chapter_num}" + "\n" + chapter_usfm_text,
#             chapter_usfm_text,
#         )
#         return updated_chapter_usfm_text
#     logger.debug("chapter marker already existed, didn't add one")
#     return chapter_usfm_text

# CHAPTER_CAPTURE_REGEX = r"(?m)^\\c\s+\d+"


def ensure_chapter_marker(
    chapter_usfm_text: str,
    chapter_num: int,
    chapter_regex: re.Pattern[str] = CHAPTER_CAPTURE_REGEX,
) -> str:
    r"""
    Modify USFM source to insert a chapter marker, \c <chapter_num>, if it does not have one.
    """
    if re.search(chapter_regex, chapter_usfm_text):
        logger.debug("chapter marker already existed, didn't add one")
        return chapter_usfm_text
    logger.debug("chapter marker is missing, adding one...")
    # Try inserting before \cl, if present
    if match := re.search(r"\\cl\s+[^\n]+", chapter_usfm_text):
        insert_pos = match.start()
        return (
            chapter_usfm_text[:insert_pos]
            + f"\n\\c {chapter_num}\n"
            + chapter_usfm_text[insert_pos:]
        )
    # Otherwise, insert at the beginning
    return f"\\c {chapter_num}\n" + chapter_usfm_text


def usfm_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    book_names: Mapping[str, str] = BOOK_NAMES,
    use_chapter_labels: bool = settings.USE_CHAPTER_LABELS,
) -> USFMBook:
    """
    First produce HTML content from USFM content and then break the
    HTML content returned into a model.USFMBook data structure for use
    during interleaving with other resource assets.
    """
    content_file = usfm_asset_file(resource_lookup_dto, resource_dir)
    content = read_file(content_file) if content_file else ""
    if not use_chapter_labels:
        content = ensure_no_chapter_labels(content)
    usfm_chapters: dict[ChapterNum, USFMChapter] = {}
    frontmatter, chapter_markers, chapters_usfm = split_usfm_by_chapters(
        resource_lookup_dto.lang_code,
        resource_lookup_dto.resource_type,
        resource_lookup_dto.book_code,
        content,
    )
    localized_book_name = maybe_localized_book_name(frontmatter)
    for chapter_marker, chapter_usfm in zip(chapter_markers, chapters_usfm):
        logger.debug("chapter_usfm[0:60]: %s", chapter_usfm[0:60])
        # chapter_usfm = chapter_marker + "\n" + chapter_usfm
        chapter_num = get_chapter_num(chapter_usfm)
        if chapter_num == -1:
            chapter_num = chapter_label_numeric_part(chapter_usfm)
        logger.debug("chapter_num: %s", chapter_num)
        if use_chapter_labels:
            chapter_usfm = ensure_chapter_label(chapter_usfm, chapter_num)
        chapter_usfm = ensure_chapter_marker(chapter_usfm, chapter_num)
        logger.debug("updated chapter_usfm[0:60]: %s", chapter_usfm[0:60])
        chapter_html_content = usfm_chapter_html(
            chapter_usfm, resource_lookup_dto, chapter_num
        )
        cleaned_chapter_html_content = remove_null_bytes_and_control_characters(
            chapter_html_content
        )
        usfm_chapters[chapter_num] = USFMChapter(
            content=(
                cleaned_chapter_html_content if cleaned_chapter_html_content else ""
            ),
            verses=None,
        )
    return USFMBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        book_code=resource_lookup_dto.book_code,
        national_book_name=(
            localized_book_name
            if localized_book_name
            else BOOK_NAMES[resource_lookup_dto.book_code]
        ),
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=usfm_chapters if usfm_chapters else {},
        lang_direction=resource_lookup_dto.lang_direction,
    )


def load_manifest(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


def glob_chapter_dirs(
    resource_dir: str,
    book_code: str,
    glob_in_subdirs_fmt_str: str = "{}/**/*{}/*[0-9]*",
    glob_fmt_str: str = "{}/*{}/*[0-9]*",
) -> list[str]:
    chapter_dirs = glob(glob_in_subdirs_fmt_str.format(resource_dir, book_code))
    # Some languages are organized differently on disk
    if not chapter_dirs:
        chapter_dirs = glob(
            glob_in_subdirs_fmt_str.format(resource_dir, book_code.upper())
        )
    if not chapter_dirs:
        chapter_dirs = glob(glob_fmt_str.format(resource_dir, book_code))
    if not chapter_dirs:
        chapter_dirs = glob(glob_fmt_str.format(resource_dir, book_code.upper()))
    return sorted(chapter_dirs)


def tn_chapter_verses(
    resource_dir: str,
    lang_code: str,
    book_code: str,
    resource_requests: Sequence[ResourceRequest],
) -> dict[int, TNChapter]:
    chapter_dirs = sorted(glob_chapter_dirs(resource_dir, book_code))
    chapter_verses = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(Path(chapter_dir).name)
        chapter_intro = tn_chapter_intro(chapter_dir)
        chapter_intro_html = ""
        if chapter_intro:
            tw_resource_dir_ = tw_resource_dir(lang_code)
            translation_words_dict_ = translation_words_dict(tw_resource_dir_)
            chapter_intro = markdown_transformer.transform_tw_links(
                chapter_intro,
                lang_code,
                resource_requests,
                translation_words_dict_,
            )
            chapter_intro = markdown_transformer.transform_ta_and_tn_links(
                chapter_intro,
                lang_code,
                resource_requests,
            )
            chapter_intro_html = mistune.markdown(chapter_intro)
            chapter_intro_html = markdown_transformer.remove_pagination_symbols(
                chapter_intro_html
            )
        verses_html = tn_verses_html(
            chapter_dir, lang_code, book_code, resource_requests
        )
        chapter_verses[chapter_num] = TNChapter(
            intro_html=chapter_intro_html, verses=verses_html
        )
    return chapter_verses


def tn_chapter_intro(
    chapter_dir: str,
    glob_md_fmt_str: str = "{}/*intro.md",
    glob_txt_fmt_str: str = "{}/*intro.txt",
) -> Optional[str]:
    intro_paths = sorted(glob(glob_md_fmt_str.format(chapter_dir)))
    if not intro_paths:
        intro_paths = sorted(glob(glob_txt_fmt_str.format(chapter_dir)))
    return read_file(intro_paths[0]) if intro_paths else None


def book_intro_markdown(resource_dir: str, book_code: str) -> str:
    book_intro_paths = sorted(glob(f"{resource_dir}/*{book_code}/front/intro.md"))
    if not book_intro_paths:
        book_intro_paths = sorted(glob(f"{resource_dir}/*{book_code}/front/intro.txt"))
    book_intro_markdown_ = read_file(book_intro_paths[0]) if book_intro_paths else ""
    return book_intro_markdown_


def tn_verses_html(
    chapter_dir: str,
    lang_code: str,
    book_code: str,
    resource_requests: Sequence[ResourceRequest],
    book_names: Mapping[str, str] = BOOK_NAMES,
    verse_fmt_str: str = "<h4>{} {}:{}</h4>\n{}",
    glob_md_fmt_str: str = "{}/*[0-9]*.md",
    glob_txt_fmt_str: str = "{}/*[0-9]*.txt",
    h1: str = H1,
    h5: str = H5,
) -> dict[VerseRef, str]:
    verse_paths = sorted(glob(glob_md_fmt_str.format(chapter_dir)))
    if not verse_paths:
        verse_paths = sorted(glob(glob_txt_fmt_str.format(chapter_dir)))
    verses_html = {}
    for filepath in verse_paths:
        verse_ref = Path(filepath).stem
        verse_md_content = read_file(filepath)
        verse_md_content = markdown_transformer.transform_ta_and_tn_links(
            verse_md_content,
            lang_code,
            resource_requests,
        )
        verse_html_content = mistune.markdown(verse_md_content)
        adjusted_verse_html_content = re.sub(h1, h5, verse_html_content)
        verses_html[verse_ref] = verse_fmt_str.format(
            book_names[book_code],
            int(Path(chapter_dir).stem),
            int(verse_ref),
            adjusted_verse_html_content,
        )
    return verses_html


def tn_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
    show_tn_book_intro: bool = settings.SHOW_TN_BOOK_INTRO,
) -> TNBook:
    chapter_verses = tn_chapter_verses(
        resource_dir,
        resource_lookup_dto.lang_code,
        resource_lookup_dto.book_code,
        resource_requests,
    )
    book_intro = ""
    if show_tn_book_intro:
        book_intro = book_intro_markdown(resource_dir, resource_lookup_dto.book_code)
        if book_intro:
            book_intro = markdown_transformer.remove_sections(book_intro)
            tw_resource_dir_ = tw_resource_dir(resource_lookup_dto.lang_code)
            translation_words_dict_ = translation_words_dict(tw_resource_dir_)
            book_intro = markdown_transformer.transform_tw_links(
                book_intro,
                resource_lookup_dto.lang_code,
                resource_requests,
                translation_words_dict_,
            )
            book_intro = markdown_transformer.transform_ta_and_tn_links(
                book_intro,
                resource_lookup_dto.lang_code,
                resource_requests,
            )
            book_intro = mistune.markdown(book_intro)
    return TNBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        book_code=resource_lookup_dto.book_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        book_intro=book_intro,
        chapters=chapter_verses,
        lang_direction=resource_lookup_dto.lang_direction,
    )


def tq_chapter_verses(
    resource_dir: str,
    lang_code: str,
    book_code: str,
    resource_requests: Sequence[ResourceRequest],
    book_names: Mapping[str, str] = BOOK_NAMES,
    verse_paths_glob_fmt_str: str = "{}/*[0-9]*.md",
    h1: str = H1,
    h5: str = H5,
    verse_label_fmt_str: str = "<h4>{} {}:{}</h4>\n{}",
) -> dict[int, TQChapter]:
    chapter_dirs = sorted(glob_chapter_dirs(resource_dir, book_code))
    chapter_verses = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(split(chapter_dir)[-1])
        verse_paths = sorted(glob(verse_paths_glob_fmt_str.format(chapter_dir)))
        verses_html: dict[VerseRef, str] = {}
        for filepath in verse_paths:
            verse_ref = Path(filepath).stem
            verse_md_content = read_file(filepath)
            verse_md_content = markdown_transformer.transform_ta_and_tn_links(
                verse_md_content,
                lang_code,
                resource_requests,
            )
            verse_html_content = mistune.markdown(verse_md_content)
            adjusted_verse_html_content = re.sub(h1, h5, verse_html_content)
            verses_html[verse_ref] = verse_label_fmt_str.format(
                book_names[book_code],
                chapter_num,
                int(verse_ref),
                adjusted_verse_html_content,
            )
            chapter_verses[chapter_num] = TQChapter(verses=verses_html)
    return chapter_verses


def tq_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
) -> TQBook:
    chapter_verses = tq_chapter_verses(
        resource_dir,
        resource_lookup_dto.lang_code,
        resource_lookup_dto.book_code,
        resource_requests,
    )
    return TQBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        book_code=resource_lookup_dto.book_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=chapter_verses,
        lang_direction=resource_lookup_dto.lang_direction,
    )


def tw_sort_key(name_content_pair: TWNameContentPair) -> str:
    return name_content_pair.localized_word


def tw_name_content_pairs(
    resource_dir: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
    h1: str = H1,
    h2: str = H2,
    h3: str = H3,
    h4: str = H4,
) -> list[TWNameContentPair]:
    translation_word_filepaths_: list[str] = translation_word_filepaths(resource_dir)
    name_content_pairs: list[TWNameContentPair] = []
    for translation_word_filepath in translation_word_filepaths_:
        translation_word_content = read_file(translation_word_filepath)
        localized_translation_word_ = localized_translation_word(
            translation_word_content
        )
        translation_word_content = markdown_transformer.remove_sections(
            translation_word_content
        )
        translation_word_content = markdown_transformer.transform_ta_and_tn_links(
            translation_word_content, lang_code, resource_requests
        )
        html_word_content = mistune.markdown(translation_word_content)
        html_word_content = re.sub(h2, h4, html_word_content)
        html_word_content = re.sub(h1, h3, html_word_content)
        name_content_pairs.append(
            TWNameContentPair(localized_translation_word_, html_word_content)
        )
    return sorted(name_content_pairs, key=tw_sort_key)


def tw_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
) -> TWBook:
    name_content_pairs = tw_name_content_pairs(
        resource_dir, resource_lookup_dto.lang_code, resource_requests
    )
    return TWBook(
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        book_code=resource_lookup_dto.book_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        name_content_pairs=name_content_pairs,
        lang_direction=resource_lookup_dto.lang_direction,
    )


def bc_book_intro_content(
    resource_dir: str,
    book_code: str,
    book_intro_glob_path_fmt_str: str = "{}/*{}/intro.md",
) -> str:
    book_intro_paths = glob(
        book_intro_glob_path_fmt_str.format(resource_dir, book_code)
    )
    return read_file(book_intro_paths[0]) if book_intro_paths else ""


def modify_commentary_label(
    chapter_commentary_html_content: str, chapter_num: int
) -> str:
    # Modify chapter heading if it's the first chapter
    if chapter_num == 1:
        chapter_commentary_html_content = re.sub(
            r"<h1>(.*?)<\/h1>",
            r"<h1>\1 Commentary</h1>",
            chapter_commentary_html_content,
        )
    return chapter_commentary_html_content


def replace_relative_with_absolute_links(
    chapter_commentary_html_content: str,
    url_fmt_str: str = BC_ARTICLE_URL_FMT_STR,
) -> str:
    chapter_commentary_html_content = re.sub(
        r'<a\s+href="\/(.*?)">',
        lambda match: '<a href="'
        + url_fmt_str.format(match.group(1))
        + '" target="_blank">',
        chapter_commentary_html_content,
    )
    return chapter_commentary_html_content


def bc_chapters(
    resource_dir: str,
    lang_code: str,
    book_code: str,
    resource_requests: Sequence[ResourceRequest],
    chapter_dirs_glob_fmt_str: str = "{}/*{}/*[0-9]*",
    url_fmt_str: str = BC_ARTICLE_URL_FMT_STR,
) -> dict[int, BCChapter]:
    chapter_dirs = sorted(
        glob(chapter_dirs_glob_fmt_str.format(resource_dir, book_code))
    )
    chapters: dict[int, BCChapter] = {}
    for chapter_dir in chapter_dirs:
        chapter_num = int(Path(chapter_dir).stem)
        chapter_commentary_md_content = read_file(chapter_dir)
        chapter_commentary_md_content = markdown_transformer.remove_sections(
            chapter_commentary_md_content
        )
        chapter_commentary_md_content = markdown_transformer.transform_ta_and_tn_links(
            chapter_commentary_md_content, lang_code, resource_requests
        )
        chapter_commentary_html_content = mistune.markdown(
            chapter_commentary_md_content
        )
        chapter_commentary_html_content = modify_commentary_label(
            chapter_commentary_html_content, chapter_num
        )
        # fmt: off
        chapter_commentary_html_content = markdown_transformer.remove_pagination_symbols(
            chapter_commentary_html_content
        )
        # fmt: on
        chapter_commentary_html_content = replace_relative_with_absolute_links(
            chapter_commentary_html_content
        )
        chapter_commentary_html_content = adjust_commentary_headings(
            chapter_commentary_html_content
        )
        # TODO For now we are deactivating the links to articles from commentary. It
        # would be nice to provide those markdown articles as rendered HTML so that the
        # user can follow those links.
        chapter_commentary_html_content = remove_links(chapter_commentary_html_content)
        chapters[chapter_num] = BCChapter(commentary=chapter_commentary_html_content)
    return chapters


def bc_book_content(
    resource_lookup_dto: ResourceLookupDto,
    resource_dir: str,
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
) -> BCBook:
    book_intro = bc_book_intro_content(resource_dir, resource_lookup_dto.book_code)
    book_intro = markdown_transformer.remove_sections(book_intro)
    book_intro = markdown_transformer.transform_ta_and_tn_links(
        book_intro, resource_lookup_dto.lang_code, resource_requests
    )
    book_intro_html_content = mistune.markdown(book_intro)
    book_intro_html_content = adjust_commentary_headings(book_intro_html_content)
    book_intro_html_content = markdown_transformer.remove_pagination_symbols(
        book_intro_html_content
    )
    book_intro_html_content = remove_links(book_intro_html_content)
    return BCBook(
        book_intro=book_intro_html_content,
        lang_code=resource_lookup_dto.lang_code,
        lang_name=resource_lookup_dto.lang_name,
        book_code=resource_lookup_dto.book_code,
        resource_type_name=resource_lookup_dto.resource_type_name,
        chapters=bc_chapters(
            resource_dir,
            resource_lookup_dto.lang_code,
            resource_lookup_dto.book_code,
            resource_requests,
        ),
    )


def books(
    resource_lookup_dtos: Sequence[ResourceLookupDto],
    resource_dirs: Sequence[str],
    resource_requests: Sequence[ResourceRequest],
    layout_for_print: bool,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    tn_resource_type: str = TN_RESOURCE_TYPE,
    en_tn_condensed_resource_type: str = EN_TN_CONDENSED_RESOURCE_TYPE,
    tq_resource_type: str = TQ_RESOURCE_TYPE,
    tw_resource_type: str = TW_RESOURCE_TYPE,
    bc_resource_type: str = BC_RESOURCE_TYPE,
    rg_resource_type: str = RG_RESOURCE_TYPE,
    docx_file_path: str = "en_rg_nt_survey.docx",
) -> tuple[
    Sequence[USFMBook],
    Sequence[TNBook],
    Sequence[TQBook],
    Sequence[TWBook],
    Sequence[BCBook],
    Sequence[RGBook],
]:
    usfm_books = []
    tn_books = []
    tq_books = []
    tw_books = []
    bc_books = []
    rg_books = []
    filtered_rg_books = []
    for resource_lookup_dto, resource_dir in zip(resource_lookup_dtos, resource_dirs):
        if resource_lookup_dto.resource_type in usfm_resource_types:
            usfm_book = usfm_book_content(
                resource_lookup_dto,
                resource_dir,
            )
            usfm_books.append(usfm_book)
        elif (
            resource_lookup_dto.resource_type == tn_resource_type
            # Handle English Condensed TN
            or resource_lookup_dto.resource_type == en_tn_condensed_resource_type
        ):
            tn_book = tn_book_content(
                resource_lookup_dto, resource_dir, resource_requests, layout_for_print
            )
            tn_books.append(tn_book)
        elif resource_lookup_dto.resource_type == tq_resource_type:
            tq_book = tq_book_content(
                resource_lookup_dto, resource_dir, resource_requests, layout_for_print
            )
            tq_books.append(tq_book)
        elif resource_lookup_dto.resource_type == tw_resource_type:
            tw_book = tw_book_content(
                resource_lookup_dto, resource_dir, resource_requests, layout_for_print
            )
            tw_books.append(tw_book)
        elif resource_lookup_dto.resource_type == bc_resource_type:
            bc_book = bc_book_content(
                resource_lookup_dto, resource_dir, resource_requests, layout_for_print
            )
            bc_books.append(bc_book)
        elif resource_lookup_dto.resource_type == rg_resource_type:
            path = join(resource_dir, docx_file_path)
            logger.debug("About to get_rg_books from: %s", path)
            rg_books = get_rg_books(
                path,
                resource_lookup_dto.lang_code,
                resource_lookup_dto.lang_name,
                resource_lookup_dto.resource_type_name,
                resource_lookup_dto.lang_direction,
            )
            filtered_rg_books = [
                rg_book
                for rg_book in rg_books
                if rg_book.lang_code == resource_lookup_dto.lang_code
                and rg_book.book_code == resource_lookup_dto.book_code
            ]
    return usfm_books, tn_books, tq_books, tw_books, bc_books, filtered_rg_books


def ensure_paragraph_before_verses(
    usfm_file: str,
    verse_content: str,
    usfm_verse_one_file_regex: str = r"^01\..*",
    chapter_marker_not_on_own_line_regex: str = r"^\\c [0-9]+ .*|\n",
    chapter_marker_not_on_own_line_with_match_groups: str = r"(^\\c [0-9]+) (.*|\n)",
    # chapter_marker_not_on_own_line_repair_regex: str = r"\1\n\\p\n\2\n",
    chapter_marker_not_on_own_line_repair_regex: str = r"\1\n\n\2\n",
) -> str:
    r"""
    If verse_content has a USFM chapter marker, \c, that is not on its
    own line (violation of the USFM spec) then repair this and
    additionally add a USFM paragraph marker, \p, so that when the USFM is
    rendered to HTML the verse spans will be enclosed in a block level
    HTML element which in turn will ensure that Docx rendering is free of
    a bug wherein the verse spans are interpreted as a continuation of the
    chapter headline (as evidenced by verse content being rendered with
    the same font color and boldness as the chapter headline).
    Return the possibly updated verse_content.
    """
    if (
        re.compile(usfm_verse_one_file_regex).match(Path(usfm_file).name) is not None
    ):  # Verse 1 of chapter
        if (
            re.compile(chapter_marker_not_on_own_line_regex).match(verse_content)
            is not None
        ):  # Chapter marker not on own line.
            # Make chapter marker occupy its own line and add a USFM paragraph
            # marker right after it. Why? Because languages which render correctly
            # in Docx have a \p USFM marker after the chapter marker and languages
            # which did not render properly (see docstring above for particulars) in
            # Docx did not have one. Presumably the 3rd party lib we use to parse
            # HTML to Docx doesn't like spans that are not contained in a block
            # level element.
            verse_content = re.sub(
                chapter_marker_not_on_own_line_with_match_groups,
                chapter_marker_not_on_own_line_repair_regex,
                verse_content,
            )
    return verse_content


def get_book_name(
    resource_path: str,
    resource_lookup_dto: ResourceLookupDto,
    bible_book_names: Mapping[str, str] = BOOK_NAMES,
    use_localized_book_name: bool = settings.USE_LOCALIZED_BOOK_NAME,
) -> str:
    """Retrieve the book name, preferring a localized title if available."""
    title_path = join(resource_path, "front", "title.txt")
    if use_localized_book_name:
        try:
            with open(title_path, encoding="utf-8") as f:
                return normalize_localized_book_name(f.read())
        except FileNotFoundError:
            logger.debug(
                "Localized book name not found, using English book name instead."
            )
    return bible_book_names[resource_lookup_dto.book_code]


def assemble_chapter_usfm(
    chapter_dir: DirEntry[str],
    use_chapter_labels: bool = settings.USE_CHAPTER_LABELS,
    use_localized_chapter_label: bool = settings.USE_LOCALIZED_CHAPTER_LABEL,
) -> list[str]:
    chapter_usfm_content = []
    try:
        chapter_num = int(str(chapter_dir.name))
    except ValueError:
        logger.info(
            "%s is not a valid chapter number, assigning -1 as chapter number",
            str(chapter_dir.name),
        )
        chapter_num = -1  # use this as a sentinal
    chapter_usfm_content.append("\n" + rf"\c {chapter_num}" + "\n")
    if use_chapter_labels:
        if use_localized_chapter_label:
            chapter_word_file = join(chapter_dir.path, "title.txt")
            try:
                with open(chapter_word_file, "r") as fin:
                    chapter_word = fin.read()
                    chapter_word = chapter_word.strip()
                    chapter_word = chapter_label_sans_numeric_part(chapter_word)
                    # logger.debug("chapter_label_sans_numeric_part: %s", chapter_word)
                    # chapter_label = "\n" + rf"\cl {chapter_word} {chapter_num}" + "\n"
                    chapter_label = "\n" + rf"\cl {chapter_word}" + "\n"
                    logger.debug("chapter_label: %s", chapter_label)
                    chapter_usfm_content.append(chapter_label)
            except FileNotFoundError:
                pass  # No file containing chapter label
                # TODO There could be a branch here wherein we wanted to use localized
                # chapter label, but it wasn't provided and thus we should provide an
                # English chapter label. The other option would be to not provide a
                # chapter label if we requested a localized one and it could not be
                # found.
        else:
            # chapter_usfm_content.append("\n" + rf"\cl Chapter" + f"{chapter_num}" + "\n")
            chapter_usfm_content.append("\n" + r"\cl Chapter" + "\n")
    logger.info(
        "Adding a USFM chapter marker for chapter: %s",
        chapter_num,
    )
    chapter_verse_files = sorted(
        [
            file.path
            for file in scandir(chapter_dir)
            if file.is_file()
            and file.name != "title.txt"
            and not file.name.startswith(".")
            and (file.name.endswith(".usfm") or file.name.endswith(".txt"))
        ]
    )
    for usfm_file in chapter_verse_files:
        with open(usfm_file, "r") as fin:
            # logger.debug("usfm_file: %s", usfm_file)
            verse_content = fin.read()
            # NOTE Area of interest
            # Some languages put a chapter marker in front of verse 1 in the verse
            # file which covers a verse span which includes verse 1 . Since we
            # ensure chapter markers ourselves when assembling multiple verse files
            # into a chapter this ends up creating a duplicate chapter marker.
            verse_content = re.sub(r"^\\c\s+\d+", "", verse_content)
            verse_content = ensure_paragraph_before_verses(usfm_file, verse_content)
            chapter_usfm_content.append(verse_content)
            chapter_usfm_content.append("\n")
    return chapter_usfm_content


def combine_usfm_files(
    resource_dir: str,
    resource_lookup_dto: ResourceLookupDto,
) -> str:
    """
    Attempt to assemble and construct parseable USFM content for USFM
    resource where repo has multiple chapter directories containing verse
    content files.
    """
    logger.info("About to assemble USFM content into a single USFM file.")
    logger.info("Adding a USFM \\ide marker which the parser requires.")
    usfm_content = [r"\ide UTF-8" + "\n"]
    logger.info("Adding a USFM \\h marker which the parser requires.")
    book_name = get_book_name(resource_dir, resource_lookup_dto)
    usfm_content.append(rf"\h {book_name}" + "\n")
    subdirs = [
        file
        for file in scandir(resource_dir)
        if file.is_dir()
        and file.name not in ["front", "00"]
        and not file.name.startswith(".")
    ]
    for chapter_dir in sorted(subdirs, key=lambda dir_entry: dir_entry.name):
        chapter_usfm_content = assemble_chapter_usfm(chapter_dir)
        usfm_content.extend(chapter_usfm_content)
    filename = join(
        resource_dir,
        (
            f"{resource_lookup_dto.lang_code}_"
            f"{resource_lookup_dto.resource_type}_"
            f"{resource_lookup_dto.book_code}.usfm"
        ),
    )
    logger.info("Writing USFM content to: %s", filename)
    with open(filename, "w") as fout:
        fout.write("".join(usfm_content))
    return filename


# Used by STET and PASSAGES apps
def lookup_verse_text(usfm_book: USFMBook, chapter_num: int, verse_ref: str) -> str:
    chapter = usfm_book.chapters.get(chapter_num)
    if not chapter or not chapter.verses:
        return ""
    verse = chapter.verses.get(verse_ref, "")
    logger.info(
        "book_code: %s, chapter_num: %s, verse_num: %s, verse: %s",
        usfm_book.book_code,
        chapter_num,
        verse_ref,
        verse,
    )
    return verse


# Used by STET and RG_PASSAGES
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
            # Remove footnotes numbers
            verse_text = re.sub(
                r'<sup id=".*?" class="caller">.*?</sup>', "", verse_text
            )
            # Fix spacing issue when div class="poetry-*" type divs
            # are used, e.g., yielding 'heartsas' for Hebrews 3:8
            verse_text = re.sub(
                r'<div class="poetry-\d">(.*?)</div>',
                r" \1",
                verse_text,
            )
            # Add to the dictionary with verse number as the key and verse text as the value
            verse_dict[verse_number_] = verse_text
    return verse_dict
