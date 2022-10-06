"""
This module provides an alternative/experimental API for looking up
the location of a resource's asset files in the cloud and acquiring
said resource assets. This module relies, amongst others, on the
resource_lookup module.
"""

import os
import yaml

from collections.abc import Sequence
from typing import Any, Callable, Mapping, cast

from document.domain import bible_books, resource_lookup
from document.config import settings
from document.utils import file_utils

logger = settings.logger(__name__)


def shared_resource_codes_and_types(
    lang0_code: str, lang1_code: str
) -> dict[str, list[tuple[str, str, str]]]:
    lang0_results = resource_codes_and_types_for_lang(lang0_code)
    lang1_results = resource_codes_and_types_for_lang(lang1_code)
    # TODO Find intersection between the two. For now just return the
    # first.
    return lang0_results


# NOTE This function could be used to gather all the information that
# IRG/DOC cares about from translation.json in order to write it to
# another format, e.g., a database. This then could be run
# periodically to update the db from translations.json.
def resource_codes_and_types_for_lang(
    lang_code: str,
    working_dir: str = settings.working_dir(),
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
    bc_resource_types: Sequence[str] = settings.BC_RESOURCE_TYPES,
) -> dict[str, list[tuple[str, str, str]]]:
    """
    Obtain the max resource codes available for each supported
    resource type for a particular language.

    >>> from document.config import settings
    >>> settings.IN_CONTAINER = False
    >>> settings.IN_CONTAINER
    False
    >>> from document.domain import resource_lookup_experimental
    >>> import logging
    >>> import sys
    >>> logger.addHandler(logging.StreamHandler(sys.stdout))
    >>> import pprint
    >>> # pprint.pprint(resource_lookup_experimental.resource_codes_and_types_for_lang("fr"))
    >>> # pprint.pprint(resource_lookup_experimental.resource_codes_and_types_for_lang("en"))
    >>> pprint.pprint(resource_lookup_experimental.resource_codes_and_types_for_lang("ndh-x-chindali"))
    {'reg': [('mat',
              'Matthew',
              'https://content.bibletranslationtools.org/richard/ndh-x-chindali_mat_text_reg'),
             ('mrk',
              'Mark',
              'https://content.bibletranslationtools.org/richard/ndh-x-chindali_mrk_text_reg'),
             ('luk',
              'Luke',
              'https://content.bibletranslationtools.org/richard/ndh-x-chindali_luk_text_reg'),
             ('act',
              'Acts',
              'https://content.bibletranslationtools.org/richard/ndh-x-chindali_act_text_ulb'),
             ('gal',
              'Galatians',
              'https://content.bibletranslationtools.org/richard/ndh-x-chindali_gal_text_ulb')]}
    >>> # resource_lookup_experimental.resource_codes_and_types_for_lang("kbt")
    >>> # pprint.pprint(resource_lookup_experimental.resource_codes_and_types_for_lang("pt-br"))
    """

    resource_type_max_resource_codes_map: dict[str, list[tuple[str, str, str]]] = {}
    data = resource_lookup.fetch_source_data(working_dir, translations_json_location)
    for item in [lang for lang in data if lang["code"] == lang_code]:
        lang_code = item["code"]
        # if lang_code in lang_code_filter_list:
        #     logger.debug("skipping lang_code: %s", lang_code)
        #     continue
        # logger.debug("lang_code: %s", lang_code)
        for resource_type in item["contents"]:
            if resource_lookup.supported_resource_type(
                lang_code, resource_type["code"]
            ):
                # logger.debug("resource_type: %s", resource_type["code"])

                subcontents_resource_codes_having_single_usfms = (
                    resource_codes_and_links(
                        "usfm", resource_type["subcontents"], identity
                    )
                )
                # logger.debug(
                #     "subcontents_resource_codes_having_single_usfms: %s",
                #     subcontents_resource_codes_having_single_usfms,
                # )
                subcontents_resource_codes_having_zips: list[tuple[str, str, str]] = []
                subcontents_resource_codes_having_git_repos: list[
                    tuple[str, str, str]
                ] = []
                contents_resource_codes_having_zips: list[tuple[str, str, str]] = []
                contents_resource_codes_having_git_repos: list[
                    tuple[str, str, str]
                ] = []
                if not subcontents_resource_codes_having_single_usfms:
                    subcontents_resource_codes_having_zips = resource_codes_and_links(
                        "zip", resource_type["subcontents"], identity
                    )
                    # logger.debug(
                    #     "subcontents_resource_codes_having_zips: %s",
                    #     subcontents_resource_codes_having_zips,
                    # )
                    if not subcontents_resource_codes_having_zips:
                        subcontents_resource_codes_having_git_repos = (
                            resource_codes_and_links(
                                "Download",
                                resource_type["subcontents"],
                                parse_repo_url,
                            )
                        )
                        # logger.debug(
                        #     "subcontents_resource_codes_having_git_repos: %s",
                        #     subcontents_resource_codes_having_git_repos,
                        # )
                        if not subcontents_resource_codes_having_git_repos:
                            # Typically TN, TQ, and TW asset files are not addressed according to a
                            # resource code in translations.json. Rather, in translations.json they
                            # are usually located at the contents > links level and their URL points
                            # to a zip or git repo whith contains asset files for many resource
                            # codes. You have to acquire and unzip or clone said files and look in
                            # the resulting directory (for a manifest file, if provided, or by
                            # globbing for file names) to determine what resource codes are
                            # supported.
                            contents_resource_codes_having_zips = (
                                resource_code_and_link_from_contents_zips(
                                    "zip", lang_code, resource_type, identity
                                )
                            )
                            # logger.debug(
                            #     "contents_resource_codes_having_zips: %s",
                            #     contents_resource_codes_having_zips,
                            # )
                            if not contents_resource_codes_having_zips:
                                contents_resource_codes_having_git_repos = (
                                    resource_code_and_link_from_contents_git_repos(
                                        "Download",
                                        lang_code,
                                        resource_type,
                                        parse_repo_url,
                                    )
                                )
                                # logger.debug(
                                #     "contents_resource_codes_having_git_repos: %s",
                                #     contents_resource_codes_having_git_repos,
                                # )

                # Each loop iteration covers a different resource type for the current
                # lang_code. Amongst the assets found for the current resource type,
                # which one has the max number of resource codes:
                all_lists = [
                    subcontents_resource_codes_having_single_usfms,
                    subcontents_resource_codes_having_zips,
                    subcontents_resource_codes_having_git_repos,
                    contents_resource_codes_having_zips,
                    contents_resource_codes_having_git_repos,
                ]
                # logger.debug("all_lists: %s", all_lists)
                non_empty_lists = [lst for lst in all_lists if lst]
                # logger.debug("non_empty_lists: %s", non_empty_lists)
                if non_empty_lists:
                    resource_type_with_max_resource_codes = max(
                        non_empty_lists,
                        key=lambda lst: len(lst),
                    )
                else:
                    resource_type_with_max_resource_codes = []
                # logger.debug(
                #     "resource_type_with_max_resource_codes: %s",
                #     resource_type_with_max_resource_codes,
                # )
                resource_type_max_resource_codes_map[
                    resource_type["code"]
                ] = resource_type_with_max_resource_codes
    return resource_type_max_resource_codes_map


