import re
from typing import Callable, Match, Sequence

from document.config import settings
from document.domain.model import ResourceLookupDto

logger = settings.logger(__name__)

# List of regex patterns to detect issues before applying corrections
pattern_matchers = {
    "remove_null_bytes_and_control_characters": r"[\x00-\x1F]+",
    "fix_dot_after_verse_number": r"(\\v\s*\d+)\s*\.\s*(\S)",
    "fix_verse_marker_without_v": r"\\(\d+)\s*\.?\s*(\S+)",
    "fix_missing_verse_marker": r"\s*(\d+)\s*\s*(\S+)",
    "fix_missing_space_before_number": r"(?<!\\c\s)(?<!\\v\s)(?<!\\s\d)(?<!\\q1\s)(?<!\\q2\s)(?<!\\li1\s)(?<!\\li2\s)(\S)(\d\s)",
    "fix_missing_space_after_number": r"(\s+|^)(\d+)(\S)",
    "fix_missing_space_before_verse_marker": r"(\S)(\\v\s+\d+)",
    "fix_standalone_verse_numbers": r"(^|\s)(?<!\\c\s)(?<!\\v\s)(?<!\\c)(?<!\\q1\s)(?<!\\q2\s)(?<!\\li1\s)(?<!\\li2\s)\b(\d+)\b(?=\s|$|[^\d\w])",
    "replace_n_with_v": r"\\n",
    # The following are actually caused by fixes above and thus
    # constitute a second pass of this "parser"
    "replace_vv_with_v": r"\\v\\v",
    "replace_sv_with_s": r"\\s\\v",
    "fix_space_after_section_marker": r"\\s\s+(\d+)",
    "replace_qv_with_q": r"\\q\\v\s+(\d+)",
    "replace_cc_with_c": r"(\\c \d+)\s+(\\c \d+)",
}

compiled_patterns = {
    key: re.compile(pattern) for key, pattern in pattern_matchers.items()
}


def remove_null_bytes_and_control_characters(content: str) -> str:
    """
    Remove any NULL bytes and all control characters.

    Some languages' accidentally have ASCI control characters in their
    USFM. We strip those out as well as the possibility of ASCII NULL
    bytes.
    """
    return re.sub(
        pattern_matchers["remove_null_bytes_and_control_characters"], "", content
    )


def fix_dot_after_verse_number(content: str) -> str:
    return re.sub(pattern_matchers["fix_dot_after_verse_number"], r"\1 \2", content)


def fix_verse_marker_without_v(content: str) -> str:
    return re.sub(pattern_matchers["fix_verse_marker_without_v"], r"\\v \1 \2", content)


def fix_missing_verse_marker(content: str) -> str:
    return re.sub(pattern_matchers["fix_missing_verse_marker"], r"\\v \1 \2", content)


def fix_missing_space_before_number(content: str) -> str:
    return re.sub(
        pattern_matchers["fix_missing_space_before_number"], r"\1 \2", content
    )


def fix_missing_space_after_number(content: str) -> str:
    return re.sub(
        pattern_matchers["fix_missing_space_after_number"], r"\1\2 \3", content
    )


def fix_missing_space_before_verse_marker(content: str) -> str:
    return re.sub(
        pattern_matchers["fix_missing_space_before_verse_marker"], r"\1 \2", content
    )


def fix_standalone_verse_numbers(content: str) -> str:
    updated_content = re.sub(
        pattern_matchers["fix_standalone_verse_numbers"],
        r"\1\\v \2",
        content,
    )
    # Handle first verse which can otherwise be unconverted if it
    # abutts a word on its right side
    # updated_content = re.sub(r"1(\w)", r"\\v 1 \1", updated_content)
    # Handle situations where prior "fixes" introduced a verse marker in between a chapter marker and its chapter number
    return re.sub(r"\\c\\v\s*(\d+)", r"\\c \1", updated_content)


