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
    "fix_missing_space_after_verse_number": r"(\\v\s+\d+)(\S)",
    "fix_standalone_verse_numbers": r"(^|\s)(?<!\\c\s)(?<!\\v\s)(?<!\\c)(?<!\\q1\s)(?<!\\q2\s)(?<!\\li1\s)(?<!\\li2\s)\b(\d+)\b(?=\s|$|[^\d\w])",
    "replace_n_with_v": r"\\n",
    "replace_vv_with_v": r"\\v\\v",
    "replace_sv_with_s": r"\\s\\v",
    "fix_space_after_section_marker": r"\\s\s+(\d+)",
    "replace_qv_with_q": r"\\q\\v\s+(\d+)",
    "replace_cc_with_c": r"(\\c \d+)\s+(\\c \d+)",
}

# Compile regex patterns
compiled_patterns = [re.compile(pattern) for pattern in pattern_matchers]


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


def fix_missing_space_after_verse_number(content: str) -> str:
    return re.sub(
        pattern_matchers["fix_missing_space_after_verse_number"], r"\1 \2", content
    )


def fix_standalone_verse_numbers(content: str) -> str:
    updated_content = re.sub(
        pattern_matchers["fix_standalone_verse_numbers"],
        r"\1 \\v \2",
        content,
    )
    return re.sub(r"\\c\\v\s*(\d+)", r"\\c \1", updated_content)


def replace_n_with_v(content: str) -> str:
    # Replace \n used mistakenly as verse markers with \v
    return re.sub(pattern_matchers["replace_n_with_v"], "\\v", content)


def replace_vv_with_v(content: str) -> str:
    # Replace \v\v, caused by other correcting functions, with \v
    return re.sub(pattern_matchers["replace_vv_with_v"], "\\v", content)


def replace_sv_with_s(content: str) -> str:
    # Replace \s\v, caused by other correcting functions, with \s
    return re.sub(pattern_matchers["replace_sv_with_s"], "\\s", content)


def fix_space_after_section_marker(content: str) -> str:
    return re.sub(pattern_matchers["fix_space_after_section_marker"], r"\\s\1", content)


# FIXME
def replace_qv_with_q(content: str) -> str:
    # Replace \q\v <integer>, caused by other correcting functions, with \q<integer>
    return re.sub(pattern_matchers["replace_qv_with_q"], r"\\q\1", content)


def replace_cc_with_c(content: str) -> str:
    """
    Replace two consecutive chapter markers with whitespace or newline between them with only one chapter marker
    """
    return re.sub(pattern_matchers["replace_cc_with_c"], r"\1", content)


def correct_usfm(usfm_content: str, resource_lookup_dto: ResourceLookupDto) -> str:
    """
    Detect and correct many USFM structural issues in USFM source.
    """
    logger.debug("usfm_content: %s", usfm_content)
    # Check if any pattern matches
    if any(pattern.search(usfm_content) for pattern in compiled_patterns):
        logger.debug(
            "USFM defect detected for resource: %s-%s-%s, about to attempt fix...",
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        correction_functions: list[Callable[[str], str]] = [
            remove_null_bytes_and_control_characters,
            fix_dot_after_verse_number,
            fix_verse_marker_without_v,
            # fix_missing_verse_marker,
            # fix_missing_space_after_verse_number,
            # fix_standalone_verse_numbers,
            replace_n_with_v,
            replace_vv_with_v,
            replace_sv_with_s,
            fix_space_after_section_marker,
            replace_qv_with_q,
            replace_cc_with_c,
        ]
        corrected_content: str = usfm_content
        # Apply corrections
        for func in correction_functions:
            corrected_content = func(corrected_content)
        logger.debug("corrected_usfm_content: %s", corrected_content)
        return corrected_content
    # Return content unchanged if no patterns match
    return usfm_content