def resource_codes_and_types_for_langs(
    working_dir: str = settings.working_dir(),
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
    bc_resource_types: Sequence[str] = settings.BC_RESOURCE_TYPES,
) -> dict[str, list[tuple[str, str, str]]]:
    """
    Obtain the max resource codes available for each supported
    resource type for every language.

    >>> from document.config import settings
    >>> # Setting IN_CONTAINER in the next line doesn't always persist for subsequent
    >>> # repl lines below. If that happens then start the test like
    >>> # IN_CONTAINER=False python backend/document/domain/resource_lookup_experimental.py
    >>> settings.IN_CONTAINER = False
    >>> settings.IN_CONTAINER
    False
    >>> from document.domain import resource_lookup_experimental
    >>> import logging
    >>> import sys
    >>> logger.addHandler(logging.StreamHandler(sys.stdout))
    >>> import pprint
    >>> # NOTE Comment for now as takes so long.
    >>> # pprint.pprint(resource_lookup_experimental.resource_codes_and_types_for_langs())
    """

    resource_type_max_resource_codes_map: dict[str, list[tuple[str, str, str]]] = {}
    data = resource_lookup.fetch_source_data(working_dir, translations_json_location)
    for item in [lang for lang in data]:
        lang_code = item["code"]
        # if lang_code in lang_code_filter_list:
        #     logger.debug("skipping lang_code: %s", lang_code)
        #     continue
        # logger.debug("lang_code: %s", lang_code)
        for resource_type in item["contents"]:
            if resource_lookup.supported_resource_type(
                lang_code, resource_type["code"]
            ):
                # logger.debug("resource_type: %s", resource_type["code"])

                subcontents_resource_codes_having_single_usfms = (
                    resource_codes_and_links(
                        "usfm", resource_type["subcontents"], identity
                    )
                )
                # logger.debug(
                #     "subcontents_resource_codes_having_single_usfms: %s",
                #     subcontents_resource_codes_having_single_usfms,
                # )
                subcontents_resource_codes_having_zips: list[tuple[str, str, str]] = []
                subcontents_resource_codes_having_git_repos: list[
                    tuple[str, str, str]
                ] = []
                contents_resource_codes_having_zips: list[tuple[str, str, str]] = []
                contents_resource_codes_having_git_repos: list[
                    tuple[str, str, str]
                ] = []
                if not subcontents_resource_codes_having_single_usfms:
                    subcontents_resource_codes_having_zips = resource_codes_and_links(
                        "zip", resource_type["subcontents"], identity
                    )
                    # logger.debug(
                    #     "subcontents_resource_codes_having_zips: %s",
                    #     subcontents_resource_codes_having_zips,
                    # )
                    if not subcontents_resource_codes_having_zips:
                        subcontents_resource_codes_having_git_repos = (
                            resource_codes_and_links(
                                "Download",
                                resource_type["subcontents"],
                                parse_repo_url,
                            )
                        )
                        # logger.debug(
                        #     "subcontents_resource_codes_having_git_repos: %s",
                        #     subcontents_resource_codes_having_git_repos,
                        # )
                        if not subcontents_resource_codes_having_git_repos:
                            # Typically TN, TQ, and TW asset files are not addressed according to a
                            # resource code in translations.json. Rather, in translations.json they
                            # are usually located at the contents > links level and their URL points
                            # to a zip or git repo whith contains asset files for many resource
                            # codes. You have to acquire and unzip or clone said files and look in
                            # the resulting directory (for a manifest file, if provided, or by
                            # globbing for file names) to determine what resource codes are
                            # supported.
                            contents_resource_codes_having_zips = (
                                resource_code_and_link_from_contents_zips(
                                    "zip", lang_code, resource_type, identity
                                )
                            )
                            # logger.debug(
                            #     "contents_resource_codes_having_zips: %s",
                            #     contents_resource_codes_having_zips,
                            # )
                            if not contents_resource_codes_having_zips:
                                contents_resource_codes_having_git_repos = (
                                    resource_code_and_link_from_contents_git_repos(
                                        "Download",
                                        lang_code,
                                        resource_type,
                                        parse_repo_url,
                                    )
                                )
                                # logger.debug(
                                #     "contents_resource_codes_having_git_repos: %s",
                                #     contents_resource_codes_having_git_repos,
                                # )

                # Each loop iteration covers a different resource type for the current
                # lang_code. Amongst the assets found for the current resource type,
                # which one has the max number of resource codes:
                all_lists = [
                    subcontents_resource_codes_having_single_usfms,
                    subcontents_resource_codes_having_zips,
                    subcontents_resource_codes_having_git_repos,
                    contents_resource_codes_having_zips,
                    contents_resource_codes_having_git_repos,
                ]
                # logger.debug("all_lists: %s", all_lists)
                non_empty_lists = [lst for lst in all_lists if lst]
                # logger.debug("non_empty_lists: %s", non_empty_lists)
                if non_empty_lists:
                    resource_type_with_max_resource_codes = max(
                        non_empty_lists,
                        key=lambda lst: len(lst),
                    )
                else:
                    resource_type_with_max_resource_codes = []
                # logger.debug(
                #     "resource_type_with_max_resource_codes: %s",
                #     resource_type_with_max_resource_codes,
                # )
                resource_type_max_resource_codes_map[
                    resource_type["code"]
                ] = resource_type_with_max_resource_codes
    return resource_type_max_resource_codes_map


