"""
This module provides an API for looking up the location of a
resource's asset files in the cloud and acquiring said resource
assets.
"""

import json
import shutil
import subprocess
from functools import cache
from os import scandir
from os.path import exists, isdir, join, sep
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence
from urllib.parse import urlparse

import requests
from document.config import settings
from document.domain import exceptions, parsing
from document.domain.bible_books import BOOK_NAMES
from document.domain.model import ResourceLookupDto
from document.utils.file_utils import dir_needs_update, file_needs_update, read_file
from fastapi import HTTPException, status
from pydantic import HttpUrl

logger = settings.logger(__name__)

SOURCE_DATA_JSON_FILENAME = "resources.json"

SOURCE_GATEWAY_LANGUAGES_FILENAME = "gateway_languages.json"


@cache
def fetch_source_data(
    json_file_name: str = SOURCE_DATA_JSON_FILENAME,
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
) -> Any:
    """
    Obtain the source data, by downloading it from json_file_url, and
    then reifying it into its JSON object form.

    >>> from document.domain import resource_lookup
    >>> ();result = resource_lookup.fetch_source_data();() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    """
    json_file_path = join(working_dir, json_file_name)
    data = None
    if file_needs_update(json_file_path):
        logger.debug("About to download %s...", json_file_name)
        try:
            data = download_data(json_file_path)
            # logger.debug("data: %s", data)
        except Exception:
            logger.exception("Caught exception: ")
    else:
        if exists(json_file_path):
            logger.debug("json_file_path, %s exists", json_file_path)
            content = read_file(json_file_path)
            # logger.debug("json data: %s", content)
            data = json.loads(content)
    return data


def download_data(
    jsonfile_path: str,
    data_api_url: HttpUrl = settings.DATA_API_URL,
) -> Any:
    """
    >>> from document.domain import resource_lookup
    >>> ();result = resource_lookup.download_data("working/temp/resources.json");() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    """
    # A debug query example of how to query one language
    # query MyQuery {
    #   git_repo(
    #     where: {content: {language: {ietf_code: {_eq: "id"}}, wa_content_metadata: {status: {_eq: "Primary"}}}}
    #   ) {
    #     repo_url
    #   }
    # }
    graphql_query = """
query MyQuery {
  git_repo(
    where: {content: {wa_content_meta: {status: {_eq: "Primary"}}}}
  ) {
    repo_url
    content {
      resource_type
      language {
        english_name
        ietf_code
        national_name
        direction
      }
    }
  }
}
    """
    payload = {"query": graphql_query}
    try:
        response = requests.post(str(data_api_url), json=payload)
        if response.status_code == 200:
            data = response.json()
            logger.debug("Writing json data to: %s", jsonfile_path)
            with open(jsonfile_path, "w") as fp:
                fp.write(str(json.dumps(data["data"])))
            return data["data"]
        else:
            logger.debug(
                "Failed to get data from data API, graphql API might be down..."
            )
            response.raise_for_status()
    except Exception as e:
        return {"error": str(e)}


def fetch_gateway_languages(
    jsonfile_path: str,
    data_api_url: HttpUrl = settings.DATA_API_URL,
) -> Any:
    """
    >>> from document.domain import resource_lookup
    >>> ();result = resource_lookup.fetch_gateway_languages("working/temp/gateway_languages.json");() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    """
    graphql_query = """
query MyQuery {
  language {
    gateway_languages {
      gateway_language {
        ietf_code
        national_name
        english_name
      }
    }
  }
}
    """
    payload = {"query": graphql_query}
    try:
        response = requests.post(str(data_api_url), json=payload)
        if response.status_code == 200:
            data = response.json()
            logger.debug("Writing json data to: %s", jsonfile_path)
            with open(jsonfile_path, "w") as fp:
                fp.write(str(json.dumps(data["data"])))
            return data["data"]
        else:
            logger.debug(
                "Failed to get data from data API, graphql API might be down..."
            )
            response.raise_for_status()
    except Exception as e:
        return {"error": str(e)}


