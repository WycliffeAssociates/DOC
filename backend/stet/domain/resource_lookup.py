from typing import Sequence

from doc.config import settings
from doc.domain.resource_lookup import fetch_source_data
from doc.utils.list_utils import unique_tuples

# List of languages which do not have USFM available for NT books. We use this
# to filter these out of STET's list of source and target
# languages so that the user doesn't have the frustrating experience of
# selecting a language which might have OT USFM resources available but
# not NT USFM so that when their resulting doc is generated no scripture is
# present. It makes it seem like a bug in STET and is bad UX.
LANG_CODES_WITH_NO_NT_USFM: frozenset[str] = frozenset(["ru"])

logger = settings.logger(__name__)


def lang_codes_and_names_having_usfm(
    lang_code_filter_list: frozenset[str] = LANG_CODES_WITH_NO_NT_USFM,
    gateway_languages: frozenset[str] = settings.GATEWAY_LANGUAGES,
) -> Sequence[tuple[str, str, bool]]:
    """
    >>> from doc.domain import resource_lookup
    >>> ();result = resource_lookup.lang_codes_and_names_having_usfm();() # doctest: +ELLIPSIS
    (...)
    >>> result[0]
    ('abz', 'Abui', False)
    >>> heart_lang_codes = [lang_code_and_name[0] for lang_code_and_name in resource_lookup.lang_codes_and_names_having_usfm() if not lang_code_and_name[2]]
    >>> sorted(heart_lang_codes)[0]
    'aao'
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