def replace_n_with_v(content: str) -> str:
    """Replace \n used mistakenly as verse markers with \v"""
    return re.sub(pattern_matchers["replace_n_with_v"], r"""\\v""", content)


def replace_cc_with_c(content: str) -> str:
    """
    Replace two consecutive chapter markers with whitespace or newline between them with only one chapter marker
    """
    return re.sub(pattern_matchers["replace_cc_with_c"], r"\1", content)


def replace_vv_with_v(content: str) -> str:
    """Replace \v\v, caused by other correcting functions, with \v"""
    return re.sub(pattern_matchers["replace_vv_with_v"], "\\v", content)


def replace_sv_with_s(content: str) -> str:
    """Replace \s\v, caused by other correcting functions, with \s"""
    return re.sub(pattern_matchers["replace_sv_with_s"], "\\s", content)


def fix_space_after_section_marker(content: str) -> str:
    """Reunite section marker with its value, caused by other correcting functions"""
    return re.sub(pattern_matchers["fix_space_after_section_marker"], r"\\s\1", content)


# FIXME
def replace_qv_with_q(content: str) -> str:
    """Replace \q\v <integer>, caused by other correcting functions, with \q<integer>"""
    return re.sub(pattern_matchers["replace_qv_with_q"], r"\\q\1", content)


def correct_usfm(usfm_content: str, resource_lookup_dto: ResourceLookupDto) -> str:
    """
    Detect and correct many USFM structural issues in USFM source.
    """
    logger.debug("usfm_content: %s", usfm_content)
    corrected_usfm_content: str = usfm_content

    if compiled_patterns["remove_null_bytes_and_control_characters"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "remove_null_bytes_and_control_characters",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = remove_null_bytes_and_control_characters(
            corrected_usfm_content
        )
    if compiled_patterns["fix_dot_after_verse_number"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "fix_dot_after_verse_number",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_dot_after_verse_number(corrected_usfm_content)
    if compiled_patterns["fix_verse_marker_without_v"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "fix_verse_marker_without_v",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_verse_marker_without_v(corrected_usfm_content)
    # if compiled_patterns["fix_missing_verse_marker"].search(corrected_usfm_content):
    #     logger.debug(
    #         "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
    #         "fix_missing_verse_marker",
    #         resource_lookup_dto.lang_code,
    #         resource_lookup_dto.resource_type,
    #         resource_lookup_dto.book_code,
    #     )
    #     corrected_usfm_content = fix_missing_verse_marker(corrected_usfm_content)
    if compiled_patterns["fix_missing_space_before_number"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "fix_missing_space_before_number",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_missing_space_before_number(corrected_usfm_content)
    if compiled_patterns["fix_missing_space_after_number"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "fix_missing_space_after_number",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_missing_space_after_number(corrected_usfm_content)
    if compiled_patterns["fix_missing_space_before_verse_marker"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "fix_missing_space_before_verse_marker",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_missing_space_before_verse_marker(
            corrected_usfm_content
        )
    if compiled_patterns["fix_standalone_verse_numbers"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "fix_standalone_verse_numbers",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_standalone_verse_numbers(corrected_usfm_content)
    if compiled_patterns["replace_n_with_v"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "replace_n_with_v",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = replace_n_with_v(corrected_usfm_content)
    if compiled_patterns["replace_vv_with_v"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "replace_vv_with_v",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = replace_vv_with_v(corrected_usfm_content)
    if compiled_patterns["replace_sv_with_s"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "replace_sv_with_s",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = replace_sv_with_s(corrected_usfm_content)
    if compiled_patterns["fix_space_after_section_marker"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "fix_space_after_section_marker",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_space_after_section_marker(corrected_usfm_content)
    if compiled_patterns["replace_qv_with_q"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "replace_qv_with_q",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = replace_qv_with_q(corrected_usfm_content)
    if compiled_patterns["replace_cc_with_c"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
            "replace_cc_with_c",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = replace_cc_with_c(corrected_usfm_content)
    return corrected_usfm_content