def get_gateway_languages(
    json_file_name: str = SOURCE_GATEWAY_LANGUAGES_FILENAME,
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    use_hardcoded_gateway_language_values: bool = True,
    hardcoded_gateway_languages: Sequence[str] = settings.GATEWAY_LANGUAGES,
) -> Any:
    """
    Obtain the source data, by downloading it from json_file_url, and
    then reifying it into its JSON object form.

    >>> from document.domain import resource_lookup
    >>> ();result = resource_lookup.gateway_languages();() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    """
    gateway_languages_collection = []
    if use_hardcoded_gateway_language_values:
        return hardcoded_gateway_languages
    json_file_path = join(working_dir, json_file_name)
    data = None
    if file_needs_update(json_file_path):
        logger.debug("About to download %s...", json_file_name)
        try:
            data = fetch_gateway_languages(json_file_path)
            # logger.debug("data: %s", data)
        except Exception:
            logger.exception("Caught exception: ")
    else:
        if exists(json_file_path):
            logger.debug("json_file_path, %s, does exist", json_file_path)
            content = read_file(json_file_path)
            # logger.debug("json data: %s", content)
            data = json.loads(content)
    gateway_languages = data["language"] if data and "language" in data else []
    if gateway_languages:
        for gateway_language in gateway_languages:
            languages = gateway_language["gateway_languages"]
            for language in languages:
                language_ = language["gateway_language"]
                ietf_code = language_["ietf_code"]
                national_name = language_["national_name"]
                english_name = language_["english_name"]
                if ietf_code not in gateway_languages_collection:
                    gateway_languages_collection.append(ietf_code)
    # logger.debug("gateway_languages: %s", gateway_languages_collection)
    return gateway_languages_collection


def lang_codes_and_names(
    # lang_code_filter_list: Sequence[str] = settings.LANG_CODE_FILTER_LIST,
    gateway_languages: Sequence[str] = settings.GATEWAY_LANGUAGES,
) -> Sequence[tuple[str, str, bool]]:
    """
    >>> from document.domain import resource_lookup
    >>> ();result = resource_lookup.lang_codes_and_names();() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    ('abz', 'Abui', False)
    """
    gateway_languages_ = get_gateway_languages()
    if not gateway_languages_:
        gateway_languages_ = gateway_languages
    data = fetch_source_data()
    values = []
    try:
        repos_info = data["git_repo"]
        for repo_info in repos_info:
            language_info = repo_info["content"]
            language = language_info["language"]
            ietf_code = language["ietf_code"]
            english_name = (
                language["english_name"] if "english_name" in language else ""
            )
            national_name = language["national_name"]
            is_gateway = ietf_code in gateway_languages_
            # if ietf_code not in lang_code_filter_list:
            if english_name in national_name:
                values.append((ietf_code, national_name, is_gateway))
            else:
                values.append(
                    (ietf_code, f"{national_name} ({english_name})", is_gateway)
                )

    except:
        logger.exception("Failed due to the following exception")
    unique_values = []
    seen_values = set()
    for value in values:
        if value[0] not in seen_values:
            unique_values.append(value)
            seen_values.add(value[0])
    return sorted(unique_values, key=lambda value: value[1])


# TODO This should be expanded to include any additional types (if
# there are any) that we want to be available to users.
RESOURCE_TYPE_CODES_AND_NAMES = {
    "ayt": "Bahasa Indonesian Bible",
    "bc": "Bible Commentary",
    "blv": "Portuguese Bíblia Livre",
    "cuv": "新标点和合本",
    "f10": "French Louis Segond 1910 Bible",
    "nav": "New Arabic Version (Ketab El Hayat)",
    "reg": "Bible",
    "tn": "Translation Notes",
    "tn-condensed": "Condensed Translation Notes",
    "tq": "Translation Questions",
    "tw": "Translation Words",
    # "udb": "Unlocked Dynamic Bible",  # Content team doesn't want udb used
    "ugnt": "unfoldingWord® Greek New Testament",
    "uhb": "unfoldingWord® Hebrew Bible",
    "ulb": "Unlocked Literal Bible",
}


