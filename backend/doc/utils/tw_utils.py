"""
Useful functions that are not class or instance specific for TW
resources that we use in multiple places.
"""

import os
import pathlib
import re
import time
from glob import glob
from typing import Optional, Sequence

from doc.config import settings
from doc.domain import parsing, resource_lookup
from doc.domain.model import ResourceRequest, TWBook, TWNameContentPair, USFMBook


logger = settings.logger(__name__)

TW = "tw"
OPENING_H3_FMT_STR: str = "<h3>{}"
OPENING_H3_WITH_ID_FMT_STR: str = '<h3 id="{}-{}">{}'


def translation_word_filepaths(resource_dir: str) -> list[str]:
    """
    Get the file paths to the translation word files located
    recursively in resource_dir.
    """
    filepaths = glob("{}/bible/kt/*.md".format(resource_dir))
    filepaths.extend(glob("{}/bible/names/*.md".format(resource_dir)))
    filepaths.extend(glob("{}/bible/other/*.md".format(resource_dir)))
    return filepaths


def localized_translation_word(
    translation_word_content: str,
) -> str:
    """
    Get the localized translation word from the
    translation_word_content.

    Sometimes a translation word file has as its first header a list
    of various forms of the word. If that is the case we use the first
    form of the word in the list.
    """
    first_line = translation_word_content.split("\n")[0]
    first_line_components = first_line.split("# ")
    localized_translation_word = (
        first_line_components[1] if len(first_line_components) >= 2 else ""
    )
    if "," in localized_translation_word:
        # logger.debug(
        #     "localized_translation_word: %s", localized_translation_word
        # )
        # In this case, the localized word is actually multiple forms of the
        # word separated by commas, use the first form of the word.
        localized_translation_word = localized_translation_word.split(",")[0]
        # logger.debug(
        #     "Updated localized_translation_word: %s", localized_translation_word
        # )
    localized_translation_word = str.strip(localized_translation_word)
    return localized_translation_word


def tw_resource_dir(lang_code: str) -> Optional[str]:
    """
    Return the location of the TW resource asset directory given the
    lang_code of the language under consideration. The location is
    based on an established convention for the directory structure to
    be consistent across lang_code, resource_type, and book_code
    combinations.
    """
    # This is a bit hacky to "know" how to derive the actual directory path
    # file pattern/convention to expect and use it literally. But, Being
    # able to derive the tw_resource_dir location from only a lang_code a
    # constant, TW, and a convention allows us to decouple TWResource from
    # other Resource subclass instances. They'd be coupled if we had
    # to pass the value of TWResource's resource_dir to Resource
    # subclasses otherwise. It is a design tradeoff.
    tw_resource_dir_candidates = glob(
        "{}/{}_{}*/{}_{}*".format(
            settings.RESOURCE_ASSETS_DIR, lang_code, TW, lang_code, TW
        )
    )
    # If tw_resource_dir_candidates is empty it is because the user
    # did not request a TW resource as part of their document request
    # which is a valid state of affairs of course. We return the empty
    # string in such cases.
    return tw_resource_dir_candidates[0] if tw_resource_dir_candidates else None


# Some document requests don't include a resource request for
# translation words. In such cases there wouldn't be a tw_resource_dir
# associated with the request (though there could be the actual TW
# resource asset files on disk from a previous document request - we
# wouldn't make the assumption that such files were there however)
# therefore we can't require tw_resource_dir as a precondition.
def translation_words_dict(tw_resource_dir: Optional[str]) -> dict[str, str]:
    """
    Given the path to the TW resource asset files, return a dictionary
    of translation word to translation word filepath mappings,
    otherwise return an empty dictionary.
    """
    translation_words_dict: dict[str, str] = {}
    if tw_resource_dir is not None:
        filepaths = translation_word_filepaths(tw_resource_dir)
        translation_words_dict = {
            pathlib.Path(os.path.basename(word_filepath)).stem: word_filepath
            for word_filepath in filepaths
        }
    return translation_words_dict


def translation_words_section(
    tw_book: TWBook,
    usfm_books: Optional[Sequence[USFMBook]],
    limit_words: bool,
    resource_requests: Sequence[ResourceRequest],
    resource_type_name_fmt_str: str = "<h2>{}</h2>",
) -> str:
    """
    Build and return the translation words definition section, i.e.,
    the list of all translation words for this language, book combination.
    Limit the translation words to only those that appear in the USFM
    resource chosen if limit_words is True and a USFM resource was also
    chosen otherwise include all the translation words for the language.
    """
    content = []
    if tw_book.name_content_pairs:
        content.append(resource_type_name_fmt_str.format(tw_book.resource_type_name))
    selected_name_content_pairs = get_selected_name_content_pairs(
        tw_book, usfm_books, limit_words, resource_requests
    )
    for name_content_pair in selected_name_content_pairs:
        content.append(name_content_pair_content(name_content_pair, tw_book))
    return "".join(content)


def get_selected_name_content_pairs(
    tw_book: TWBook,
    usfm_books: Optional[Sequence[USFMBook]],
    limit_words: bool,
    resource_requests: Sequence[ResourceRequest],
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
) -> list[TWNameContentPair]:
    selected_name_content_pairs = []
    if usfm_books and limit_words:
        selected_name_content_pairs = filter_name_content_pairs(tw_book, usfm_books)
    elif (
        not usfm_books and limit_words
    ):  # This branch is necessarily expensive computationally and in IO
        t0 = time.time()
        usfm_books = fetch_usfm_book_content_units(resource_requests)
        selected_name_content_pairs = filter_name_content_pairs(tw_book, usfm_books)
        t1 = time.time()
        logger.info(
            "Time for acquiring and filtering TW content based on books chosen: %s",
            t1 - t0,
        )
    else:
        selected_name_content_pairs = tw_book.name_content_pairs
    return selected_name_content_pairs


