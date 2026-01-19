import re
from typing import Sequence

from doc.config import settings

logger = settings.logger(__name__)

# Resources known to have USFM defects found through automatic
# randomized testing and subsequent manual investigation. As an aside:
# When we find one defective USFM resource for a language then the
# language might have others. In keeping with that fact one can set
# the value of settings.CHECK_ALL_BOOKS_FOR_LANGUAGE in .env file.
# This list is also used in tests and in that context
# settings.CHECK_ALL_BOOKS_FOR_LANGUAGE is not checked but each
# resource listed below is tested.
RESOURCES_WITH_USFM_DEFECTS: Sequence[tuple[str, str, str]] = [
    ("aaz-x-amarasibarat", "reg", "2pe"),
    ("abu", "reg", "php"),
    ("ach-SS-acholi", "reg", "gal"),
    ("adh", "reg", "1th"),
    ("adn", "reg", "mat"),
    ("agd-x-namel", "reg", "2th"),
    ("ahm", "reg", "php"),
    ("ahm", "reg", "php"),
    ("ajg-x-adjtalagbe", "reg", "mat"),
    ("aoa", "reg", "col"),
    ("aoa", "reg", "luk"),
    ("ayn", "reg", "jud"),
    ("bds", "reg", "phm"),
    ("bem", "reg", "mat"),
    ("bem", "reg", "gal"),
    ("bem-x-kabenmushi", "reg", "zec"),
    ("bem-x-kabenmushi", "reg", "2sa"),
    ("bem-x-kabenmushi", "reg", "mat"),
    ("bem-x-kabenmushi", "reg", "isa"),
    ("bem-x-kabenmushi", "reg", "jer"),
    ("bem-x-kabenmushi", "reg", "sng"),
    ("bem-x-kabenmushi", "reg", "deu"),
    ("bem-x-kabenmushi", "reg", "1ki"),
    # ("bem-x-kabenmushi", "reg", "1ch"), # unavailable from data API
    ("bem-x-kabenmushi", "reg", "ecc"),
    ("bem-x-kabenmushi", "reg", "2ki"),
    ("bi", "reg", "act"),
    ("bji", "reg", "mat"),
    ("bji", "reg", "1co"),
    ("bji", "reg", "luk"),
    ("bji", "reg", "heb"),
    ("bjz", "reg", "eph"),
    ("blo", "reg", "rom"),
    ("blo", "reg", "act"),
    ("blo", "reg", "col"),
    ("blo", "reg", "php"),
    ("blo", "reg", "heb"),
    ("blo", "reg", "1jn"),
    ("blo", "reg", "col"),
    ("bne", "reg", "gal"),
    ("bof", "reg", "mat"),
    ("bou", "reg", "gen"),
    ("btd-x-boang", "reg", "mat"),
    ("btd-x-boang", "reg", "1ti"),
    ("btd-x-boang", "reg", "phm"),
    ("btm", "reg", "phm"),
    ("btm", "reg", "1th"),
    ("btm", "reg", "2co"),
    ("btm", "reg", "1pe"),
    ("bwc", "reg", "lev"),
    ("bwc", "reg", "php"),
    ("bwc", "reg", "tit"),
    ("byi", "reg", "gen"),
    ("byi", "reg", "php"),
    ("byi", "reg", "rut"),
    ("byn", "reg", "2sa"),
    ("byn", "reg", "nam"),
    ("byn", "reg", "2co"),
    ("byn", "reg", "jud"),
    ("byn", "reg", "dan"),
    ("byn", "reg", "hab"),
    ("byn", "reg", "hag"),
    ("byn", "reg", "mic"),
    ("byn", "reg", "1ti"),
    ("byn", "reg", "2ti"),
    ("byn", "reg", "2pe"),
    ("bzu", "reg", "tit"),
    ("cbt", "reg", "jos"),
    ("cbt", "reg", "est"),
    ("ccp", "reg", "mat"),
    ("ccp", "reg", "gal"),
    ("ceb", "ulb", "gen"),
    ("cot", "reg", "rut"),
    ("cot", "reg", "oba"),
    ("dne", "reg", "3jn"),
    ("ekp", "reg", "2co"),
    ("ema-x-emai", "reg", "act"),
    ("erk-x-epang", "reg", "php"),
    ("eyo", "reg", "2jn"),
    ("eyo", "reg", "php"),
    ("gux-x-gourmantche", "reg", "deu"),
    ("gux-x-gourmantche", "reg", "jon"),
    ("gux-x-gourmantche", "reg", "jos"),
    ("gwg", "reg", "php"),
    ("gwg", "reg", "3jn"),
    ("gwg", "reg", "2co"),
    ("gwg", "reg", "2jn"),
    ("gwg", "reg", "gal"),
    ("gwg", "reg", "rom"),
    ("hay-x-nyaihangiro", "reg", "1jn"),
    ("hay-x-nyaihangiro", "reg", "phm"),
    ("iba-x-desatempunak", "reg", "phm"),
    ("iba-x-ibanempran", "reg", "2co"),
    ("iba-x-ibanempran", "reg", "eph"),
    ("iba-x-ibanempran", "reg", "jud"),
    ("iba-x-ibanempran", "reg", "col"),
    ("ife-x-ana", "reg", "1th"),
    ("jid", "reg", "mat"),
    ("jni", "reg", "luk"),
    ("jni", "ulb", "luk"),
    ("kin-x-kinyabinza", "reg", "phm"),
    ("kiz", "reg", "heb"),
    # ("kiz", "reg", "php"),  # USFM is found under cloned repo with name kiz_reg; resource_lookup_dto is None (BUG?)
    # ("kiz", "reg", "1th"),  # USFM is found under cloned repo with name kiz_reg; resource_lookup_dto is None (BUG?)
    ("kiz", "reg", "jhn"),
    # ("kiz", "reg", "2jn"),  # USFM is found under cloned repo with name kiz_reg; resource_lookup_dto is None (BUG?)
    ("kki", "reg", "mat"),
    ("kki", "reg", "2ti"),
    ("kki", "reg", "1th"),
    ("kng-x-kilemfu", "reg", "jud"),
    ("kng-x-kilemfu", "reg", "eph"),
    ("kod", "reg", "2ti"),
    ("kod", "reg", "phm"),
    # ("kqi", "reg", "2th"), # unavailable from data API
    # ("kqi", "reg", "2ti"), # unavailable from data API
    # ("kqi", "reg", "mrk"), # book no longer available from data api
    ("kqi", "reg", "heb"),
    # ("kqi", "reg", "1pe"), # unavailable from data API
    # ("kqi", "reg", "tit"), # unavailable from data API
    ("ksm", "reg", "rom"),
    ("ksm", "reg", "1pe"),
    ("ksm", "reg", "2ti"),
    ("ksm", "reg", "heb"),
    ("ksm", "reg", "col"),
    ("ksm", "reg", "2pe"),
    ("kyt", "reg", "2ti"),
    ("kyt", "reg", "eph"),
    ("lbx-x-capuracu", "reg", "mrk"),
    ("lch-ZM-luchazi", "reg", "gen"),
    ("ldo", "reg", "1co"),
    ("leb-x-bisa", "reg", "zep"),
    ("lio", "reg", "phm"),
    ("lks", "reg", "heb"),
    ("lky", "reg", "jas"),
    ("lky", "reg", "2th"),
    ("lbx-x-capuracu", "reg", "eph"),
    ("mfq-x-mual", "reg", "1ki"),
    ("mgs", "reg", "php"),
    ("mgs", "reg", "2th"),
    ("mhi-x-burolo", "reg", "mat"),
    ("mhi-x-burolo", "reg", "2jn"),
    ("mhi-x-burolo", "reg", "2th"),
    ("mhi-x-burolo", "reg", "1pe"),
    ("mhi-x-burolo", "reg", "2th"),
    ("mhy-x-benualima", "reg", "mrk"),
    # ("mwe", "reg", "tit"),  # book is available as choice, but resource not cloned?
    # ("mxo", "reg", "mrk"),  # not currently unavailable from data API
    ("nak-x-bileki", "reg", "mat"),
    ("nak-x-bileki", "reg", "1ti"),
    ("nak-x-bileki", "reg", "eph"),
    ("nak-x-bileki", "reg", "2ti"),
    ("nak-x-bileki", "reg", "jas"),
    ("nak-x-bileki", "reg", "mrk"),
    ("ndc-x-chibangwe", "reg", "mrk"),
    ("ndc-x-chidanda", "reg", "luk"),
    ("ndc-x-chidanda", "reg", "gal"),
    ("nfd", "reg", "gal"),
    ("nfd", "reg", "2th"),
    ("nfd", "reg", "2ti"),
    ("nfd", "reg", "heb"),
    # ("nhx", "reg", "jos"),  # not currently available from data API
    ("nnb-x-kishula", "reg", "mrk"),
    ("not", "reg", "jos"),
    ("now", "reg", "mic"),
    ("nue", "reg", "php"),
    ("nya-x-nyanja", "reg", "jon"),
    ("nyj", "reg", "col"),
    ("nyj", "reg", "nam"),
    ("nyj", "reg", "hag"),
    # ("nyj-x-kitiri", "reg", "2th"),  # failed to fix; repo is cloned; I don't see obvious source issue
    ("nyn-x-runyaruguru", "reg", "1co"),
    ("nyr", "reg", "mat"),
    ("nyr", "reg", "php"),
    ("nyr", "reg", "3jn"),
    ("nyr", "reg", "jud"),
    ("nyr", "reg", "jas"),
    ("nza-x-mbembnthal", "reg", "act"),
    ("nza-x-mbembnthal", "reg", "luk"),
    ("nza-x-mbembnthal", "reg", "jud"),
    ("okv-x-bokoro", "reg", "2co"),
    ("okv-x-bokoro", "reg", "1jn"),
    ("okv-x-bokoro", "reg", "php"),
    ("okv-x-bokoro", "reg", "jud"),
    ("okv-x-bokoro", "reg", "jas"),
    ("omw-x-bonta", "reg", "1co"),
    ("ors-x-oranglau", "reg", "mrk"),
    ("ors-x-oranglau", "reg", "jhn"),
    ("pip", "reg", "1ti"),
    ("pip", "reg", "2co"),
    ("pip", "reg", "2th"),
    ("pip", "reg", "rom"),
    ("pip", "reg", "mat"),
    ("pse-x-riauasli", "reg", "luk"),
    # ("rmp", "ulb", "jas"),  # failed to fix; repo is cloned and source looks good other than duplicate \c markers, but we handle those (BUG?)
    ("ruc", "reg", "jhn"),
    ("ruc", "reg", "1ti"),
    ("rw-x-kinyabwisha", "reg", "num"),
    ("rw-x-kinyabwisha", "reg", "luk"),
    ("saw", "reg", "1ch"),
    ("saw", "reg", "luk"),
    ("saw", "reg", "psa"),
    ("saw", "reg", "job"),
    ("saw", "reg", "sng"),
    ("saw", "reg", "dan"),
    ("saw", "reg", "est"),
    ("sbp", "reg", "phm"),
    ("sbp", "reg", "2th"),
    ("sbp", "reg", "1ti"),
    ("sbp", "reg", "2ti"),
    ("sbp", "reg", "eph"),
    ("sbs-x-chiikuhane", "reg", "jon"),
    ("scg-x-mayau", "reg", "luk"),
    ("scg-x-mayau", "reg", "jas"),
    ("sdm-x-beginci", "reg", "2th"),
    ("sdm-x-beginci", "reg", "2pe"),
    ("set-x-csentani", "reg", "mrk"),
    ("set-x-csentani", "reg", "2jn"),
    ("sie-x-makoma", "reg", "2th"),
    ("sie-x-makoma", "reg", "2jn"),
    ("sie-x-makoma", "reg", "rut"),
    ("spy-x-bongomek", "reg", "phm"),
    ("spy-x-bongomek", "reg", "2jn"),
    ("spy-x-pok", "reg", "jud"),
    ("spy-x-pok", "reg", "3jn"),
    ("ssc-x-kine", "reg", "2jn"),
    ("tbp-x-airo", "reg", "php"),
    ("thr", "reg", "tit"),
    ("ttl-x-totelnamib", "reg", "3jn"),
    ("txy", "reg", "1co"),
    ("txy", "reg", "2jn"),
    ("tyn", "reg", "jud"),
    ("tyn", "reg", "mrk"),
    # ("vin", "reg", "2co"), # not currently available from data API
    # ("vin", "reg", "1th"),
    # ("vin", "reg", "1ti"),
    # ("vin", "reg", "gal"),
    ("wbj", "reg", "luk"),
    ("wbj", "reg", "tit"),
    ("wbj", "reg", "2jn"),
    ("wkd", "reg", "mrk"),
    ("wkd", "reg", "3jn"),
    ("wsk-x-makitu", "reg", "php"),
    ("wsk-x-makitu", "reg", "3jn"),
    ("xem-x-karambai", "reg", "luk"),
    ("xem-x-karambai", "reg", "eph"),
    # ("xkg", "reg", "3jn"),  # failed to fix; source looks fine but could have UTF issues (BUG?)
    ("xmt", "reg", "eph"),
    ("xwg", "reg", "luk"),
    ("zga-x-mahanji", "reg", "php"),
    ("ziw", "reg", "1th"),
    ("ziw", "reg", "1jn"),
    ("zlm-x-kisaran", "reg", "2ti"),
]