def resource_types(lang_code: str) -> Sequence[tuple[str, str]]:
    """
    >>> from document.domain import resource_lookup
    >>> ();result = resource_lookup.resource_types("pt-br");() # doctest: +ELLIPSIS
    (...)
    >>> result
    [('blv', 'Portuguese Bíblia Livre'), ('tw', 'Translation Words'), ('tn', 'Translation Notes'), ('ulb', 'Unlocked Literal Bible'), ('tq', 'Translation Questions')]
    """
    data = fetch_source_data()
    resource_types = []
    try:
        repos_info = data["git_repo"]
        for repo_info in repos_info:
            content = repo_info["content"]
            language_info = content["language"]
            if language_info["ietf_code"] == lang_code:
                if content["resource_type"] in RESOURCE_TYPE_CODES_AND_NAMES:
                    resource_types.append(
                        (
                            content["resource_type"],
                            RESOURCE_TYPE_CODES_AND_NAMES[content["resource_type"]],
                        )
                    )
    except:
        pass
    if lang_code == "en":
        # Add tn-condensed since graphql data api doesn't support it, but DOC must
        resource_types.append(
            ("tn-condensed", RESOURCE_TYPE_CODES_AND_NAMES["tn-condensed"])
        )
    elif lang_code == "id":
        resource_types.append(("ayt", RESOURCE_TYPE_CODES_AND_NAMES["ayt"]))
    unique_values = []
    seen_values = set()
    for value in resource_types:
        if value[0] not in seen_values:
            unique_values.append(value)
            seen_values.add(value[0])
    return sorted(unique_values, key=lambda value: value[1])


def shared_book_codes(lang0_code: str, lang1_code: str) -> Sequence[tuple[str, str]]:
    """
    Given two language codes, return the intersection of resource
    codes between the two languages.

    >>> from document.domain import resource_lookup
    >>> # Hack to ignore logging output: https://stackoverflow.com/a/33400983/3034580
    >>> ();data = resource_lookup.shared_book_codes("pt-br", "es-419");() # doctest: +ELLIPSIS
    (...)
    >>> list(data)
    [('gen', 'Genesis'), ('exo', 'Exodus'), ('lev', 'Leviticus'), ('num', 'Numbers'), ('deu', 'Deuteronomy'), ('jos', 'Joshua'), ('jdg', 'Judges'), ('rut', 'Ruth'), ('1sa', '1 Samuel'), ('2sa', '2 Samuel'), ('1ki', '1 Kings'), ('2ki', '2 Kings'), ('1ch', '1 Chronicles'), ('2ch', '2 Chronicles'), ('ezr', 'Ezra'), ('neh', 'Nehemiah'), ('est', 'Esther'), ('job', 'Job'), ('psa', 'Psalms'), ('pro', 'Proverbs'), ('ecc', 'Ecclesiastes'), ('sng', 'Song of Solomon'), ('isa', 'Isaiah'), ('jer', 'Jeremiah'), ('lam', 'Lamentations'), ('ezk', 'Ezekiel'), ('dan', 'Daniel'), ('hos', 'Hosea'), ('jol', 'Joel'), ('amo', 'Amos'), ('oba', 'Obadiah'), ('jon', 'Jonah'), ('mic', 'Micah'), ('nam', 'Nahum'), ('hab', 'Habakkuk'), ('zep', 'Zephaniah'), ('hag', 'Haggai'), ('zec', 'Zechariah'), ('mal', 'Malachi'), ('mat', 'Matthew'), ('mrk', 'Mark'), ('luk', 'Luke'), ('jhn', 'John'), ('act', 'Acts'), ('rom', 'Romans'), ('1co', '1 Corinthians'), ('2co', '2 Corinthians'), ('gal', 'Galatians'), ('eph', 'Ephesians'), ('php', 'Philippians'), ('col', 'Colossians'), ('1th', '1 Thessalonians'), ('2th', '2 Thessalonians'), ('1ti', '1 Timothy'), ('2ti', '2 Timothy'), ('tit', 'Titus'), ('phm', 'Philemon'), ('heb', 'Hebrews'), ('jas', 'James'), ('1pe', '1 Peter'), ('2pe', '2 Peter'), ('1jn', '1 John'), ('2jn', '2 John'), ('3jn', '3 John'), ('jud', 'Jude'), ('rev', 'Revelation')]
    """
    lang0_book_codes = book_codes_for_lang(lang0_code)
    lang1_book_codes = book_codes_for_lang(lang1_code)
    # Find intersection of book codes:
    return [
        (x, y) for x, y in lang0_book_codes if x in [s for s, t in lang1_book_codes]
    ]