def identity(url: str) -> str:
    return url


def resource_codes_and_links(
    format: str,
    subcontents: Any,
    link_transformer_fn: Callable[[str], str],
    book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
) -> list[tuple[str, str, str]]:
    tuples = [
        (
            resource_code["code"],
            # Deal with TW manifests which have the
            # only project in projects as 'bible'.
            book_names[resource_code["code"]]
            if resource_code["code"] in book_names.keys()
            else "",
            [
                link_transformer_fn(link["url"])
                for link in resource_code["links"]
                if link["url"] and link["format"] == format
            ],
        )
        for resource_code in subcontents
        if [
            link_transformer_fn(link["url"])
            for link in resource_code["links"]
            if link["url"] and link["format"] == format
        ]
    ]
    return [
        (
            resource_code,
            name,
            cast(str, link[0] if isinstance(link, list) else link),
        )
        for resource_code, name, link in tuples
    ]


def resource_code_and_link_from_contents_zips(
    format: str,
    lang_code: str,
    resource_type: Any,
    link_transformer_fn: Callable[[str], str],
    book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
) -> list[tuple[str, str, str]]:
    resource_dir = resource_lookup.resource_directory(lang_code, resource_type["code"])
    resource_codes: list[tuple[str, str, str]] = []
    links = [
        link["url"]
        for link in resource_type["links"]
        if link["url"] and link["format"] == format
    ]
    for url in links:
        resource_filepath = os.path.join(
            resource_dir,
            url.rpartition(os.path.sep)[2],
        )
        # logger.debug("resource_filepath: %s", resource_filepath)
        if file_utils.asset_file_needs_update(resource_filepath):
            resource_lookup.prepare_resource_directory(lang_code, resource_type["code"])
            resource_lookup.download_asset(url, resource_filepath)
            resource_lookup.unzip_asset(
                lang_code,
                resource_type["code"],
                resource_filepath,
            )
        # When a git repo is cloned or when a zip file is
        # unzipped, a subdirectory of resource_dir is created
        # as a result. Update resource_dir to point to that
        # subdirectory.
        resource_dir = resource_lookup.update_resource_dir(
            lang_code, resource_type["code"]
        )
        # Now look for manifest and if it is avialable use it to return the list of resource codes.

        manifest_path = ""
        # if resource_type["code"] not in tw_resource_types:
        if os.path.exists(f"{resource_dir}/manifest.yaml"):
            manifest_path = f"{resource_dir}/manifest.yaml"
            with open(manifest_path, "r") as file:
                yaml_content = yaml.safe_load(file)
                resource_codes = [
                    (
                        resource_code["identifier"],
                        # Deal with TW manifests which have the
                        # only project in projects as 'bible'.
                        book_names[resource_code["identifier"]]
                        if resource_code["identifier"] in book_names.keys()
                        else "",
                        resource_code["path"],
                    )
                    for resource_code in yaml_content["projects"]
                ]

        elif os.path.exists(f"{resource_dir}/projects.yaml"):
            manifest_path = f"{resource_dir}/projects.yaml"
            with open(manifest_path, "r") as file:
                yaml_content = yaml.safe_load(file)
                resource_codes = [
                    (
                        resource_code["identifier"],
                        # Deal with TW manifests which have the
                        # only project in projects as 'bible'.
                        book_names[resource_code["identifier"]]
                        if resource_code["identifier"] in book_names.keys()
                        else "",
                        resource_code["path"],
                    )
                    for resource_code in yaml_content
                ]

        # TODO If manifest was not found, then glob filenames for resource codes provided.
        if not resource_codes:
            logger.debug("resource_codes is empty")
            pass

    contents_resource_codes = [
        # (resource_code_path_tuple[0], resource_code_path_tuple[1], [])
        (resource_code_tuple[0], resource_code_tuple[1], resource_code_tuple[2])
        for resource_code_tuple in resource_codes
    ]
    return contents_resource_codes


