"""
This module provides an API for looking up the location of a
resource's asset files in the cloud and acquiring said resource
assets.
"""
import shutil
import subprocess
from os.path import exists, join, sep
from typing import Any, Optional, Sequence
from urllib.parse import urlparse

import requests
from document.config import settings
from document.domain import bible_books, exceptions
from document.domain.model import ResourceLookupDto
from document.utils.file_utils import file_needs_update
from fastapi import HTTPException, status

from pydantic import HttpUrl

logger = settings.logger(__name__)


# Get data by graphql
def fetch_source_data(
    json_file_name: str = settings.SOURCE_DATA_JSON_FILENAME,
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
    # if file_needs_update(json_file_path):
    #     logger.debug("Downloading %s...", json_file_name)
    try:
        data = download_data(json_file_path)
        # logger.debug("data: %s", data)
    except Exception:
        logger.exception("Caught exception: ")
    # FIXME The json somehow ends up with single quotes rather than double and is thus invalid and not readable from file.
    # else:
    #     if exists(json_file_path):
    #         logger.debug("json_file_path, %s, does exist", json_file_path)
    #         content = read_file(json_file_path)
    #         logger.debug("json data: %s", content)
    #         data = json.loads(content)
    #     else:
    #         logger.debug("json_file_path, %s, does not exist", json_file_path)
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
    graphql_query = """
query MyQuery {
  git_repo(
    where: {content: {wa_content_meta: {status: {_eq: "Primary"}, show_on_biel: {_eq: true}}}}
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
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            return data["data"]
        else:
            # Log error if request failed
            response.raise_for_status()
    except Exception as e:
        return {"error": str(e)}
    # logger.debug("Writing json data to: %s", jsonfile_path)
    # with open(jsonfile_path, "w") as fp:
    #     fp.write(str(data["data"]))
    # return data


def lang_codes_and_names(
    lang_code_filter_list: Sequence[str] = settings.LANG_CODE_FILTER_LIST,
    gateway_languages: Sequence[str] = settings.GATEWAY_LANGUAGES,
) -> Sequence[tuple[str, str, bool]]:
    """
    >>> from document.domain import resource_lookup
    >>> ();result = resource_lookup.lang_codes_and_names();() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    ('abz', 'Abui', False)
    """
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
            is_gateway = ietf_code in gateway_languages
            if ietf_code not in lang_code_filter_list:
                if english_name in national_name:
                    values.append((ietf_code, national_name, is_gateway))
                else:
                    values.append(
                        (ietf_code, f"{national_name} ({english_name})", is_gateway)
                    )

    except:
        logger.exception("Failed due to the following exception")
    # NOTE This is how we used to use toolz unique
    # unique_values = unique(values, key=lambda value: value[0])
    unique_values = []
    seen_values = set()
    for value in values:
        if value[0] not in seen_values:
            unique_values.append(value)
            seen_values.add(value[0])
    return sorted(unique_values, key=lambda value: value[1])


RESOURCE_TYPE_CODES_AND_NAMES = {
    "reg": "Bible",
    "ulb": "Unlocked Literal Bible",
    # "udb":  "Unlocked Dynamic Bible",
    "cuv": "新标点和合本",
    "f10": "French Louis Segond 1910 Bible",
    "nav": "New Arabic Version (Ketab El Hayat)",
    "ugnt": "unfoldingWord® Greek New Testament",
    "ayt": "Bahasa Indonesian Bible",
    "blv": "Portuguese Bíblia Livre",
    "tn-condensed": "Condensed Translation Notes",
    "tn": "Translation Notes",
    "tq": "Translation Questions",
    "tw": "Translation Words",
    "bc": "Bible Commentary",
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
    >>> # FIXME kbt shouldn't be obtainable due to an invalid URL in translations.json
    >>> ();data = resource_lookup.shared_book_codes("pt-br", "es-419");() # doctest: +ELLIPSIS
    (...)
    >>> list(data)
    [('gen', 'Genesis'), ('exo', 'Exodus'), ('lev', 'Leviticus'), ('num', 'Numbers'), ('deu', 'Deuteronomy'), ('jos', 'Joshua'), ('jdg', 'Judges'), ('rut', 'Ruth'), ('1sa', '1 Samuel'), ('2sa', '2 Samuel'), ('1ki', '1 Kings'), ('2ki', '2 Kings'), ('1ch', '1 Chronicles'), ('2ch', '2 Chronicles'), ('ezr', 'Ezra'), ('neh', 'Nehemiah'), ('est', 'Esther'), ('job', 'Job'), ('psa', 'Psalms'), ('pro', 'Proverbs'), ('ecc', 'Ecclesiastes'), ('sng', 'Song of Solomon'), ('isa', 'Isaiah'), ('jer', 'Jeremiah'), ('lam', 'Lamentations'), ('ezk', 'Ezekiel'), ('dan', 'Daniel'), ('hos', 'Hosea'), ('jol', 'Joel'), ('amo', 'Amos'), ('oba', 'Obadiah'), ('jon', 'Jonah'), ('mic', 'Micah'), ('nam', 'Nahum'), ('hab', 'Habakkuk'), ('zep', 'Zephaniah'), ('hag', 'Haggai'), ('zec', 'Zechariah'), ('mal', 'Malachi'), ('mat', 'Matthew'), ('mrk', 'Mark'), ('luk', 'Luke'), ('jhn', 'John'), ('act', 'Acts'), ('rom', 'Romans'), ('1co', '1 Corinthians'), ('2co', '2 Corinthians'), ('gal', 'Galatians'), ('eph', 'Ephesians'), ('php', 'Philippians'), ('col', 'Colossians'), ('1th', '1 Thessalonians'), ('2th', '2 Thessalonians'), ('1ti', '1 Timothy'), ('2ti', '2 Timothy'), ('tit', 'Titus'), ('phm', 'Philemon'), ('heb', 'Hebrews'), ('jas', 'James'), ('1pe', '1 Peter'), ('2pe', '2 Peter'), ('1jn', '1 John'), ('2jn', '2 John'), ('3jn', '3 John'), ('jud', 'Jude'), ('rev', 'Revelation')]
    """
    # Get book codes for reach language.
    lang0_book_codes = book_codes_for_lang(lang0_code)
    lang1_book_codes = book_codes_for_lang(lang1_code)
    # Find intersection of book codes:
    return [
        (x, y) for x, y in lang0_book_codes if x in [s for s, t in lang1_book_codes]
    ]


def get_last_segment(url: str) -> str:
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split("/")
    last_segment = path_segments[-1]
    return last_segment


def book_codes_for_lang(lang_code: str) -> Sequence[tuple[str, str]]:
    """
    >>> from document.domain import resource_lookup
    >>> ();result = resource_lookup.book_codes_for_lang("pt-br");() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    ('gen', 'Genesis')
    """

    data = fetch_source_data()
    book_codes = []
    try:
        repos_info = data["git_repo"]
        for repo_info in repos_info:
            content = repo_info["content"]
            language_info = content["language"]
            if language_info["ietf_code"] == lang_code:
                url = repo_info["repo_url"]
                last_segment = get_last_segment(url)
                book_code = last_segment.split("_")[1]
                if book_code in bible_books.BOOK_NAMES:
                    book_codes.append((book_code, bible_books.BOOK_NAMES[book_code]))
    except:
        pass
    if not book_codes:
        # If no values found, return all book codes and names because this
        # is the case when, e.g., the repo is something like en_ulb.
        return [(key, value) for key, value in bible_books.BOOK_NAMES.items()]
    else:
        # TODO Make sure unique
        return book_codes


def resource_lookup_dto(
    lang_code: str,
    resource_type: str,
    book_code: str,
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
    try:
        repos_info = data["git_repo"]
        for repo_info in repos_info:
            content = repo_info["content"]
            language_info = content["language"]
            resource_type_ = content["resource_type"]
            book_code_ = repo_info["repo_url"].split("_")[1]
            if lang_code == language_info["ietf_code"]:
                if (
                    resource_type_ in RESOURCE_TYPE_CODES_AND_NAMES
                    and resource_type == resource_type_
                    and book_code_ == book_code
                ):
                    resource_lookup_dto = ResourceLookupDto(
                        lang_code=lang_code,
                        lang_name=language_info["english_name"],
                        resource_type=resource_type,
                        resource_type_name=RESOURCE_TYPE_CODES_AND_NAMES[resource_type],
                        book_code=book_code,
                        lang_direction=language_info["direction"],
                        url=repo_info["repo_url"],
                    )
                    break
            elif lang_code == "en" and resource_type == "tn-condensed":
                resource_lookup_dto = ResourceLookupDto(
                    lang_code=lang_code,
                    lang_name=language_info["english_name"],
                    resource_type=resource_type,
                    resource_type_name=RESOURCE_TYPE_CODES_AND_NAMES[resource_type],
                    book_code=book_code,
                    lang_direction=language_info["direction"],
                    url=settings.TN_CONDENSED_GIT_REPO_URL,
                )
                break
    except:
        logger.debug(
            "Problem creating ResourceLookupDto instance for %s, %s, %s, likely a data problem",
            lang_code,
            resource_type,
            book_code,
        )
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
            # NOTE This is how we used to do the next line
            # resource_lookup_dto.url.rpartition(sep)[2],
            get_last_segment(resource_lookup_dto.url),
        )
        # Check if resource assets need updating otherwise use
        # what we already have on disk.
        if file_needs_update(resource_filepath):
            clone_git_repo(resource_lookup_dto.url, resource_filepath)
        else:
            logger.debug("Cache hit for %s", resource_filepath)
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
    if exists(resource_filepath):
        logger.debug(
            "About to delete pre-existing git repo %s in order to recreate it due to cache staleness.",
            resource_filepath,
        )
        try:
            shutil.rmtree(resource_filepath)
        except OSError:
            logger.debug(
                "Directory %s was not removed due to an error.",
                resource_filepath,
            )
            logger.exception("Caught exception: ")
    if branch:  # CLient specified a particular branch
        command = "git clone --depth=1 --branch '{}' '{}' '{}'".format(
            branch, url, resource_filepath
        )
    else:
        command = "git clone --depth=1 '{}' '{}'".format(url, resource_filepath)
    logger.debug("Attempting to clone into %s ...", resource_filepath)
    try:
        subprocess.call(command, shell=True)
    except subprocess.SubprocessError:
        logger.debug("git command: %s", command)
        logger.debug("git clone failed!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="git clone failed",
        )
    else:
        logger.debug("git command: %s", command)
        logger.debug("git clone succeeded.")


if __name__ == "__main__":

    # To run the doctests in the this module, in the root of the project do:
    # python backend/document/domain/resource_lookup.py
    # or
    # python backend/document/domain/resource_lookup.py -v
    # See https://docs.python.org/3/library/doctest.html
    # for more details.
    import doctest

    doctest.testmod()