def get_last_segment(url: str, lang_code: str) -> str:
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split("/")
    last_segment = path_segments[-1]
    # Handle special cases where git repo URL was improperly named.
    # Ideally these repos URLs would have their last segment renamed
    # properly, e.g.,
    # 'https://content.bibletranslationtools.org/faustin_azaza/faustin_azaza'
    # renamed to
    # 'https://content.bibletranslationtools.org/faustin_azaza/zmq_mrk_text_reg',
    # but since we don't have control over that, we handle these anomalies
    # here.
    if lang_code == "zmq" and last_segment == "faustin_azaza":
        last_segment = "zmq_mrk_text_reg"
    elif lang_code == "my" and last_segment == "my_juds":
        last_segment = "my_ulb"
    elif lang_code == "fa" and last_segment == "fa_opv":
        last_segment = "fa_ulb"
    return last_segment


def update_repo_components(repo_components: list[str]) -> list[str]:
    last_component = repo_components[-1]
    # Some DCS-Mirror URLs have an unusual pattern wherein a non resource type is the last component
    # url: https://content.bibletranslationtools.org/DCS-Mirror/danjuma_alfred_h_kgo_phm_text_ulb_l1,
    # repo_components: ['danjuma', 'alfred', 'h', 'kgo', 'phm', 'text', 'ulb', 'l1']
    if (
        last_component not in settings.USFM_RESOURCE_TYPES
        and last_component not in settings.NON_USFM_RESOURCE_TYPES
        and last_component not in RESOURCE_TYPE_CODES_AND_NAMES
    ):
        repo_components = repo_components[0:-1]
    match len(repo_components):
        case 7:
            repo_components = repo_components[3:]
        case 6:
            repo_components = repo_components[2:]
        case 5:
            repo_components = repo_components[1:]
        case 3:
            # Handle en_tn_condensed last segment of URL case
            if repo_components[0] == "en" and repo_components[1] == "condensed":
                repo_components = ["en", "tn_condensed"]
    return repo_components