def resource_code_and_link_from_contents_git_repos(
    format: str,
    lang_code: str,
    resource_type: Any,
    link_transformer_fn: Callable[[str], str],
    book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
) -> list[tuple[str, str, str]]:

    links = [
        link_transformer_fn(link["url"])
        for link in resource_type["links"]
        if link["url"] and link["format"] == format
    ]
    # logger.debug("contents_links_git_repos: %s", contents_links_git_repos)
    resource_codes: list[tuple[str, str, str]] = []
    resource_dir = resource_lookup.resource_directory(lang_code, resource_type["code"])
    for url in links:
        resource_filepath = os.path.join(
            resource_dir,
            url.rpartition(os.path.sep)[2],
        )
        # logger.debug("resource_filepath: %s", resource_filepath)
        if file_utils.asset_file_needs_update(resource_filepath):
            resource_lookup.clone_git_repo(url, resource_filepath)
        # When a git repo is cloned or when a zip file is
        # unzipped, a subdirectory of resource_dir is created
        # as a result. Update resource_dir to point to that
        # subdirectory.
        resource_dir = resource_lookup.update_resource_dir(
            lang_code, resource_type["code"]
        )
        # Now look for manifest and if it is avialable use it to return the list of resource codes.
        manifest_path = ""
        # if resource_type["code"] not in tw_resource_types:
        if os.path.exists(f"{resource_dir}/manifest.yaml"):
            manifest_path = f"{resource_dir}/manifest.yaml"
            with open(manifest_path, "r") as file:
                yaml_content = yaml.safe_load(file)
                resource_codes = [
                    (
                        resource_code["identifier"],
                        # Deal with TW manifests which have the
                        # only project in projects as 'bible'.
                        book_names[resource_code["identifier"]]
                        if resource_code["identifier"] in book_names.keys()
                        else "",
                        resource_code["path"],
                    )
                    for resource_code in yaml_content["projects"]
                ]

        elif os.path.exists(f"{resource_dir}/projects.yaml"):
            manifest_path = f"{resource_dir}/projects.yaml"
            with open(manifest_path, "r") as file:
                yaml_content = yaml.safe_load(file)
                resource_codes = [
                    (
                        resource_code["identifier"],
                        # Deal with TW manifests which have the
                        # only project in projects as 'bible'.
                        book_names[resource_code["identifier"]]
                        if resource_code["identifier"] in book_names.keys()
                        else "",
                        resource_code["path"],
                    )
                    for resource_code in yaml_content
                ]

        # TODO If manifest was not found, then glob filenames for resource codes provided.
        if not resource_codes:
            logger.debug("resource_codes empty")
            pass

    contents_resource_codes = [
        # (resource_code_path_tuple[0], resource_code_path_tuple[1], [])
        (resource_code_tuple[0], resource_code_tuple[1], resource_code_tuple[2])
        for resource_code_tuple in resource_codes
    ]
    return contents_resource_codes