def filter_name_content_pairs(
    tw_book: TWBook, usfm_books: Optional[Sequence[USFMBook]]
) -> list[TWNameContentPair]:
    selected_name_content_pairs = []
    added_pairs = set()
    if usfm_books:
        for name_content_pair in tw_book.name_content_pairs:
            for usfm_book in usfm_books:
                for chapter in usfm_book.chapters.values():
                    if re.search(
                        re.escape(name_content_pair.localized_word),
                        chapter.content,
                    ):
                        if name_content_pair not in added_pairs:
                            selected_name_content_pairs.append(name_content_pair)
                            added_pairs.add(name_content_pair)
                        break
    return selected_name_content_pairs


def contains_tw(resource_request: ResourceRequest, tw_regex: str = "tw.*") -> bool:
    """Return True if the resource_request describes a TW resource."""
    value = bool(re.compile(tw_regex).match(resource_request.resource_type))
    return value


def name_content_pair_content(
    name_content_pair: TWNameContentPair,
    tw_book: TWBook,
    # include_uses_section: bool,
) -> str:
    name_content_pair.content = modify_content_for_anchors(name_content_pair, tw_book)
    # uses_section_ = ""
    # if (
    #     include_uses_section
    #     and name_content_pair.localized_word in book_content_unit.uses
    # ):
    #     uses_section_ = uses_section(
    #         book_content_unit.uses[name_content_pair.localized_word]
    #     )
    #     name_content_pair.content = f"{name_content_pair.content}{uses_section_}"
    return name_content_pair.content


def filter_unique_by_lang_code(tw_books: Sequence[TWBook]) -> list[TWBook]:
    unique_tw_books = []
    seen_lang_codes = set()
    for tw_book in tw_books:
        lang_code = tw_book.lang_code
        if lang_code not in seen_lang_codes:
            seen_lang_codes.add(lang_code)
            unique_tw_books.append(tw_book)
    return unique_tw_books


def modify_content_for_anchors(
    name_content_pair: TWNameContentPair,
    book_content_unit: TWBook,
    opening_h3_fmt_str: str = OPENING_H3_FMT_STR,
    opening_h3_with_id_fmt_str: str = OPENING_H3_WITH_ID_FMT_STR,
) -> str:
    return name_content_pair.content.replace(
        opening_h3_fmt_str.format(name_content_pair.localized_word),
        opening_h3_with_id_fmt_str.format(
            book_content_unit.lang_code,
            name_content_pair.localized_word,
            name_content_pair.localized_word,
        ),
    )


def fetch_usfm_book_content_units(
    resource_requests: Sequence[ResourceRequest],
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
) -> list[USFMBook]:
    usfm_resource_lookup_dtos = []
    for resource_request in resource_requests:
        for usfm_type in usfm_resource_types:
            resource_lookup_dto = resource_lookup.resource_lookup_dto(
                resource_request.lang_code,
                usfm_type,
                resource_request.book_code,
            )
            if resource_lookup_dto:
                usfm_resource_lookup_dtos.append(resource_lookup_dto)
    # Determine which resource URLs were actually found.
    found_usfm_resource_lookup_dtos = [
        resource_lookup_dto
        for resource_lookup_dto in usfm_resource_lookup_dtos
        if resource_lookup_dto.url is not None
    ]
    t0 = time.time()
    resource_dirs = [
        resource_lookup.prepare_resource_filepath(dto)
        for dto in found_usfm_resource_lookup_dtos
    ]
    for resource_dir, dto in zip(resource_dirs, found_usfm_resource_lookup_dtos):
        resource_lookup.provision_asset_files(dto.url, resource_dir)
    t1 = time.time()
    logger.debug(
        "Time to provision USFM asset files (acquire and write to disk) for TW resource: %s",
        t1 - t0,
    )
    # Initialize found resources from their provisioned assets.
    usfm_book_content_units = [
        parsing.usfm_book_content(resource_lookup_dto, resource_dir, False)  # , False
        for resource_lookup_dto, resource_dir in zip(
            found_usfm_resource_lookup_dtos, resource_dirs
        )
    ]
    return usfm_book_content_units


# def uses_section(
#     uses: Sequence[TWUse],
#     translation_word_verse_section_header_str: str = settings.TRANSLATION_WORD_VERSE_SECTION_HEADER_STR,
#     unordered_list_begin_str: str = settings.UNORDERED_LIST_BEGIN_STR,
#     translation_word_verse_ref_item_fmt_str: str = settings.TRANSLATION_WORD_VERSE_REF_ITEM_FMT_STR,
#     unordered_list_end_str: str = settings.UNORDERED_LIST_END_STR,
#     book_numbers: Mapping[str, str] = bible_books.BOOK_NUMBERS,
#     book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
#     num_zeros: int = 3,
# ) -> str:
#     """
#     Construct and return the 'Uses:' section which comes at the end of
#     a translation word definition and wherein each item points to
#     verses (as targeted by lang_code, book_id, chapter_num, and
#     verse_num) wherein the word occurs.
#     """
#     html: list[str] = []
#     html.append(translation_word_verse_section_header_str)
#     html.append(unordered_list_begin_str)
#     for use in uses:
#         html_content_str = translation_word_verse_ref_item_fmt_str.format(
#             use.lang_code,
#             book_numbers[use.book_id].zfill(num_zeros),
#             str(use.chapter_num).zfill(num_zeros),
#             str(use.verse_num).zfill(num_zeros),
#             book_names[use.book_id],
#             use.chapter_num,
#             use.verse_num,
#         )
#         html.append(html_content_str)
#     html.append(unordered_list_end_str)
#     return "\n".join(html)