def add_data_not_supplied_by_data_api(repos_info: Any) -> Any:
    """
    DOC needs to support en/tn_condensed, id/ayt, id/tq, and id/tw none of which are supplied by the data API so we augment the data returned from the data API to include them here.
    """
    # The data API only provides id_tn repo for id, we have to
    # add the other repos for id that are available for DOC's use.
    id_ayt = {
        "repo_url": "https://content.bibletranslationtools.org/WA-Catalog/id_ayt",
        "content": {
            "resource_type": "ayt",
            "language": {
                "english_name": "Indonesian",
                "ietf_code": "id",
                "national_name": "Bahasa Indonesian",
                "direction": "ltr",
            },
        },
    }
    repos_info.append(id_ayt)
    id_tq = {
        "repo_url": "https://content.bibletranslationtools.org/WA-Catalog/id_tq",
        "content": {
            "resource_type": "tq",
            "language": {
                "english_name": "Indonesian",
                "ietf_code": "id",
                "national_name": "Bahasa Indonesian",
                "direction": "ltr",
            },
        },
    }
    repos_info.append(id_tq)
    id_tw = {
        "repo_url": "https://content.bibletranslationtools.org/WA-Catalog/id_tw",
        "content": {
            "resource_type": "tw",
            "language": {
                "english_name": "Indonesian",
                "ietf_code": "id",
                "national_name": "Bahasa Indonesian",
                "direction": "ltr",
            },
        },
    }
    repos_info.append(id_tw)
    # data API does not provide tn_condensed for en, but DOC needs to support it
    en_tn_condensed = {
        "repo_url": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn_condensed",
        "content": {
            "resource_type": "tn-condensed",
            "language": {
                "english_name": "English",
                "ietf_code": "en",
                "national_name": "English",
                "direction": "ltr",
            },
        },
    }
    repos_info.append(en_tn_condensed)
    # logger.debug("repos_info[-4:]: %s", repos_info[-4:])
    return repos_info


def book_codes_for_lang(
    lang_code: str,
    resource_assets_dir: str = settings.RESOURCE_ASSETS_DIR,
    book_names: Mapping[str, str] = BOOK_NAMES,
    dcs_mirror_git_username: str = "DCS-Mirror",
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
) -> Sequence[tuple[str, str]]:
    """
    >>> from document.domain import resource_lookup
    >>> ();result = resource_lookup.book_codes_for_lang("pt-br");() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    ('gen', 'Genesis')
    """
    data = fetch_source_data()
    book_codes_and_names = []
    book_codes_and_names2: list[tuple[str, str]] = []
    try:
        repos_info = data["git_repo"]
        augmented_repos_info = add_data_not_supplied_by_data_api(repos_info)
        for repo_info in augmented_repos_info:
            content = repo_info["content"]
            language_info = content["language"]
            url = repo_info["repo_url"]
            if language_info["ietf_code"] == lang_code:
                last_segment = get_last_segment(url, lang_code)
                repo_components = last_segment.split("_")
                if dcs_mirror_git_username in url:
                    repo_components = update_repo_components(repo_components)
                logger.debug("url: %s, repo_components: %s", url, repo_components)
                if len(repo_components) > 2:
                    book_code = repo_components[1]
                    if book_code in book_names:
                        book_codes_and_names.append((book_code, book_names[book_code]))
                elif (
                    len(repo_components) == 2 and not book_codes_and_names
                ):  # e.g., amo_reg, id_tn
                    if not book_codes_and_names2:
                        resource_filepath = f"{resource_assets_dir}/{last_segment}"
                        clone_git_repo(url, resource_filepath)
                        # Check repo's layout on disk to determine which books it provides.
                        # First look at USFM assets.
                        if repo_components[-1] in usfm_resource_types:
                            usfm_files = parsing.find_usfm_files(resource_filepath)
                            for usfm_file in usfm_files:
                                book_code = Path(usfm_file).stem.lower().split("-")[1]
                                book_codes_and_names2.append(
                                    (book_code, book_names[book_code])
                                )
                        # If no USFM assets found, look for others
                        if not book_codes_and_names2:
                            # Search for book directories amongst non-USFM repo assets
                            if repo_components[-1] in ["tn", "tq"]:
                                subdirs = [
                                    file
                                    for file in scandir(resource_filepath)
                                    if file.is_dir()
                                    and file.name not in ["front", "00"]
                                    and not file.name.startswith(".")
                                ]
                                logger.debug("subdirs (as book codes): %s", subdirs)
                                for subdir in subdirs:
                                    book_codes_and_names2.append(
                                        (
                                            subdir.name.lower(),
                                            book_names[subdir.name.lower()],
                                        )
                                    )

                        # logger.debug("book_codes_and_names2: %s", book_codes_and_names2)
    except:
        pass
    # Keep book codes unique and sorted by canonical bible book order
    unique_values = []
    seen_values = set()
    book_codes_and_names.extend(book_codes_and_names2)
    for value in book_codes_and_names:
        if value[0] not in seen_values:
            unique_values.append(value)
            seen_values.add(value[0])
    book_id_map = dict((id, pos) for pos, id in enumerate(book_names.keys()))
    book_codes_sorted = sorted(
        unique_values,
        key=lambda book_code_and_name: book_id_map[book_code_and_name[0]],
    )
    return book_codes_sorted