# Make mypy and max function where this is used happy
def parse_repo_url(url: str) -> str:
    parsed_url = resource_lookup._parse_repo_url(url)
    if not parsed_url:
        parsed_url = ""
    return parsed_url


# NOTE An alternative/experimental (different approach), yet ultimately non-performant version.
def resource_codes_for_lang(
    lang_code: str,
    jsonpath_str: str = settings.RESOURCE_CODES_FOR_LANG_JSONPATH,
    book_names: Mapping[str, str] = bible_books.BOOK_NAMES,
    book_numbers: Mapping[str, str] = bible_books.BOOK_NUMBERS,
    working_dir: str = settings.working_dir(),
    translations_json_location: str = settings.TRANSLATIONS_JSON_LOCATION,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
) -> Sequence[tuple[str, str]]:
    """
    Convenience method that can be called, e.g., from the UI, to
    get the set of all resource codes for a particular lang_code.

    >>> from document.config import settings
    >>> settings.IN_CONTAINER = False
    >>> from document.domain import resource_lookup
    >>> # Hack to ignore logging output: https://stackoverflow.com/a/33400983/3034580
    >>> ();data = resource_lookup.resource_codes_for_lang("fr");() # doctest:+ELLIPSIS
    (...)
    >>> list(data)
    [('gen', 'Genesis'), ('exo', 'Exodus'), ('lev', 'Leviticus'), ('num', 'Numbers'), ('deu', 'Deuteronomy'), ('jos', 'Joshua'), ('jdg', 'Judges'), ('rut', 'Ruth'), ('1sa', '1 Samuel'), ('2sa', '2 Samuel'), ('1ki', '1 Kings'), ('2ki', '2 Kings'), ('1ch', '1 Chronicles'), ('2ch', '2 Chronicles'), ('ezr', 'Ezra'), ('neh', 'Nehemiah'), ('est', 'Esther'), ('job', 'Job'), ('psa', 'Psalms'), ('pro', 'Proverbs'), ('ecc', 'Ecclesiastes'), ('sng', 'Song of Solomon'), ('isa', 'Isaiah'), ('jer', 'Jeremiah'), ('lam', 'Lamentations'), ('ezk', 'Ezekiel'), ('dan', 'Daniel'), ('hos', 'Hosea'), ('jol', 'Joel'), ('amo', 'Amos'), ('oba', 'Obadiah'), ('jon', 'Jonah'), ('mic', 'Micah'), ('nam', 'Nahum'), ('hab', 'Habakkuk'), ('zep', 'Zephaniah'), ('hag', 'Haggai'), ('zec', 'Zechariah'), ('mal', 'Malachi'), ('mat', 'Matthew'), ('mrk', 'Mark'), ('luk', 'Luke'), ('jhn', 'John'), ('act', 'Acts'), ('rom', 'Romans'), ('1co', '1 Corinthians'), ('2co', '2 Corinthians'), ('gal', 'Galatians'), ('eph', 'Ephesians'), ('php', 'Philippians'), ('col', 'Colossians'), ('1th', '1 Thessalonians'), ('2th', '2 Thessalonians'), ('1ti', '1 Timothy'), ('2ti', '2 Timothy'), ('tit', 'Titus'), ('phm', 'Philemon'), ('heb', 'Hebrews'), ('jas', 'James'), ('1pe', '1 Peter'), ('2pe', '2 Peter'), ('1jn', '1 John'), ('2jn', '2 John'), ('3jn', '3 John'), ('jud', 'Jude'), ('rev', 'Revelation')]
    """
    results = resource_codes_and_types_for_lang(lang_code)
    usfm_resource_type_with_max_resource_codes: list[tuple[str, str, str]] = []
    usfm_keys = [key for key in results.keys() if key in usfm_resource_types]
    if (
        usfm_keys and len(usfm_keys) > 1
    ):  # More than one USFM type is available for lang_code
        # logger.debug("usfm_keys: %s", usfm_keys)
        # logger.debug(
        #     "resource_codes for %s: %s",
        #     usfm_keys[0],
        #     [code for code, name, link in results[usfm_keys[0]]],
        # )
        # logger.debug(
        #     "resource_codes for %s: %s",
        #     usfm_keys[1],
        #     [code for code, name, link in results[usfm_keys[1]]],
        # )
        usfm_resource_type_with_max_resource_codes = max(
            [results[usfm_keys[0]], results[usfm_keys[1]]], key=lambda entry: len(entry)
        )
    elif (
        usfm_keys and len(usfm_keys) == 1
    ):  # Just one USFM type is available for lang_code
        usfm_resource_type_with_max_resource_codes = results[usfm_keys[0]]

    resource_codes = [
        (code, name) for code, name, link in usfm_resource_type_with_max_resource_codes
    ]
    logger.debug("resource_codes: %s", resource_codes)
    return sorted(
        resource_codes,
        key=lambda resource_code_name_pair: book_numbers[resource_code_name_pair[0]],
    )


if __name__ == "__main__":

    # To run the doctests in this module, in the root of the project do:
    # python backend/document/domain/resource_lookup_experimental.py
    # or
    # python backend/document/domain/resource_lookup_experimental.py -v
    #
    # See https://docs.python.org/3/library/doctest.html
    # for more details.
    #
    # NOTE If you have issues with /working/temp being used rather than
    # working/temp then run the tests as above but with
    # IN_CONTAINER=False prepended.
    import doctest

    doctest.testmod()