# List of regex patterns to detect issues before applying corrections
pattern_matchers = {
    "remove_null_bytes_and_control_characters": r"[\x00-\x1F]+",
    "fix_dot_after_verse_number": r"(\\v\s*\d+)\s*\.\s*(\S)",
    "fix_verse_marker_without_v": r"\\(\d+)\s*\.?\s*(\S+)",
    "fix_missing_space_before_number": r"(?<!\\c\s)(?<!\\v\s)(?<!\\v\s\d)(?<!\\q\d\s)(?<!\\li)(?<!\\li\d)(?<=\S)(?<!\\\S)(\d+)(?=\s)",
    "fix_missing_space_after_number": r"(\s+|^)(\d+)(\S+)",
    "fix_missing_space_before_verse_marker": r"(\S)(\\v\s+\d+)",
    "fix_standalone_verse_numbers": r"(?<!\\)(?<!\\c\s)(?<!\\v\s)(?<!\\v\s\d)(?<!\\q\d\s)(?<!\\li)(?<!\\li\d)\b(\d+)\b(?=\s|$|[^\d\w])",
    "fix_standalone_verse_number_and_period": r"(?<!\\)(?<!\\c\s)(?<!\\v\s)(?<!\\v\s\d)(?<!\\q\d\s)(?<!\\li)(?<!\\li\d)\b(\d+)\.\s*(.*?)(?=\s|$|[^\d\w])",
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
        # logger.debug(
        #     "match.group(1): %s",
        #     match.group(1),
        # )
        character_before_number = content[match.start() - 1]
        character_before_before_number = content[match.start() - 2]
        # logger.debug("character_before_number: %s", character_before_number)
        if (
            character_before_number.isdigit()
            and match.group(1).isdigit()
            or character_before_number in [".", ","]  # handle 299.100 or 299,100
            and character_before_before_number.isdigit()
            and match.group(1).isdigit()
        ):
            logger.info(
                "Actually, it wasn't missing a space before number after all upon further checking"
            )
            return content
        else:
            return re.sub(
                pattern_matchers["fix_missing_space_before_number"], r" \1", content
            )
    return content


def fix_missing_space_after_number(content: str) -> str:
    matches = re.findall(compiled_patterns["fix_missing_space_after_number"], content)
    for match in matches:
        if not match[2].isdigit() and match[2][0] not in [
            ":",
            "-",
            ")",
            "(",
            "[",
            "]",
            ",",
            ".",
        ]:  # Skip e.g., '(Zak 13:9)'
            replacement = match[1] + " " + match[2]
            pattern2 = f"{match[1]}{match[2]}"
            content = re.sub(pattern2, replacement, content)
    return content


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
    # goal, we check for three conditions:
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
        # Extract all standalone numbers (likely verse numbers) from
        # content but skip the first part, 6 characters, of content
        # which could contain a chapter marker and its value.
        matches = [int(m.group()) for m in re.finditer(r"\b\d+\b", content[7:])]
        # logger.debug("standalone number matches: %s", matches)
        is_ascending = all(
            earlier < later for earlier, later in zip(matches, matches[1:])
        )
        # logger.debug("is_ascending: %s", is_ascending)
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
            logger.info(
                "Actually, we can't be certain it was a standalone verse number after all upon further checking"
            )
    return content


def fix_standalone_verse_number_and_period(content: str) -> str:
    # E.g., in Russian (ru) some of the USFM exhibits verse markers of the
    # form 1. rather than \v 1
    if match := compiled_patterns["fix_standalone_verse_number_and_period"].search(
        content
    ):
        # Calculate safe slice indices
        length_of_context = 50
        num_of_occurrences = 3
        start_index = max(0, match.start() - length_of_context)
        end_index = min(len(content), match.end() + length_of_context)
        context_for_standalone_verse_and_period = content[start_index:end_index]
        logger.debug(
            "context_for_standalone_verse_and_period: %s",
            context_for_standalone_verse_and_period,
        )
        # Extract all standalone number and period (likely verse numbers) from
        # content but skip the first part, 6 characters, of content
        # which could contain a chapter marker and its value.
        matches = [int(m.group(1)) for m in re.finditer(r"\b(\d+)\.", content[7:])]
        logger.debug("standalone verse number and period matches: %s", matches)
        is_ascending = all(
            earlier < later for earlier, later in zip(matches, matches[1:])
        )
        logger.debug("is_ascending: %s", is_ascending)
        num_matches = len(matches)
        if (
            not re.compile(r"""\\v \d+""").search(
                context_for_standalone_verse_and_period
            )
            and not num_matches >= num_of_occurrences
        ) or is_ascending:  # Check for non-ascending numbers
            return re.sub(
                pattern_matchers["fix_standalone_verse_number_and_period"],
                r"\\v \1 \2",
                content,
            )
        else:
            logger.info(
                "Actually, we can't be certain it was a standalone verse number and period after all upon further checking"
            )
    return content


def replace_n_with_v(content: str) -> str:
    """Replace \n used mistakenly as verse markers with \v"""
    return re.sub(pattern_matchers["replace_n_with_v"], r"""\\v""", content)


def replace_cc_with_c(content: str) -> str:
    """
    Replace two consecutive chapter markers with whitespace or newline between them with only one chapter marker
    """
    return re.sub(pattern_matchers["replace_cc_with_c"], r"\1" + "\n", content)


def replace_vv_with_v(content: str) -> str:
    """Replace \v\v, caused by other correcting functions, with \v"""
    return re.sub(pattern_matchers["replace_vv_with_v"], "\\v", content)


def replace_sv_with_s(content: str) -> str:
    r"""Replace \s\v, caused by other correcting functions, with \s"""
    return re.sub(pattern_matchers["replace_sv_with_s"], "\\s", content)


def fix_space_after_section_marker(content: str) -> str:
    """Reunite section marker with its value, caused by other correcting functions"""
    return re.sub(pattern_matchers["fix_space_after_section_marker"], r"\\s\1", content)


def replace_qv_with_q(content: str) -> str:
    r"""Replace \q\v <integer>, caused by other correcting functions, with \q<integer>"""
    return re.sub(pattern_matchers["replace_qv_with_q"], r"\\q\1", content)


def fix_usfm(
    usfm_content: str,
    lang_code: str,
    resource_type: str,
    book_code: str,
) -> str:
    """
    Detect and correct many USFM structural issues in USFM source.
    """
    # logger.debug("Possibly defective USFM content: %s", usfm_content)
    corrected_usfm_content: str = usfm_content
    # NOTE This is called in a different place now, leaving commented out for now.
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
            "USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "fix_dot_after_verse_number",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = fix_dot_after_verse_number(corrected_usfm_content)
    if match := compiled_patterns["fix_verse_marker_without_v"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "fix_verse_marker_without_v",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = fix_verse_marker_without_v(corrected_usfm_content)
    if match := compiled_patterns["fix_missing_space_before_number"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "fix_missing_space_before_number",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = fix_missing_space_before_number(corrected_usfm_content)
    if match := compiled_patterns["fix_missing_space_after_number"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "Potential USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, if confirmed, then will attempt fix...",
            "fix_missing_space_after_number",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = fix_missing_space_after_number(corrected_usfm_content)
    if match := compiled_patterns["fix_missing_space_before_verse_marker"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "fix_missing_space_before_verse_marker",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = fix_missing_space_before_verse_marker(
            corrected_usfm_content
        )
    if match := compiled_patterns["fix_standalone_verse_numbers"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "Possible USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, if confirmed, attempt to fix...",
            "fix_standalone_verse_numbers",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = fix_standalone_verse_numbers(corrected_usfm_content)
    if match := compiled_patterns["fix_standalone_verse_number_and_period"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "Possible USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, if confirmed, attempt to fix...",
            "fix_standalone_verse_number_and_period",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = fix_standalone_verse_number_and_period(
            corrected_usfm_content
        )
    if match := compiled_patterns["replace_n_with_v"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "replace_n_with_v",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = replace_n_with_v(corrected_usfm_content)
    if match := compiled_patterns["replace_vv_with_v"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "replace_vv_with_v",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = replace_vv_with_v(corrected_usfm_content)
    if match := compiled_patterns["replace_sv_with_s"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "replace_sv_with_s",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = replace_sv_with_s(corrected_usfm_content)
    if match := compiled_patterns["fix_space_after_section_marker"].search(
        corrected_usfm_content
    ):
        logger.debug(
            "USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "fix_space_after_section_marker",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = fix_space_after_section_marker(corrected_usfm_content)
    if match := compiled_patterns["replace_qv_with_q"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "replace_qv_with_q",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = replace_qv_with_q(corrected_usfm_content)
    if match := compiled_patterns["replace_cc_with_c"].search(corrected_usfm_content):
        logger.debug(
            "USFM defect %s detected, specifically %s, context: %s, for resource: %s-%s-%s, about to attempt fix...",
            "replace_cc_with_c",
            match.group(),
            corrected_usfm_content[
                max(0, match.start() - 5) : min(
                    len(corrected_usfm_content), match.end() + 5
                )
            ],
            lang_code,
            resource_type,
            book_code,
        )
        corrected_usfm_content = replace_cc_with_c(corrected_usfm_content)
    return corrected_usfm_content