def resource_lookup_dto(
    lang_code: str,
    resource_type: str,
    book_code: str,
    dcs_mirror_git_username: str = "DCS-Mirror",
    zmq_git_username: str = "faustin_azaza",
) -> Optional[ResourceLookupDto]:
    """
    >>> from document.domain import resource_lookup
    >>> ();data = resource_lookup.resource_lookup_dto("pt-br", "ulb", "mat");() # doctest: +ELLIPSIS
    (...)
    >>> data
    ResourceLookupDto(lang_code='pt-br', lang_name='Brazilian Portuguese', resource_type='ulb', resource_type_name='Unlocked Literal Bible', book_code='mat', url='https://content.bibletranslationtools.org/WA-Catalog/pt-br_blv')
    """
    data = fetch_source_data()
    resource_lookup_dto = None
    two_component_url_resource_lookup_dtos = []
    more_than_two_component_url_resource_lookup_dtos = []
    try:
        repos_info = data["git_repo"]
        augmented_repos_info = add_data_not_supplied_by_data_api(repos_info)
        for repo_info in augmented_repos_info:
            content = repo_info["content"]
            language_info = content["language"]
            resource_type_ = content["resource_type"]
            url = repo_info["repo_url"]
            if language_info["ietf_code"] == lang_code:
                last_segment = get_last_segment(url, lang_code)
                repo_components = last_segment.split("_")
                repo_components = update_repo_components(repo_components)
                logger.debug(
                    "url: %s, repo_components: %s, resource_type: %s",
                    url,
                    repo_components,
                    resource_type_,
                )
                if len(repo_components) > 2:
                    book_code_ = repo_components[1]
                    if (
                        (book_code_ in url or zmq_git_username in url)
                        and resource_type == resource_type_
                        and book_code_ == book_code
                    ):
                        resource_lookup_dto = ResourceLookupDto(
                            lang_code=lang_code,
                            lang_name=language_info["english_name"],
                            resource_type=resource_type,
                            resource_type_name=RESOURCE_TYPE_CODES_AND_NAMES[
                                resource_type
                            ],
                            book_code=book_code,
                            lang_direction=language_info["direction"],
                            url=url,
                        )
                        more_than_two_component_url_resource_lookup_dtos.append(
                            resource_lookup_dto
                        )
                elif (
                    len(repo_components) == 2 and resource_type == resource_type_
                ):  # Here we handle cases like es-419_ulb, es-419_tn, en_ulb, etc.
                    resource_lookup_dto = ResourceLookupDto(
                        lang_code=lang_code,
                        lang_name=language_info["english_name"],
                        resource_type=resource_type,
                        resource_type_name=RESOURCE_TYPE_CODES_AND_NAMES[resource_type],
                        book_code=book_code,
                        lang_direction=language_info["direction"],
                        url=url,
                    )
                    two_component_url_resource_lookup_dtos.append(resource_lookup_dto)
    except:
        logger.debug(
            "Problem creating ResourceLookupDto instance for %s, %s, %s, likely a data problem",
            lang_code,
            resource_type,
            book_code,
        )
    logger.debug(
        "two_component_url_resource_lookup_dtos: %s",
        two_component_url_resource_lookup_dtos,
    )
    logger.debug(
        "more_than_two_component_url_resource_lookup_dtos: %s",
        more_than_two_component_url_resource_lookup_dtos,
    )
    if more_than_two_component_url_resource_lookup_dtos:
        resource_lookup_dto = more_than_two_component_url_resource_lookup_dtos[0]
    elif two_component_url_resource_lookup_dtos:
        resource_lookup_dto = two_component_url_resource_lookup_dtos[0]
    logger.debug("resource_lookup_dto: %s", resource_lookup_dto)
    return resource_lookup_dto


