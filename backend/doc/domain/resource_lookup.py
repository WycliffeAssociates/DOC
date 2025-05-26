"""
This module provides an API for looking up the location of a
resource's asset files in the cloud and acquiring said resource
assets.
"""

from datetime import datetime, timedelta
import json
import re
import shutil
import subprocess
from glob import glob
from os import scandir, stat
from os.path import basename, exists, isdir, join
from pathlib import Path
from typing import Mapping, Optional, Sequence
from urllib.parse import urlparse

import requests
import yaml
from doc.config import settings
from doc.domain import parsing, worker
from doc.domain.bible_books import BOOK_CHAPTERS, BOOK_NAMES
from doc.domain.model import (
    NON_USFM_RESOURCE_TYPES,
    Content,
    Data,
    JsonManifestBook,
    JsonManifestData,
    LangDirEnum,
    Language,
    RepoEntry,
    ResourceLookupDto,
    SourceData,
)
from doc.reviewers_guide.model import BibleReference
from doc.reviewers_guide.parser import (
    find_bible_references,
    get_rg_books,
    parse_bible_reference,
)
from doc.utils.file_utils import file_needs_update, make_dir, read_file
from doc.utils.list_utils import unique_tuples
from doc.utils.text_utils import normalize_localized_book_name
from fastapi import HTTPException, status
from pydantic import HttpUrl

logger = settings.logger(__name__)

SOURCE_DATA_JSON_FILENAME = "resources.json"

SOURCE_GATEWAY_LANGUAGES_FILENAME = "gateway_languages.json"

# This can be expanded to include any additional types (if
# there are any) that we want to be available to users. These are all
# that I found of relevance in the data API.
RESOURCE_TYPE_CODES_AND_NAMES: Mapping[str, str] = {
    "ayt": "Bahasa Indonesian Bible",
    "bc": "Bible Commentary",
    "blv": "Portuguese Bíblia Livre",
    "cuv": "新标点和合本",
    "f10": "French Louis Segond 1910 Bible",
    "nav": "New Arabic Version (Ketab El Hayat)",
    "reg": "Regular",
    "rg": "NT Survey Reviewer's Guide",
    "tn": "Translation Notes",
    "tn-condensed": "Condensed Translation Notes",
    "tq": "Translation Questions",
    "tw": "Translation Words",
    # "udb": "Unlocked Dynamic Bible",  # Content team doesn't want udb used
    "ugnt": "unfoldingWord® Greek New Testament",
    "uhb": "unfoldingWord® Hebrew Bible",
    "ulb": "Unlocked Literal Bible",
}

# NOTE This is only used to see if a lang_code is in the collection
# otherwise it is a heart language. Eventually the graphql data api may
# provide gateway/heart boolean value.
GATEWAY_LANGUAGES: Sequence[str] = [
    "abs",
    "aju",
    "am",
    "apd",
    "ar",
    "ar-x-dcv",
    "ary",
    "arz",
    "as",
    "ase",
    "bem",
    "bg",
    "bgw",
    "bi",
    "bn",
    "ceb",
    "cmn",
    "cmn-x-omc",
    "csl",
    "dz",
    "en",
    "es",
    "es-419",
    "fa",
    "fil",
    "fr",
    "grt",
    "gu",
    "gug",
    "ha",
    "hbs",
    "hca",
    "he",
    "hi",
    "hne",
    "hu",
    "id",
    "id-x-dcv",
    "idb",
    "ilo",
    "ins",
    "ja",
    "jv",
    "kas",
    "km",
    "kn",
    "lbj",
    "ln",
    "lo",
    "mai",
    "mg",
    "ml",
    "mn",
    "mni",
    "mnk",
    "mr",
    "ms",
    "my",
    "ne",
    "nl",
    "npi",
    "or",
    "pa",
    "pbt",
    "pes",
    "pis",
    "plt",
    "pmy",
    "pnb",
    "prs",
    "ps",
    "psr",
    "pt",
    "pt-br",
    "raj",
    "rsl",
    "ru",
    "rwr",
    "sn",
    "sw",
    "swc",
    "swh",
    "ta",
    "te",
    "th",
    "ti",
    "tl",
    "tn",
    "tpi",
    "tr",
    "tsg",
    "ug",
    "ur",
    "vi",
    "zh",
    "zlm",
]

# The book name in the tuple key is what
# resource_lookup.get_book_codes_for_lang is returning for lang_code in
# the tuple key and the associated value is what we would prefer to
# use.
BOOK_NAME_CORRECTION_TABLE: dict[tuple[str, str], str] = {
    ("pt-br", "1 Corintios"): "1 Coríntios",
    ("es-419", "I juan"): "1 Juan",
}

# List of languages which do not have USFM available for any books. We use this
# to filter these out of STET's list of source and target
# languages so that the user doesn't have the frustrating experience of
# selecting a language which might have non-USFM resources available but
# not USFM so that when their resulting doc is generated no scripture is
# present. It makes it seem like a bug in STET and is bad UX.
LANG_CODES_WITH_NO_USFM: list[str] = ["ru"]


