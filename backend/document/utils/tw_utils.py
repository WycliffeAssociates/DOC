"""
Useful functions that are not class or instance specific for TW
resources that we use in multiple places.
"""

import os
import pathlib
from glob import glob
from typing import Optional

from document.config import settings


logger = settings.logger(__name__)

TW = "tw"


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
