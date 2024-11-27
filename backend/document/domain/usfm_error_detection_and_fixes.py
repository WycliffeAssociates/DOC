import re

from document.config import settings
from document.domain.model import ResourceLookupDto

logger = settings.logger(__name__)


# List of regex patterns to detect issues before applying corrections
pattern_matchers = {
    "remove_null_bytes_and_control_characters": r"[\x00-\x1F]+",
    "fix_dot_after_verse_number": r"(\\v\s*\d+)\s*\.\s*(\S)",
    "fix_verse_marker_without_v": r"\\(\d+)\s*\.?\s*(\S+)",
    "fix_missing_space_before_number": r"(?<!\\c\s)(?<!\\v\s)(?<!\\v\s\d)(?<!\\q\d\s)(?<!\\li)(?<!\\li\d)(?<=\S)(?<!\\\S)(\d+)(?=\s)",
    "fix_missing_space_after_number": r"(\s+|^)(\d+)(\S)",
    "fix_missing_space_before_verse_marker": r"(\S)(\\v\s+\d+)",
    "fix_standalone_verse_numbers": r"(?<!\\)(?<!\\c\s)(?<!\\v\s)(?<!\\v\s\d)(?<!\\q\d\s)(?<!\\li)(?<!\\li\d)\b(\d+)\b(?=\s|$|[^\d\w])",
    "replace_n_with_v": r"\\n",
    # The following are actually caused by fixes above and thus
    # constitute a second pass of this "parser" and are thus invoked
    # after those rules above.
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


def fix_missing_space_before_number(content: str) -> str:
    if match := compiled_patterns["fix_missing_space_before_number"].search(content):
        logger.debug(
            "match.group(1): %s",
            match.group(1),
        )
        character_before_number = content[match.start() - 1]
        logger.debug("character_before_number: %s", character_before_number)
        if character_before_number.isdigit() and match.group(1).isdigit():
            logger.debug(
                "Actually, it wasn't missing a space before number after all upon further checking"
            )
            return content
        else:
            return re.sub(
                pattern_matchers["fix_missing_space_before_number"], r" \1", content
            )
    return content


def fix_missing_space_after_number(content: str) -> str:
    result = ""
    if match := compiled_patterns["fix_missing_space_after_number"].search(content):
        logger.debug(
            "match.group(1): %s, match.group(2): %s, match.group(3): %s",
            match.group(1),
            match.group(2),
            match.group(3),
        )
        if match.group(2).isdigit() and match.group(3).isdigit():
            logger.debug(
                "Actually, it wasn't missing a space after number after all upon further checking"
            )
            result = content
        else:
            result = re.sub(
                pattern_matchers["fix_missing_space_after_number"], r"\1\2 \3", content
            )
    return result


def fix_missing_space_before_verse_marker(content: str) -> str:
    return re.sub(
        pattern_matchers["fix_missing_space_before_verse_marker"], r"\1 \2", content
    )


def fix_standalone_verse_numbers(content: str) -> str:
    # We have to try to determine if a standalone integer should be
    # interpreted as a verse with missing verse marker or as a valid piece
    # of non-structural content. E.g., in ayn, mat, chapter 1, verse 17, the
    # use of 14 happens twice where it refers to "fourteen generations". To
    # modify that would be a mistake. We need to determine more context to
    # see when to apply fix_standalone_verse_numbers. Toward that
    # goal, we check for two conditions:
    #
    # 1) if a valid verse marker occurs within an arbitrary distance in
    # characters of content before or after the supposed standalone verse
    # number, then we'll arbitrarily decide that it is not a mistake in
    # structure. Of course, this misses the case when a translator got most
    # of the verse markers correct, but flubbed the random one.
    # 2) if, however, there are a number of the standalone verses equal or
    # greater than an arbitrary number of allowed occurrences, then we will
    # decide that the supposed standalone verse is, in fact, supposed to be
    # preceded by a verse marker. The thought here is that it is unlikely that
    # standalone numbers will be used more than some arbitrary number
    # of times per chapter unless, indeed, the translator had made a
    # structural mistake and just forgot to precede the number with a USFM
    # verse marker.
    # 3) if consecutive supposed standalone verse numbers are in ascending
    # order numerically we decide that they are likely verse numbers after
    # all.
    if match := compiled_patterns["fix_standalone_verse_numbers"].search(content):
        # Calculate safe slice indices
        length_of_context = 50
        num_of_occurrences = 3
        start_index = max(0, match.start() - length_of_context)
        end_index = min(len(content), match.end() + length_of_context)
        context_for_standalone_verse = content[start_index:end_index]
        logger.debug("context_for_standalone_verse: %s", context_for_standalone_verse)
        # Extract all standalone numbers
        matches = [int(m.group()) for m in re.finditer(r"\b\d+\b", content)]
        is_ascending = all(
            earlier < later for earlier, later in zip(matches, matches[1:])
        )
        num_matches = len(matches)
        if (
            not re.compile(r"""\\v \d+""").search(context_for_standalone_verse)
            and not num_matches >= num_of_occurrences
        ) or is_ascending:  # Check for non-ascending numbers
            return re.sub(
                pattern_matchers["fix_standalone_verse_numbers"],
                r"\\v \1",
                content,
            )
        else:
            logger.debug(
                "Actually, we can't be certain it was a standalone verse number after all upon further checking"
            )
    return content


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


def fix_usfm(usfm_content: str, resource_lookup_dto: ResourceLookupDto) -> str:
    """
    Detect and correct many USFM structural issues in USFM source.
    """
    logger.debug("usfm_content: %s", usfm_content)
    corrected_usfm_content: str = usfm_content

    # if compiled_patterns["remove_null_bytes_and_control_characters"].search(
    #     corrected_usfm_content
    # ):
    #     logger.debug(
    #         "USFM defect, %s, detected for resource: %s-%s-%s, about to attempt fix...",
    #         "remove_null_bytes_and_control_characters",
    #         resource_lookup_dto.lang_code,
    #         resource_lookup_dto.resource_type,
    #         resource_lookup_dto.book_code,
    #     )
    #     corrected_usfm_content = remove_null_bytes_and_control_characters(
    #         corrected_usfm_content
    #     )
    if match := compiled_patterns["fix_dot_after_verse_number"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "fix_dot_after_verse_number",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_dot_after_verse_number(corrected_usfm_content)
    if match := compiled_patterns["fix_verse_marker_without_v"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "fix_verse_marker_without_v",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_verse_marker_without_v(corrected_usfm_content)
    if match := compiled_patterns["fix_missing_space_before_number"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "fix_missing_space_before_number",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_missing_space_before_number(corrected_usfm_content)
    if match := compiled_patterns["fix_missing_space_after_number"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "Potential USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, if confirmed, then will attempt fix...",
            "fix_missing_space_after_number",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_missing_space_after_number(corrected_usfm_content)
    if match := compiled_patterns["fix_missing_space_before_verse_marker"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "fix_missing_space_before_verse_marker",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_missing_space_before_verse_marker(
            corrected_usfm_content
        )
    if match := compiled_patterns["fix_standalone_verse_numbers"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "Possible USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, if confirmed, attempt to fix...",
            "fix_standalone_verse_numbers",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_standalone_verse_numbers(corrected_usfm_content)
    if match := compiled_patterns["replace_n_with_v"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "replace_n_with_v",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = replace_n_with_v(corrected_usfm_content)
    if match := compiled_patterns["replace_vv_with_v"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "replace_vv_with_v",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = replace_vv_with_v(corrected_usfm_content)
    if match := compiled_patterns["replace_sv_with_s"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "replace_sv_with_s",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = replace_sv_with_s(corrected_usfm_content)
    if match := compiled_patterns["fix_space_after_section_marker"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "fix_space_after_section_marker",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = fix_space_after_section_marker(corrected_usfm_content)
    if match := compiled_patterns["replace_qv_with_q"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "replace_qv_with_q",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = replace_qv_with_q(corrected_usfm_content)
    if match := compiled_patterns["replace_cc_with_c"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect, %s, detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "replace_cc_with_c",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            resource_lookup_dto.lang_code,
            resource_lookup_dto.resource_type,
            resource_lookup_dto.book_code,
        )
        corrected_usfm_content = replace_cc_with_c(corrected_usfm_content)
    return corrected_usfm_content