def provision_asset_files(resource_lookup_dto: ResourceLookupDto) -> str:
    """
    Prepare the resource directory and then download the
    resource's file assets into that directory. Return resource_dir.
    """
    return acquire_resource_assets(resource_lookup_dto)


def acquire_resource_assets(
    resource_lookup_dto: ResourceLookupDto,
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
) -> str:
    """
    git clone resource asset.
    Return the resource_dir path.
    """
    if (
        resource_lookup_dto.url is not None
    ):  # We know that resource_url is not None because of how we got here, but mypy isn't convinced. Let's convince mypy.
        resource_filepath = join(
            working_dir,
            get_last_segment(resource_lookup_dto.url, resource_lookup_dto.lang_code),
        )
        # TODO There was some issue here which checking the cache and
        # then cloning. Just cloning made it go away. Investigate later. Lower
        # priority.
        # Check if resource assets need updating otherwise use
        # what we already have on disk.
        # if file_needs_update(resource_filepath):
        clone_git_repo(resource_lookup_dto.url, resource_filepath)
        # else:
        #     logger.debug("Cache hit for %s", resource_filepath)
    return resource_filepath


def clone_git_repo(
    url: str,
    resource_filepath: str,
    branch: Optional[str] = None,
) -> None:
    """
    Clone the git repo. If the repo was previously cloned but
    the ASSET_CACHING_PERIOD has expired then delete the repo and
    clone it again to get updates.
    """
    if branch:  # CLient specified a particular branch
        command = "git clone --depth=1 --branch '{}' '{}' '{}'".format(
            branch, url, resource_filepath
        )
    else:
        command = "git clone --depth=1 '{}' '{}'".format(url, resource_filepath)
    # TODO There were some issues with the commented out code below. It exists for the case where
    # we'd want to reclone a repo when it is sufficiently stale, just
    # in case it was updated by translators.
    # if dir_needs_update(resource_filepath):
    #     logger.debug(
    #         "About to delete pre-existing git repo %s in order to recreate it due to cache staleness.",
    #         resource_filepath,
    #     )
    if isdir(resource_filepath):
        logger.info("No need to clone repo as it already exists.")
        # try:
        #     shutil.rmtree(resource_filepath)
        # except OSError:
        #     logger.debug(
        #         "Directory %s was not removed due to an error.",
        #         resource_filepath,
        #     )
        #     logger.exception("Caught exception: ")

        # logger.debug("Attempting to clone into %s ...", resource_filepath)
        # try:
        #     subprocess.call(command, shell=True)
        # except subprocess.SubprocessError:
        #     logger.debug("git command: %s", command)
        #     logger.debug("git clone failed!")
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="git clone failed",
        #     )
        # else:
        #     logger.debug("git command: %s", command)
        #     logger.debug("git clone succeeded.")
    else:
        logger.debug("Attempting to clone into %s ...", resource_filepath)
        try:
            subprocess.call(command, shell=True)
            logger.debug("git command: %s", command)
            logger.debug("git clone succeeded.")
        except subprocess.SubprocessError:
            logger.debug("git command: %s", command)
            logger.debug("git clone failed!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="git clone failed",
            )


if __name__ == "__main__":

    # To run the doctests in the this module, in the root of the project do:
    # python backend/document/domain/resource_lookup.py
    # or
    # python backend/document/domain/resource_lookup.py -v
    # See https://docs.python.org/3/library/doctest.html
    # for more details.
    import doctest

    doctest.testmod()