def fetch_source_data(
    data_api_url: HttpUrl = settings.DATA_API_URL,
) -> Optional[SourceData]:
    """
    Downloads data from a GraphQL API.

    >>> from doc.domain import resource_lookup
    >>> ();result = resource_lookup.fetch_source_data();() # doctest: +ELLIPSIS
    (...)
    >>> result.git_repo[0]
    {'repo_url': 'https://content.bibletranslationtools.org/bahasatech.indotengah/adn_1jn_text_reg', 'content': {'resource_type': 'reg', 'language': {'english_name': 'Adang', 'ietf_code': 'adn', 'national_name': 'Adang', 'direction': 'ltr'}}}
    """
    graphql_query = """
query MyQuery {
  git_repo(
    where: {content: {wa_content_metadata: {status: {_eq: "Primary"}}}}
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
    query_json = {"query": graphql_query}
    try:
        response = requests.post(str(data_api_url), json=query_json)
        if response.status_code == 200:
            data_payload = response.json().get("data", {})
            if "git_repo" in data_payload:
                return SourceData.model_validate(data_payload)
            else:
                logger.info("Invalid payload structure, no data.")
                return SourceData(git_repo=[])
        else:
            logger.info(
                "Failed to get data from data API, graphql API might be down..."
            )
            return SourceData(git_repo=[])
    except requests.RequestException as e:
        logger.exception("Request failed: %s", e)
        logger.info("Failed to get data from data API, API might be down...")
        return SourceData(git_repo=[])


def lang_codes_and_names(
    # lang_code_filter_list: Sequence[str] = settings.LANG_CODE_FILTER_LIST,
    gateway_languages: Sequence[str] = GATEWAY_LANGUAGES,
) -> Sequence[tuple[str, str, bool]]:
    """
    >>> from doc.domain import resource_lookup
    >>> ();result = resource_lookup.lang_codes_and_names();() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    ('abz', 'Abui', False)
    >>> heart_lang_codes = [lang_code_and_name[0] for lang_code_and_name in resource_lookup.lang_codes_and_names() if not lang_code_and_name[2]]
    >>> for heart_lang_code in heart_lang_codes:
    ...     resource_lookup.book_codes_for_lang(heart_lang_code)
    ...
    """
    data = fetch_source_data()
    values = []
    if data is None or not data.git_repo:
        logger.info("Data API is down or no git_repo found!")
        return []
    try:
        # if ietf_code not in lang_code_filter_list:
        for repo_info in data.git_repo:
            language_info = repo_info.content
            language = language_info.language
            ietf_code = language.ietf_code
            english_name = language.english_name if language.english_name else ""
            localized_name = language.national_name
            is_gateway = ietf_code in gateway_languages
            if english_name in localized_name:
                values.append((ietf_code, localized_name, is_gateway))
            else:
                values.append(
                    (ietf_code, f"{localized_name} ({english_name})", is_gateway)
                )
    except Exception:
        logger.exception("Failed due to the following exception.")
    unique_values = unique_tuples(values)
    return sorted(unique_values, key=lambda value: value[1])


def lang_codes_and_names_having_usfm(
    lang_code_filter_list: Sequence[str] = LANG_CODES_WITH_NO_USFM,
    gateway_languages: Sequence[str] = GATEWAY_LANGUAGES,
) -> Sequence[tuple[str, str, bool]]:
    """
    >>> from doc.domain import resource_lookup
    >>> ();result = resource_lookup.lang_codes_and_names_having_usfm();() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    ('abz', 'Abui', False)
    >>> heart_lang_codes = [lang_code_and_name[0] for lang_code_and_name in resource_lookup.lang_codes_and_names_having_usfm() if not lang_code_and_name[2]]
    >>> for heart_lang_code in heart_lang_codes:
    ...     resource_lookup.book_codes_for_lang(heart_lang_code)
    ...
    """
    data = fetch_source_data()
    values = []
    if data is None or not data.git_repo:
        logger.info("Data API is down or no git_repo found!")
        return []
    try:
        for repo_info in data.git_repo:
            language_info = repo_info.content
            language = language_info.language
            ietf_code = language.ietf_code
            english_name = language.english_name if language.english_name else ""
            localized_name = language.national_name
            is_gateway = ietf_code in gateway_languages
            if ietf_code not in lang_code_filter_list:
                if english_name in localized_name:
                    values.append((ietf_code, localized_name, is_gateway))
                else:
                    values.append(
                        (ietf_code, f"{localized_name} ({english_name})", is_gateway)
                    )
    except Exception:
        logger.exception("Failed due to the following exception.")
    unique_values = unique_tuples(values)
    return sorted(unique_values, key=lambda value: value[1])


@worker.app.task
def resource_types(
    lang_code: str,
    book_codes_str: str,
    resource_assets_dir: str = settings.RESOURCE_ASSETS_DIR,
    bc_book_asset_pattern: str = r"^\d{2,}-[0-9a-z]{3}$",
    resource_type_codes_and_names: Mapping[str, str] = RESOURCE_TYPE_CODES_AND_NAMES,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    book_names: Mapping[str, str] = BOOK_NAMES,
    docx_file_path: str = "en_rg_nt_survey.docx",
) -> Sequence[tuple[str, str]]:
    """
    >>> from doc.domain import resource_lookup
    >>> lang_code = "pt-br"
    >>> books = resource_lookup.book_codes_for_lang(lang_code)
    >>> ();result = resource_lookup.resource_types(lang_code, "".join([book[0] for book in books]));() # doctest: +ELLIPSIS
    (...)
    >>> result
    [('blv', 'Portuguese Bíblia Livre'), ('tw', 'Translation Words'), ('ulb', 'Unlocked Literal Bible')]
    Fetches and processes available resource types for the given language and book codes.
    """
    book_codes = book_codes_str.split(",")
    if book_codes and book_codes[0] == "all":
        book_codes = list(book_names.keys())
    data = fetch_source_data()
    resource_types = []
    repo_clone_list: list[tuple[HttpUrl, str]] = []
    resource_type: str | None
    if data is None or not data.git_repo:
        logger.info("Data API is down or no git_repo found!")
        return []
    try:
        repos_info = data.git_repo
        augmented_repos_info = add_data_not_supplied_by_data_api(repos_info)
        for repo_info in augmented_repos_info:
            content = repo_info.content
            language_info = content.language
            if language_info.ietf_code == lang_code:
                resource_type = content.resource_type
                if resource_type in resource_type_codes_and_names:
                    url = repo_info.repo_url
                    last_segment = get_last_segment(url, lang_code)
                    resource_filepath = f"{resource_assets_dir}/{last_segment}"
                    # Append to repo_clone_list if the URL is not already present
                    if not any(item[0] == url for item in repo_clone_list):
                        repo_clone_list.append((url, resource_filepath))
        # Separate repos that need to be cloned from en_rg
        repos_to_clone = [
            (url, path) for url, path in repo_clone_list if "en_rg" not in path
        ]
        # Perform batch cloning only on filtered list
        batch_clone_git_repos(repos_to_clone)
        # Process cloned repositories
        for url, resource_filepath in repo_clone_list:
            resource_type = next(
                (
                    repo_info.content.resource_type
                    for repo_info in data.git_repo
                    if repo_info.repo_url == url
                ),
                None,
            )
            if not resource_type:
                continue
            # Determine book assets
            book_assets = []
            if resource_type in ["tq", "tn", "tn-condensed"]:
                book_assets = [
                    file.name
                    for file in scandir(resource_filepath)
                    if file.is_dir()
                    and not file.name.startswith(".")
                    and file.name.lower() in book_codes
                ]
            elif resource_type == "bc":
                book_assets = [
                    file.name
                    for file in scandir(resource_filepath)
                    if file.is_dir()
                    and not file.name.startswith(".")
                    and re.search(bc_book_asset_pattern, file.name)
                    and file.name.split("-")[1].lower() in book_codes
                ]
            elif resource_type in usfm_resource_types:
                book_assets = parsing.find_usfm_files(resource_filepath)
            elif resource_type == "rg":
                between_texts, bible_reference_strs = find_bible_references(
                    f"{resource_filepath}/{docx_file_path}"
                )
                bible_references = [
                    parse_bible_reference(bible_reference)
                    for bible_reference in bible_reference_strs
                ]
                book_codes_ = {
                    bible_reference.book_code
                    for bible_reference in bible_references
                    if bible_reference
                }
                book_assets = [
                    book_code for book_code in book_codes if book_code in book_codes_
                ]
            # Check if at least one selected book exists in the repo
            if book_assets or resource_type == "tw":
                resource_types.append(
                    (
                        resource_type,
                        resource_type_codes_and_names[resource_type],
                    )
                )
    except Exception:
        logger.exception("Failed due to the following exception.")
    unique_values = unique_tuples(resource_types)
    return sorted(unique_values, key=lambda value: value[1])


def batch_clone_git_repos(
    repos: list[tuple[HttpUrl, str]],
    asset_caching_enabled: bool = settings.ASSET_CACHING_ENABLED,
    asset_caching_period: int = settings.ASSET_CACHING_PERIOD,
) -> None:
    """
    Clones multiple git repositories in a single batch operation.
    - If a repository already exists and is fully cloned, it is skipped.
    - If a repository exists but is a partial clone (corrupt or missing key files), it is removed first.
    - The 'en_rg' directory is preserved and never deleted or cloned.
    - If asset_caching_enabled is False, repositories are always deleted and re-cloned (except 'en_rg').
    """
    clone_commands = []
    for url, resource_filepath in repos:
        if isdir(resource_filepath):
            if basename(resource_filepath) == "en_rg":
                logger.info(f"Preserving special directory: {resource_filepath}")
                continue
            git_dir = join(resource_filepath, ".git")
            if asset_caching_enabled:
                if isdir(git_dir):
                    try:
                        stat_ = stat(git_dir)
                        mod_time = datetime.fromtimestamp(stat_.st_mtime)
                        expiry = timedelta(minutes=asset_caching_period)
                        if (
                            all(
                                exists(join(git_dir, filename))
                                for filename in ["config", "HEAD", "objects"]
                            )
                            and datetime.now() - mod_time <= expiry
                            and any(scandir(resource_filepath))
                        ):
                            logger.info(
                                f"Skipping clone: {resource_filepath} already exists and is a full repo."
                            )
                            continue  # ✅ Fully cloned, reuse
                    except FileNotFoundError:
                        logger.warning(f"Git directory not found: {git_dir}")
                logger.info(
                    f"Removing stale, incomplete, or corrupt repository: {resource_filepath}"
                )
            else:
                logger.info(
                    f"Asset caching disabled: forcibly removing {resource_filepath}"
                )
            shutil.rmtree(resource_filepath)
        clone_command = f"git clone --depth=1 '{url}' '{resource_filepath}' || true"
        clone_commands.append(clone_command)
    if clone_commands:
        full_command = " && ".join(clone_commands)
        try:
            subprocess.call(full_command, shell=True)
        except subprocess.SubprocessError:
            logger.error("Batch git clone failed!")


# Used by some tests
def usfm_resource_types_and_book_tuples(
    lang_code: str,
    book_codes_str: str,
    resource_assets_dir: str = settings.RESOURCE_ASSETS_DIR,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
) -> Sequence[tuple[str, str]]:
    """
    >>> from doc.domain import resource_lookup
    >>> lang_code = "ruc"
    >>> ();books = resource_lookup.book_codes_for_lang(lang_code);() # doctest: +ELLIPSIS
    (...)
    >>> ();tuples = resource_lookup.usfm_resource_types_and_book_tuples(lang_code, ",".join([book[0] for book in books]));() # doctest: +ELLIPSIS
    (...)
    >>> sorted(tuples, key=lambda value: value[1])
    [('reg', '1co'), ('reg', '1jn'), ('reg', '1pe'), ('reg', '1th'), ('reg', '1ti'), ('reg', '2co'), ('reg', '2jn'), ('reg', '2pe'), ('reg', '2th'), ('reg', '2ti'), ('reg', '3jn'), ('reg', 'act'), ('reg', 'col'), ('reg', 'eph'), ('reg', 'gal'), ('reg', 'heb'), ('reg', 'jas'), ('reg', 'jhn'), ('reg', 'jud'), ('reg', 'luk'), ('reg', 'mat'), ('reg', 'mrk'), ('reg', 'phm'), ('reg', 'php'), ('reg', 'rev'), ('reg', 'rom'), ('reg', 'tit')]
    """
    book_codes = book_codes_str.split(",")
    data: SourceData | None = fetch_source_data()
    resource_type_and_book_tuples = set()
    if data is None:
        return []
    repos_info = data.git_repo
    augmented_repos_info = add_data_not_supplied_by_data_api(repos_info)
    for repo_info in augmented_repos_info:
        content = repo_info.content
        language_info = content.language
        if language_info.ietf_code == lang_code:
            resource_type = content.resource_type
            if resource_type in usfm_resource_types:
                url = repo_info.repo_url
                for book_code in book_codes:
                    dto = ResourceLookupDto(
                        lang_code=lang_code,
                        lang_name=language_info.english_name,
                        localized_lang_name=language_info.national_name,
                        resource_type=resource_type,
                        resource_type_name="",
                        url=url,
                        lang_direction=LangDirEnum(language_info.direction),
                        book_code=book_code,
                    )
                    resource_filepath = prepare_resource_filepath(dto)
                    if file_needs_update(resource_filepath):
                        provision_asset_files(dto.url, resource_filepath)
                    content_file = parsing.usfm_asset_file(
                        dto, resource_filepath, False
                    )
                    if content_file:
                        resource_type_and_book_tuples.add((resource_type, book_code))
    return sorted(resource_type_and_book_tuples, key=lambda value: value[0])


def shared_book_codes(lang0_code: str, lang1_code: str) -> Sequence[tuple[str, str]]:
    """
    Given two language codes, return the intersection of resource
    codes between the two languages.

    >>> from doc.domain import resource_lookup
    >>> # Hack to ignore logging output: https://stackoverflow.com/a/33400983/3034580
    >>> ();data = resource_lookup.shared_book_codes("pt-br", "es-419");() # doctest: +ELLIPSIS
    (...)
    >>> list(data)
    [('gen', 'Gênesis'), ('exo', 'Êxodo'), ('lev', 'Levíticos'), ('num', 'Números'), ('deu', 'Deuteronômio'), ('jos', 'Josué'), ('jdg', 'Juízes'), ('rut', 'Rute'), ('1sa', '1 Samuel'), ('2sa', '2 Samuel'), ('1ki', '1 Reis'), ('2ki', '2 Reis'), ('1ch', '1 Crônicas'), ('2ch', '2 Crônicas'), ('ezr', 'Esdras'), ('neh', 'Neemias'), ('est', 'Ester'), ('job', 'Jó'), ('psa', 'Salmos'), ('pro', 'Provérbios'), ('ecc', 'Eclesiastes'), ('sng', 'Cantares de salomão'), ('isa', 'Isaías'), ('jer', 'Jeremias'), ('lam', 'Lamentações'), ('ezk', 'Ezequiel'), ('dan', 'Daniel'), ('hos', 'Oseias'), ('jol', 'Joel'), ('amo', 'Amós'), ('oba', 'Obadias'), ('jon', 'Jonas'), ('mic', 'Miqueias'), ('nam', 'Naum'), ('hab', 'Habacuque'), ('zep', 'Sofonias'), ('hag', 'Ageu'), ('zec', 'Zacarias'), ('mal', 'Malaquias'), ('mat', 'Mateus'), ('mrk', 'Marcos'), ('luk', 'Lucas'), ('jhn', 'João'), ('act', 'Atos'), ('rom', 'Romanos'), ('1co', '1 Coríntios'), ('2co', '2 Coríntios'), ('gal', 'Gálatas'), ('eph', 'Efésios'), ('php', 'Filipenses'), ('col', 'Colossenses'), ('1th', '1 Tessalonicenses'), ('2th', '2 Tessalonicenses'), ('1ti', '1 Timóteo'), ('2ti', '2 Timóteo'), ('tit', 'Tito'), ('phm', 'Filemom'), ('heb', 'Hebreus'), ('jas', 'Tiago'), ('1pe', '1 Pedro'), ('2pe', '2 Pedro'), ('1jn', '1 João'), ('2jn', '2 João'), ('3jn', '3 João'), ('jud', 'Judas'), ('rev', 'Apocalipse')]

    """
    lang0_book_codes = book_codes_for_lang(lang0_code)
    lang1_book_codes = book_codes_for_lang(lang1_code)
    # Find intersection of book codes:
    return [
        (x, y) for x, y in lang0_book_codes if x in [s for s, t in lang1_book_codes]
    ]


def get_last_segment(url: HttpUrl, lang_code: str) -> str:
    """
    Extract the last segment of the URL path and normalize it
    according to known anomalies and naming patterns.
    """
    parsed_url = urlparse(str(url))
    path_segments = parsed_url.path.strip("/").split("/")
    last_segment = path_segments[-1] if path_segments else ""
    return normalize_last_segment(lang_code, last_segment)


# Specific replacements: lang code, last_segment -> replacement last_segment
REPLACEMENTS_BY_LANG_CODE_AND_LAST_SEGMENT = {
    ("fa", "fa_opv"): "fa_ulb",
    ("my", "my_juds"): "my_ulb",
    ("zmq", "faustin_azaza"): "zmq_mrk_text_reg",
}

# Prefixes to remove regardless of lang code
PREFIXES_TO_REMOVE = [
    "Dawit-Dessie_",
    "Jordan_",
    "Lawadinusah_",
    "alexandre_brazil_",
    "azz_athan_",
    "bayan_",
    "billburns58_",
    "botsw01_",
    "burje_duro_",
    "danjuma_alfred_h_",
    "dijim1_",
    "ezekieldabere_",
    "faustin-azaza_",
    "gravy_",
    "jathapu_",
    "jdwood_",
    "jks222111_",
    "jonathan_",
    "krispy_",
    "lawadinusah_",
    "lversaw_",
    "michael_",
    "mitikiwostky_",
    "moufida_",
    "mushohe-25nb_63.kum_",
    "mvccbtt_",
    "nbtt_",
    "ngamo1_",
    "ngamo_",
    "oratab01_",
    "otlaadisa_",
    "parfait-ayanou_",
    "romantts2_",
    "sambadanum_",
    "shyarpa_",
    "tersitzewde_",
    "timothydanjuma_",
    "tom-88pn_0003.machinga_",
    "translator09_",
    "ukum1_",
    "vere3_",
    "yukuben1_",
]

# lang code -> prefixes to remove
LANG_SPECIFIC_PREFIXES_TO_REMOVE = {
    "iba-x-ketungau": ["dayakketungau_"],
    "knx-x-bajanya": ["bajanya_knx"],
    "ndh": ["chindali_"],
    "scg-x-dayakkatarak": ["yustius_"],
    "sdm-x-pangkalsuka": ["dayaksuka_"],
    "xdy-x-dayakpunti": ["anselmus_"],
    "xdy-x-mentebah": ["dayakfdkj_"],
    "xdy-x-senduruhan": ["dayaksenduruhan_"],
}


def normalize_last_segment(
    lang_code: str,
    last_segment: str,
    hardcoded_replacements: dict[
        tuple[str, str], str
    ] = REPLACEMENTS_BY_LANG_CODE_AND_LAST_SEGMENT,
    universal_prefixes: list[str] = PREFIXES_TO_REMOVE,
    lang_specific_prefixes: dict[str, list[str]] = LANG_SPECIFIC_PREFIXES_TO_REMOVE,
) -> str:
    """
    Handle special cases where git repo URL does not follow the expected pattern.
    Ideally these repos URLs would have their last segment renamed
    properly, e.g.,
    'https://content.bibletranslationtools.org/faustin_azaza/faustin_azaza'
    renamed to
    'https://content.bibletranslationtools.org/faustin_azaza/zmq_mrk_text_reg',
    but since we don't have control over that, we handle these anomalies
    here.
    """
    if lang_code == "en" and last_segment.endswith(".docx"):
        return "en_rg"
    if (lang_code, last_segment) in hardcoded_replacements:
        return hardcoded_replacements[(lang_code, last_segment)]
    for prefix in universal_prefixes:
        if last_segment.startswith(prefix):
            return re.sub(f"^{re.escape(prefix)}", "", last_segment)
    for lang, prefixes in lang_specific_prefixes.items():
        if lang_code == lang:
            for prefix in prefixes:
                if last_segment.startswith(prefix):
                    return re.sub(f"^{re.escape(prefix)}", "", last_segment)
    return last_segment


def update_repo_components(
    repo_components: list[str],
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    non_usfm_resource_types: Sequence[str] = NON_USFM_RESOURCE_TYPES,
    resource_type_codes_and_names: Mapping[str, str] = RESOURCE_TYPE_CODES_AND_NAMES,
) -> list[str]:
    last_component = repo_components[-1]
    # Some DCS-Mirror URLs have an unusual pattern wherein a non resource type is the last component
    # in the URL, e.g., https://content.bibletranslationtools.org/DCS-Mirror/danjuma_alfred_h_kgo_phm_text_ulb_l1,
    # repo_components: ['danjuma', 'alfred', 'h', 'kgo', 'phm', 'text', 'ulb', 'l1']
    if (
        last_component not in usfm_resource_types
        and last_component not in non_usfm_resource_types
        and last_component not in resource_type_codes_and_names
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


def add_data_not_supplied_by_data_api(repos_info: list[RepoEntry]) -> list[RepoEntry]:
    """
    DOC needs to support some resources which are not supplied by the
    data API so we augment the data returned from the data API to include
    them here.
    """

    def make_entry(url: HttpUrl, resource_type: str, lang: Language) -> RepoEntry:
        return RepoEntry(
            repo_url=url, content=Content(resource_type=resource_type, language=lang)
        )

    id_lang = Language(
        english_name="Indonesian",
        ietf_code="id",
        national_name="Bahasa Indonesian",
        direction=LangDirEnum.LTR,
    )
    en_lang = Language(
        english_name="English",
        ietf_code="en",
        national_name="English",
        direction=LangDirEnum.LTR,
    )
    extra_entries = [
        make_entry(
            HttpUrl("https://content.bibletranslationtools.org/WA-Catalog/id_ayt"),
            "ayt",
            id_lang,
        ),
        make_entry(
            HttpUrl("https://content.bibletranslationtools.org/WA-Catalog/id_tq"),
            "tq",
            id_lang,
        ),
        make_entry(
            HttpUrl("https://content.bibletranslationtools.org/WA-Catalog/id_tw"),
            "tw",
            id_lang,
        ),
        make_entry(
            HttpUrl(
                "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn_condensed"
            ),
            "tn-condensed",
            en_lang,
        ),
        make_entry(
            HttpUrl(
                "https://github.com/WycliffeAssociates/TS-biel-files/blob/master/training/en/Refinement%20and%20Publication/Reviewers'%20Guide/NT%20Survey%20RG%20Files/NT%20Survey%20Reviewers'%20Guide.docx"
            ),
            "rg",
            en_lang,
        ),
    ]
    repos_info.extend(extra_entries)
    return repos_info


def maybe_correct_book_name(
    lang_code: str,
    book_name: str,
    book_name_correction_table: dict[tuple[str, str], str] = BOOK_NAME_CORRECTION_TABLE,
) -> str:
    """
    Translate incorrect or undesirable book names to a preferred form.
    """
    book_name_ = BOOK_NAME_CORRECTION_TABLE.get((lang_code, book_name), "")
    if not book_name_:
        book_name_ = book_name
    return book_name_


def get_book_codes_for_lang(
    lang_code: str,
    resource_assets_dir: str,
    book_names: Mapping[str, str],
    dcs_mirror_git_username: str,
    usfm_resource_types: Sequence[str],
    use_localized_book_name: bool,
    usfm_only: bool = False,
    check_usfm: bool = False,
) -> Sequence[tuple[str, str]]:
    data = fetch_source_data()
    if data is None:
        return []
    book_codes_and_names_localized: list[tuple[str, str]] = []
    book_codes_and_names: list[tuple[str, str]] = []
    book_codes_and_names2: list[tuple[str, str]] = []
    repo_clone_list: list[tuple[HttpUrl, str]] = []
    try:
        repos_info = data.git_repo
        augmented_repos_info = add_data_not_supplied_by_data_api(repos_info)
        for repo_info in augmented_repos_info:
            content = repo_info.content
            language_info = content.language
            url = repo_info.repo_url
            if language_info.ietf_code == lang_code:
                last_segment = get_last_segment(url, lang_code)
                repo_components = last_segment.split("_")
                if dcs_mirror_git_username in str(url):
                    repo_components = update_repo_components(repo_components)
                if any(rt in str(url) for rt in usfm_resource_types):
                    resource_filepath = f"{resource_assets_dir}/{last_segment}"
                    if not any(item[0] == url for item in repo_clone_list):
                        repo_clone_list.append((url, resource_filepath))
        repos_to_clone = [
            (url, path) for url, path in repo_clone_list if "en_rg" not in path
        ]
        batch_clone_git_repos(repos_to_clone)
        for url, resource_filepath in repo_clone_list:
            for repo_info in augmented_repos_info:
                if repo_info.repo_url == url:
                    last_segment = get_last_segment(url, lang_code)
                    repo_components = last_segment.split("_")
                    if (
                        len(repo_components) == 2
                        and repo_components[-1] in usfm_resource_types
                    ):
                        book_codes_and_names_localized = []
                        usfm_files = parsing.find_usfm_files(resource_filepath)
                        for usfm_file in usfm_files:
                            usfm_file_components = (
                                Path(usfm_file).stem.lower().split("-")
                            )
                            book_code = usfm_file_components[1]
                            resource_type = repo_components[1]
                            usfm = read_file(usfm_file) if usfm_file else ""
                            frontmatter, _, _ = parsing.split_usfm_by_chapters(
                                lang_code, resource_type, book_code, usfm, check_usfm
                            )
                            localized_book_name = parsing.maybe_localized_book_name(
                                frontmatter
                            )
                            localized_book_name = maybe_correct_book_name(
                                lang_code, localized_book_name
                            )
                            book_codes_and_names_localized.append(
                                (book_code, localized_book_name)
                            )
                        break
                    if (
                        use_localized_book_name
                        and len(repo_components) > 2
                        and repo_components[-1] in usfm_resource_types
                    ):
                        book_name_file = f"{resource_filepath}/front/title.txt"
                        if exists(book_name_file):
                            with open(book_name_file, "r") as fin:
                                book_name = fin.read()
                                localized_book_name_ = normalize_localized_book_name(
                                    book_name
                                )
                                localized_book_name = maybe_correct_book_name(
                                    lang_code, localized_book_name_
                                )
                                book_code = repo_components[1]
                                book_codes_and_names_localized.append(
                                    (
                                        book_code,
                                        localized_book_name,
                                    )
                                )
                    if not usfm_only:
                        if not book_codes_and_names_localized or any(
                            name == "" for _, name in book_codes_and_names_localized
                        ):
                            if len(repo_components) > 2:
                                book_code = repo_components[1]
                                if book_code in book_names:
                                    book_codes_and_names.append(
                                        (book_code, book_names[book_code])
                                    )
                            elif len(repo_components) == 2 and not book_codes_and_names:
                                if not book_codes_and_names2:
                                    if resource_type in usfm_resource_types:
                                        usfm_files = parsing.find_usfm_files(
                                            resource_filepath
                                        )
                                        for usfm_file in usfm_files:
                                            book_code = (
                                                Path(usfm_file)
                                                .stem.lower()
                                                .split("-")[1]
                                            )
                                            book_codes_and_names2.append(
                                                (book_code, book_names[book_code])
                                            )
                                    elif resource_type in ["tn", "tq"]:
                                        subdirs = [
                                            file
                                            for file in scandir(resource_filepath)
                                            if file.is_dir() and file.name in book_names
                                        ]
                                        for subdir in subdirs:
                                            book_codes_and_names2.append(
                                                (
                                                    subdir.name.lower(),
                                                    book_names[subdir.name.lower()],
                                                )
                                            )
    except Exception:
        logger.exception("Error during get_book_codes_for_lang")
    if not book_codes_and_names_localized or any(
        name == "" for _, name in book_codes_and_names_localized
    ):
        book_codes_and_names.extend(book_codes_and_names2)
        unique_values = unique_tuples(book_codes_and_names)
    else:
        unique_values = unique_tuples(book_codes_and_names_localized)
    book_id_map = {id: pos for pos, id in enumerate(book_names.keys())}
    return sorted(
        unique_values, key=lambda book_code_and_name: book_id_map[book_code_and_name[0]]
    )


@worker.app.task
def book_codes_for_lang(
    lang_code: str,
    resource_assets_dir: str = settings.RESOURCE_ASSETS_DIR,
    book_names: Mapping[str, str] = BOOK_NAMES,
    dcs_mirror_git_username: str = "DCS-Mirror",
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    use_localized_book_name: bool = settings.USE_LOCALIZED_BOOK_NAME,
) -> Sequence[tuple[str, str]]:
    """
    >>> from doc.domain import resource_lookup
    >>> ();result = resource_lookup.book_codes_for_lang("pt-br");() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    ('gen', 'Gênesis')
    """
    return get_book_codes_for_lang(
        lang_code,
        resource_assets_dir,
        book_names,
        dcs_mirror_git_username,
        usfm_resource_types,
        use_localized_book_name,
        usfm_only=False,
    )


@worker.app.task
def book_codes_for_lang_from_usfm_only(
    lang_code: str,
    resource_assets_dir: str = settings.RESOURCE_ASSETS_DIR,
    book_names: Mapping[str, str] = BOOK_NAMES,
    dcs_mirror_git_username: str = "DCS-Mirror",
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    use_localized_book_name: bool = settings.USE_LOCALIZED_BOOK_NAME,
) -> Sequence[tuple[str, str]]:
    """
    >>> from doc.domain import resource_lookup
    >>> ();result = resource_lookup.book_codes_for_lang_from_usfm_only("pt-br");() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    ('gen', 'Gênesis')
    """
    return get_book_codes_for_lang(
        lang_code,
        resource_assets_dir,
        book_names,
        dcs_mirror_git_username,
        usfm_resource_types,
        use_localized_book_name,
        usfm_only=True,
    )


def chapters_in_books(
    book_chapters: Mapping[str, int] = BOOK_CHAPTERS
) -> dict[str, list[int]]:
    chapters_in_book: dict[str, list[int]] = {
        book_code: list(range(1, num_of_chapters + 1))
        for book_code, num_of_chapters in book_chapters.items()
    }
    return chapters_in_book


def load_manifest(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


def book_codes_and_names_from_manifest(
    resource_dir: str,
    manifest_glob_fmt_str: str = "{}/**/manifest.{}",
    manifest_glob_alt_fmt_str: str = "{}/manifest.{}",
) -> list[tuple[str, str]]:
    """
    Look up the language direction in the manifest file if one is
    available for this resource.
    """
    # Try to find manifest yaml at typical directory
    manifest_candidates = glob(manifest_glob_fmt_str.format(resource_dir, "yaml"))
    if not manifest_candidates:
        # Now try to find manifest yaml at parent directory of typical directory
        manifest_candidates = glob(
            manifest_glob_alt_fmt_str.format(resource_dir, "yaml")
        )
        if not manifest_candidates:
            # Some languages provide their manifest in json format.
            # Try to find manifest json at typical directory
            manifest_candidates = glob(
                manifest_glob_fmt_str.format(resource_dir, "json")
            )
            if not manifest_candidates:
                # Try to find manifest json at parent directory of typical directory
                manifest_candidates = glob(
                    manifest_glob_alt_fmt_str.format(resource_dir, "json")
                )
    # logger.debug("manifest_candidates: %s", manifest_candidates)
    if manifest_candidates:
        # logger.debug("len(manifest_candidates): %s", len(manifest_candidates))
        candidate = manifest_candidates[0]
        suffix = str(Path(candidate).suffix)
        book_codes_and_names: list[tuple[str, str]] = []
        # Get localized book names
        manifest_data = load_manifest(candidate)
        # logger.debug("manifest_data: %s", manifest_data)
        if suffix == ".yaml":
            data: Data = yaml.safe_load(manifest_data)
            book_codes_and_names = [
                (book["identifier"], book["title"]) for book in data["projects"]
            ]
        # Heart languages often have .json manifest files
        # per book and not per language.
        elif suffix == ".json":
            json_data: JsonManifestData = json.loads(manifest_data)
            logger.debug("json_data: %s", json_data)
            project: JsonManifestBook = json_data["project"]
            book_codes_and_names = [(project["id"], project["name"])]
            # logger.debug("book_codes_and_names from json: %s", book_codes_and_names)
    return book_codes_and_names


def resource_lookup_dto(
    lang_code: str,
    resource_type: str,
    book_code: str,
    dcs_mirror_git_username: str = "DCS-Mirror",
    zmq_git_username: str = "faustin_azaza",
    resource_type_codes_and_names: Mapping[str, str] = RESOURCE_TYPE_CODES_AND_NAMES,
) -> Optional[ResourceLookupDto]:
    """
    >>> from doc.domain import resource_lookup
    >>> ();data = resource_lookup.resource_lookup_dto("pt-br", "ulb", "mat");() # doctest: +ELLIPSIS
    (...)
    >>> data
    ResourceLookupDto(lang_code='pt-br', lang_name='Brazilian Portuguese', resource_type='ulb', resource_type_name='Unlocked Literal Bible', book_code='mat', lang_direction=<LangDirEnum.LTR: 'ltr'>, url=HttpUrl('https://content.bibletranslationtools.org/WA-Catalog/pt-br_ulb'))

    """
    data = fetch_source_data()  # Fetch source data
    if data is None:
        return None
    resource_lookup_dto: Optional[ResourceLookupDto] = None
    rg_resource_lookup_dtos: list[ResourceLookupDto] = []
    two_component_url_resource_lookup_dtos: list[ResourceLookupDto] = []
    more_than_two_component_url_resource_lookup_dtos: list[ResourceLookupDto] = []
    try:
        repos_info = data.git_repo
        augmented_repos_info = add_data_not_supplied_by_data_api(repos_info)
        for repo_info in augmented_repos_info:
            content = repo_info.content
            language_info = content.language
            resource_type_ = content.resource_type
            url = repo_info.repo_url
            if language_info.ietf_code == lang_code:
                last_segment = get_last_segment(url, lang_code)
                if last_segment[-4:] == "docx":
                    resource_lookup_dto = ResourceLookupDto(
                        lang_code=lang_code,
                        lang_name=language_info.english_name,
                        localized_lang_name=language_info.national_name,
                        resource_type=resource_type,
                        resource_type_name=resource_type_codes_and_names[resource_type],
                        book_code=book_code,
                        lang_direction=language_info.direction,
                        url=url,
                    )
                    rg_resource_lookup_dtos.append(resource_lookup_dto)
                else:
                    repo_components = last_segment.split("_")
                    repo_components = update_repo_components(repo_components)
                    if len(repo_components) > 2:
                        book_code_ = repo_components[1]
                        if (
                            (book_code_ in str(url) or zmq_git_username in str(url))
                            and resource_type == resource_type_
                            and resource_type_ in resource_type_codes_and_names
                            and book_code_ == book_code
                        ):
                            resource_lookup_dto = ResourceLookupDto(
                                lang_code=lang_code,
                                lang_name=language_info.english_name,
                                localized_lang_name=language_info.national_name,
                                resource_type=resource_type,
                                resource_type_name=resource_type_codes_and_names[
                                    resource_type
                                ],
                                book_code=book_code,
                                lang_direction=language_info.direction,
                                url=url,
                            )
                            more_than_two_component_url_resource_lookup_dtos.append(
                                resource_lookup_dto
                            )
                    elif len(repo_components) == 2 and resource_type == resource_type_:
                        # Handle cases like es-419_ulb, es-419_tn, en_ulb, etc.
                        resource_lookup_dto = ResourceLookupDto(
                            lang_code=lang_code,
                            lang_name=language_info.english_name,
                            localized_lang_name=language_info.national_name,
                            resource_type=resource_type,
                            resource_type_name=resource_type_codes_and_names[
                                resource_type
                            ],
                            book_code=book_code,
                            lang_direction=language_info.direction,
                            url=url,
                        )
                        two_component_url_resource_lookup_dtos.append(
                            resource_lookup_dto
                        )
    except Exception:
        logger.info(
            "Problem creating ResourceLookupDto instance for %s, %s, %s, likely a data problem",
            lang_code,
            resource_type,
            book_code,
        )
    if rg_resource_lookup_dtos:
        resource_lookup_dto = rg_resource_lookup_dtos[0]
    elif more_than_two_component_url_resource_lookup_dtos:
        resource_lookup_dto = more_than_two_component_url_resource_lookup_dtos[0]
    elif two_component_url_resource_lookup_dtos:
        resource_lookup_dto = two_component_url_resource_lookup_dtos[0]
    return resource_lookup_dto


def provision_asset_files(
    url: Optional[HttpUrl],
    resource_filepath: str,
) -> None:
    if url is not None:
        if str(url)[-4:] != "docx":
            clone_git_repo(url, resource_filepath)
        elif str(url)[-4:] == "docx":
            download_rg_file(url, resource_filepath)


def prepare_resource_filepath(
    resource_lookup_dto: ResourceLookupDto,
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
) -> str:
    resource_filepath = ""
    if (
        resource_lookup_dto.url is not None
    ):  # We know that resource_url is not None because of how we got here, but mypy isn't convinced. Let's convince mypy.
        resource_filepath = join(
            working_dir,
            get_last_segment(resource_lookup_dto.url, resource_lookup_dto.lang_code),
        )
    return resource_filepath


def clone_git_repo(
    url: HttpUrl,
    resource_filepath: str,
    branch: Optional[str] = None,
) -> None:
    if branch:  # CLient specified a particular branch
        command = "git clone --depth=1 --branch '{}' '{}' '{}'".format(
            branch, url, resource_filepath
        )
    else:
        command = "git clone --depth=1 '{}' '{}'".format(url, resource_filepath)
    if not isdir(resource_filepath):
        logger.info("Attempting to clone into %s ...", resource_filepath)
        try:
            subprocess.call(command, shell=True)
            logger.info("git command: %s", command)
            logger.info("git clone succeeded.")
        except subprocess.SubprocessError:
            logger.info("git command: %s", command)
            logger.info("git clone failed!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="git clone failed",
            )


def download_rg_file(
    url: HttpUrl,
    resource_filepath: str,
) -> None:
    # TODO Until data API provides reviewer's guide URL that is
    # downloadable, we provide the reviewer's guide in our build process
    # using directives in our Dockerfile. Downloading the file using curl
    # doesn't work as it is below. There is a way to authenticate to github
    # using curl and download the file, but this requires using an
    # authentication token which would need to be shared via an env var that
    # is not committed to git.
    pass
    # logger.debug("About to download rg file: %s to: %s", url, resource_filepath)
    # make_dir(resource_filepath)
    # command = "curl -L -o '{}/en_rg_nt_survey.docx' '{}'".format(resource_filepath, url)
    # if exists(resource_filepath):
    #     logger.info(
    #         "No need to download file as it already exists: %s", resource_filepath
    #     )
    # else:
    #     logger.debug("Attempting to download file into %s ...", resource_filepath)
    #     try:
    #         subprocess.call(command, shell=True)
    #         logger.debug("curl command: %s", command)
    #         logger.debug("download file succeeded.")
    #     except subprocess.SubprocessError:
    #         logger.debug("curl command: %s", command)
    #         logger.debug("download file failed!")
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail="download file failed",
    #         )


def nt_survey_rg_passages(
    lang_code: str = "en",
    lang_name: str = "English",
    resource_type_name: str = "NT Survey Reviewer's Guide",
    lang_direction: LangDirEnum = LangDirEnum.LTR,
    assets_dir: str = settings.RESOURCE_ASSETS_DIR,
    resource_dir: str = "en_rg",
    docx_file_path: str = "en_rg_nt_survey.docx",
) -> list[BibleReference]:
    """
    >>> from doc.domain import resource_lookup
    >>> rg_books = resource_lookup.nt_survey_rg_passages()
    >>> rg_books[0]
    RGBook(
      lang_code=en,
      lang_name=English,
      book_code=mat,
      resource_type_name=NT Survey Reviewer's Guide,
      chapters={2: RGChapter(content=ParsedText(bible_reference=BibleReference(book_code='mat', book_name='Matthew', chapter=2, verse_ref='1-12'), background='', directive='Read the passage.', part_1=[Part1Item(text='Wise men came from the east to Jerusalem looking for the one who was born king of the Jews.', reference='[2:1-2]'), Part1Item(text='The chief priests and scribes told Herod that the Christ was to be born in Bethlehem according to Scripture.', reference='[2:5-6]'), Part1Item(text='Herod sent the wise men to Bethlehem.', reference='[2:7-8]'), Part1Item(text='Herod ordered the wise men to return, telling them that he also wanted to worship the baby.', reference='[2:8]'), Part1Item(text='The wise men went to Bethlehem, found the baby, gave him gifts, and worshiped him.', reference='[2:11]'), Part1Item(text='They did not return to Herod.', reference='[2:12]')], part_1_directive='Tell in your own words what you just read in this passage.', part_2=[Part2Item(reference='[2:1-2]', question='After Jesus was born in Bethlehem, why did some wise men go to Jerusalem?', answer='They were looking for the one who had been born King of the Jews.'), Part2Item(reference='[2:2]', question='Why were they looking for the King of the Jews?', answer='They said that they saw his star and were coming to worship him.'), Part2Item(reference='[2:3]', question='Why do you think that Herod was troubled when he heard the wise men wanted to find the King of the Jews that had just been born?', answer='(Answer may vary.) Herod was probably worried that a new king might take away his own position as king.'), Part2Item(reference='[2:4]', question='How did Herod find out where the Christ would be born?', answer='He asked the priests and scribes of the Jewish people where Christ would be born.'), Part2Item(reference='[2:5-6]', question='How did the priests and scribes know where Christ would be born?', answer='The scriptures said that a ruler would come from Bethlehem.'), Part2Item(reference='[2:9-10]', question='How did the wise men find the one who was born king of the Jews?', answer='They left Jerusalem, and the star guided them to the house where the child was.'), Part2Item(reference='[2:11]', question='What did the wise men do when they found the child?', answer='They fell down and worshiped him, and they opened their gifts and gave them to him.'), Part2Item(reference='[2:11]', question='Who do you think the child was that they were worshiping?', answer='From the rest of the passage, it is clear that the child was Jesus.'), Part2Item(reference='[2:12]', question='Why didn’t the wise men return to Herod?', answer='They had been warned by God in a dream not to return to Herod.')], part_2_directive='Answer the following questions from the specified verses.', comment_section='')),
     3: RGChapter(content=ParsedText(bible_reference=BibleReference(book_code='mat', book_name='Matthew', chapter=3, verse_ref='13-17'), background='After Jesus grew up, John the Baptist went into the wilderness and preached that people should stop sinning and be baptized. John also taught that someone more powerful than he would come, and that person would judge people.', directive='Read the passage.', part_1=[Part1Item(text='Jesus came to the Jordan River to be baptized by John.', reference='[3:13]'), Part1Item(text='John tried to stop Jesus, but Jesus said it was right for John to baptize him.', reference='[3:14-15]'), Part1Item(text='After John baptized Jesus, God’s Spirit came down like a dove and rested on Jesus.', reference='[3:16]'), Part1Item(text='A voice from heaven said, “This is my beloved Son. I am very pleased with him.”', reference='[3:17]')], part_1_directive='Tell in your own words what you just read in this passage.', part_2=[Part2Item(reference='[3:14]', question='When Jesus came to be baptized, what did John tell Jesus?', answer='John told Jesus that he needed to be baptized by Jesus.'), Part2Item(reference='[3:15]', question='What did Jesus say was the reason that John should baptize him?', answer='It was right for them to fulfill all righteousness.'), Part2Item(reference='[3:16]', question='What did the Spirit of God do when Jesus came out of the water?', answer='The Spirit of God came down and rested on Jesus.'), Part2Item(reference='[3:17]', question='What did the voice from heaven say after Jesus came out of the water?', answer='The voice said, “This is my beloved Son. I am very pleased with him.”'), Part2Item(reference='[3:17]', question='Whose voice do you think was speaking?', answer='By saying the voice came out of heaven, the passage shows that it was the voice of God the Father.')], part_2_directive='Answer the following questions from the specified verses.', comment_section='')),
     4: RGChapter(content=ParsedText(bible_reference=BibleReference(book_code='mat', book_name='Matthew', chapter=4, verse_ref='1-11'), background='', directive='Read the passage.', part_1=[Part1Item(text='The Spirit led Jesus into the wilderness.', reference='[4:1]'), Part1Item(text='Jesus fasted, and he was hungry.', reference='[4:2]'), Part1Item(text='The devil tempted Jesus three times.', reference='[4:3-10]'), Part1Item(text='Each time, Jesus quoted scripture to the devil.', reference='[4:4-10]'), Part1Item(text='After the devil left him, angels came and served Jesus.', reference='[4:11]')], part_1_directive='Tell in your own words what you just read in this passage.', part_2=[Part2Item(reference='[4:2]', question='How long did Jesus fast?', answer='Jesus fasted for forty days.'), Part2Item(reference='[4:3]', question='What did the devil first tempt Jesus to do?', answer='The devil tempted Jesus to command the stones to become bread.'), Part2Item(reference='[4:4]', question='How did Jesus respond?', answer='Jesus quoted what was written about not living on just bread but on every word that comes out of the mouth of God.'), Part2Item(reference='[4:4]', question='What do you think it means to live on God’s word?', answer='(Answer may vary.) It may mean to believe God’s word and obey it. It may mean that God’s words are needed by all, just as food is.'), Part2Item(reference='[4:5-6]', question='What did the devil next tempt Jesus to do?', answer='The devil tempted Jesus to throw himself down from the highest part of the temple building.'), Part2Item(reference='[4:7]', question='How did Jesus respond?', answer='Jesus quoted what was written about not testing the Lord God.'), Part2Item(reference='[4:3, 6]', question='When the devil tempted Jesus the first two times, what part of what he said was the same?', answer='Both times the devil said, “If you are the Son of God.”'), Part2Item(reference='[4:3-4]', question='Do you think that Jesus would have been able to turn the stones into bread?', answer='Why do you think that? (Answer may vary.) Probably Jesus would have been able to do that because he was the Son of God.'), Part2Item(reference='[4:8-9]', question='The devil said that he would give Jesus the kingdoms of the world if Jesus would do what?', answer='The devil said that he would give the kingdoms to Jesus if Jesus would fall down and worship him.'), Part2Item(reference='[4:10]', question='How did Jesus respond?', answer='Jesus told Satan to go away, and he quoted what was written about worshiping only the Lord God.'), Part2Item(reference='[4:4, 7, 10]', question='Where do you think the words that Jesus quoted were written?', answer='Here and in other parts of the New Testament, the words “it is written” indicate that they were written in the scriptures—in the part of the Bible now called the Old Testament.')], part_2_directive='Answer the following questions from the specified verses.', comment_section='')),
     5: RGChapter(content=ParsedText(bible_reference=BibleReference(book_code='mat', book_name='Matthew', chapter=5, verse_ref='1-12'), background='Jesus went around teaching people to repent because the kingdom of God was near. He also told some men to follow him, and he healed many people. Large crowds of people followed Jesus.', directive='Read the passage.', part_1=[Part1Item(text='Jesus went up on a mountain and taught his disciples.', reference='[5:1-2]'), Part1Item(text='Jesus described people who were blessed and then told how they would be blessed.', reference='[5:2-12]'), Part1Item(text='Jesus told the disciples to rejoice when they were persecuted for believing in him.', reference='[5:11-12]')], part_1_directive='Tell in your own words what you just read in this passage.', part_2=[Part2Item(reference='[5:1-2]', question='What did Jesus do when he saw the crowds?', answer='Jesus went up on a mountain and taught his disciples.'), Part2Item(reference='[5:3]', question='Who does the kingdom of heaven belong to?', answer='It belongs to the poor in spirit.'), Part2Item(reference='[5:4]', question='Who will be comforted?', answer='Those who mourn will be comforted.'), Part2Item(reference='[5:5]', question='Who will inherit the earth?', answer='The meek will inherit the earth.'), Part2Item(reference='[5:6]', question='Who will be filled?', answer='Those who hunger and thirst for righteousness will be filled.'), Part2Item(reference='[5:6]', question='What do you think those who hunger and thirst for righteousness will be filled with?', answer='(Answer may vary.) The passage probably means they will be filled with righteousness.'), Part2Item(reference='[5:7]', question='Who will receive mercy?', answer='The merciful will receive mercy.'), Part2Item(reference='[5:8]', question='Who will see God?', answer='The pure in heart will see God.'), Part2Item(reference='[5:9]', question='Who will be called sons of God?', answer='The peacemakers will be called sons of God.'), Part2Item(reference='[5:9]', question='Why do you think the peacemakers will be called sons of God?', answer='(Answer may vary.) The passage might mean that by helping people to have peace with one another, they will reflect the character of God, who enables people to have peace with him.'), Part2Item(reference='[5:10]', question='Who does the kingdom of heaven belong to?', answer="It belongs to those who are persecuted for righteousness' sake.")], part_2_directive='Answer the following questions from the specified verses.', comment_section='')),
     6: RGChapter(content=ParsedText(bible_reference=BibleReference(book_code='mat', book_name='Matthew', chapter=6, verse_ref='1-15'), background='Jesus continued to teach his disciples on the mountain.', directive='Read the passage.', part_1=[Part1Item(text='Jesus taught people not to do good works in order to be seen by other people.', reference='[6:1-4]'), Part1Item(text='Jesus taught people not to pray in order to be seen by other people.', reference='[6:5-8]'), Part1Item(text='Jesus taught people how to pray.', reference='[6:9-13]'), Part1Item(text='Jesus taught about forgiveness.', reference='[6:14-15]')], part_1_directive='Tell in your own words what you just read in this passage.', part_2=[Part2Item(reference='[6:1]', question='What did Jesus warn them against doing?', answer='He warned them not to do their good deeds to be seen by others.'), Part2Item(reference='[6:1]', question='What did he say the result of doing their good deeds to be seen by others would be?', answer='Their Father in heaven would not reward them.'), Part2Item(reference='[6:1]', question='Who do you think Jesus meant when he spoke of their Father in heaven?', answer='It is evident that he was talking about God the Father.'), Part2Item(reference='[6:2]', question='Why did hypocrites sound a trumpet when they gave to the poor?', answer='Because they wanted other people to glorify them.'), Part2Item(reference='[6:3]', question='When Jesus said not to let their left hand know what their right hand was doing, what do you think he meant?', answer='(Answer may vary.) He may have meant that they should do their good works so secretly that even those closest to them would not know about it. Or maybe it should become so customary or simple to do a good work that they might not even remember doing it.'), Part2Item(reference='[6:4, 6]', question='What did Jesus say about the Father in verses 4 and 6?', answer='The Father sees who gives and prays in secret, and he will reward these people.'), Part2Item(reference='[6:8]', question='What did he say the Father knows in verse 8?', answer='He knows what people need before they ask for it.'), Part2Item(reference='[6:8]', question='What did Jesus tell his disciples to call God when they prayed?', answer='He told them to call him Father.'), Part2Item(reference='[6:9-13]', question='What things did Jesus tell them to pray about?', answer='He said to pray for: the Father’s name to be honored as holy his kingdom to come his will to be done their daily needs forgiveness protection from temptation and evil'), Part2Item(reference='[6:14]', question='What did Jesus say the Father would do if they would forgive other people?', answer='He said the Father would forgive them.')], part_2_directive='Answer the following questions from the specified verses.', comment_section='')),
     13: RGChapter(content=ParsedText(bible_reference=BibleReference(book_code='mat', book_name='Matthew', chapter=13, verse_ref='44-46'), background='Jesus went and sat down beside the sea. A large crowd gathered around him, and he used parables to teach them about the kingdom of God.', directive='Read the passage.', part_1=[Part1Item(text='Jesus said that the kingdom of heaven is like a treasure hidden in a field.', reference='[13:44]'), Part1Item(text='Jesus also said that the kingdom of heaven is like a merchant looking for valuable pearls.', reference='[13:45-46]')], part_1_directive='Tell in your own words what you just read in this passage.', part_2=[Part2Item(reference='[13:44]', question='How did Jesus describe the kingdom of heaven in verse 44?', answer='It is like a treasure hidden in a field.'), Part2Item(reference='[13:44]', question='What did the man do when he found the treasure hidden in the field?', answer='The man hid the treasure and sold all his possessions and bought the field.'), Part2Item(reference='[13:44]', question='Why do you think the man bought the field?', answer='He probably wanted the treasure that was hidden in the field.'), Part2Item(reference='[13:45]', question='How did Jesus describe the kingdom of heaven in verse 45?', answer='The kingdom of heaven is like a man who was a merchant looking for valuable pearls.'), Part2Item(reference='[13:46]', question='What did the man do when he found a very valuable pearl?', answer='He went and sold everything that he owned and bought it.'), Part2Item(reference='[13:44-46]', question='Why do you think the two men in the stories sold everything they possessed?', answer='It appears that they sold everything so they could get enough money to buy the land and the pearl.')], part_2_directive='Answer the following questions from the specified verses.', comment_section='')),
     14: RGChapter(content=ParsedText(bible_reference=BibleReference(book_code='mat', book_name='Matthew', chapter=14, verse_ref='13-21'), background='King Herod killed Jesus’ cousin, John the Baptist. John’s disciples went and told Jesus about it. ', directive='Read the passage. Read the passage.', part_1=[Part1Item(text='Jesus went to a place far away from people, but the crowds followed him, and he had compassion on them.', reference='[14:13-14]'), Part1Item(text='Jesus told his disciples to feed the people, but they could only find a small amount of food.', reference='[14:15-18]'), Part1Item(text='Jesus blessed the food and gave it to the disciples, and they gave it to the people.', reference='[14:19]'), Part1Item(text='There was enough for over 5,000 people. After the people ate, there was a lot of food left over.', reference='[14:20-21]'), Part1Item(text='Jesus’ disciples got into a boat and went out on the sea.', reference='[14:22]'), Part1Item(text='At night, Jesus walked on the water to his disciples. He told them not to be afraid.', reference='[14:25-27]'), Part1Item(text='Peter walked toward Jesus on the water, but he began to sink. Jesus saved him.', reference='[14:29-31]'), Part1Item(text='The wind stopped blowing.', reference='[14:32]'), Part1Item(text='The disciples worshiped Jesus.', reference='[14:33]')], part_1_directive='Tell in your own words what you just read in this passage. Tell in your own words what you just read in this passage.', part_2=[Part2Item(reference='[14:13]', question='Where did Jesus go in a boat?', answer='He went to a place far away from people.'), Part2Item(reference='[14:14]', question='What did Jesus do when he saw the large crowd of people?', answer='He had compassion on them, and he healed those who were sick.'), Part2Item(reference='[14:15]', question='Why did the disciples want Jesus to send the crowds away?', answer='Because it was late in the day, the disciples knew the people needed to go to the villages to buy food.'), Part2Item(reference='[14:16]', question='What did Jesus tell his disciples to do?', answer='He told them to give the people something to eat.'), Part2Item(reference='[14:17]', question='How did the disciples reply to Jesus?', answer='They said that they had only five loaves of bread and two fish.'), Part2Item(reference='[14:17]', question='Why do you think the disciples said this to Jesus?', answer='It appears that they were telling Jesus they did not have enough food to give to so many people.'), Part2Item(reference='[14:19]', question='What did Jesus do with the food?', answer='He looked up to heaven, blessed the food, broke the loaves, and gave them to his disciples.'), Part2Item(reference='[14:20]', question='After the people all ate, how much food was left over?', answer='Twelve baskets full of food were left over.'), Part2Item(reference='[14:21]', question='How many people ate the food that Jesus provided?', answer='About 5,000 men, plus women and children, ate the food.'), Part2Item(reference='[14:23]', question='What did Jesus do on the mountain?', answer='He prayed.'), Part2Item(reference='[14:24]', question='What happened while the disciples were in the boat?', answer='The wind blew strongly against them, and the boat was tossed around by the waves.'), Part2Item(reference='[14:25]', question='What unusual thing did Jesus do in verse 25?', answer='Jesus walked to them on the water.'), Part2Item(reference='[14:26]', question='Why do you think that the disciples thought that the person walking to them on the sea was a ghost?', answer='(Answer may vary.) They probably thought this because people have bodies that cannot walk on the sea.'), Part2Item(reference='[14:28]', question='What did Peter ask Jesus to do to show that it really was him walking on the water?', answer='Peter asked Jesus to command him to go to him on the water.'), Part2Item(reference='[14:30]', question='What happened when Peter was walking on the water, and he saw the wind?', answer='Peter became afraid, and he began to sink.'), Part2Item(reference='[14:30]', question='What did Peter do when he began to sink?', answer='He cried out to the Lord to save him.'), Part2Item(reference='[14:31-32]', question='How did Jesus save Peter?', answer='Jesus grabbed Peter and they went into the boat.'), Part2Item(reference='[14:32]', question='What happened when Jesus and Peter went into the boat?', answer='The wind stopped blowing.'), Part2Item(reference='[14:33]', question='How did the disciples respond?', answer='They worshiped Jesus and acknowledged that Jesus is the Son of God.'), Part2Item(reference='[14:25-32]', question='What events in this passage do you think showed the disciples that Jesus was the Son of God?', answer='Jesus walked on the sea, Jesus enabled Peter to walk on the sea, and Jesus made the wind stop blowing.'), Part2Item(reference='[14:34-35]', question='When the boat got to land, what did the men in that place do?', answer='They sent messages to the surrounding area, and people brought sick people to Jesus.'), Part2Item(reference='[14:36]', question='What do you think was the reason that people wanted to touch the edge of Jesus’ garment?', answer='They probably believed (had faith) that just touching Jesus’ garment would heal them.')], part_2_directive='Answer the following questions from the specified verses. Answer the following questions from the specified verses.', comment_section=' '))},
      lang_direction=LangDirEnum.LTR
    )
    """
    path = join(assets_dir, resource_dir, docx_file_path)
    # logger.debug("path: %s exists: %s", path, exists(path))
    # TODO Check if resource_dir exists and if it doesn't then submit
    # a document request to DOC API to make sure it is cloned.
    # Currently we don't have to do this because at startup we copy
    # English NT Survey RG doc into place.
    # assert exists(path)
    rg_books = get_rg_books(
        path,
        lang_code,
        lang_name,
        resource_type_name,
        lang_direction,
    )
    rg_book_chapters = [
        chapter for rg_book in rg_books for chapter in rg_book.chapters.values()
    ]
    bible_references = [
        pt.bible_reference
        for chapter in rg_book_chapters
        for pt in chapter.content  # content is now list[ParsedText]
    ]
    # Localize the book names since they are provided in English from en_rg_nt_survey.docx
    book_name_map = {
        book_code_and_name[0]: book_code_and_name[1]
        for book_code_and_name in book_codes_for_lang_from_usfm_only(lang_code)
    }
    for bible_reference in bible_references:
        maybe_localized_book_name = book_name_map.get(
            bible_reference.book_code, bible_reference.book_name
        )
        logger.debug("maybe_localized_book_name: %s", maybe_localized_book_name)
        bible_reference.book_name = maybe_localized_book_name
    return bible_references


if __name__ == "__main__":

    # To run the doctests in this module, in the root of the project do:
    # python backend/document/domain/resource_lookup.py
    # or
    # python backend/document/domain/resource_lookup.py -v
    # See https://docs.python.org/3/library/doctest.html
    # for more details.
    import doctest

    doctest.testmod()
