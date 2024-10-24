from os.path import exists, join
import re
from re import finditer, search
from typing import Sequence

from document.config import settings
from document.domain.bible_books import BOOK_NUMBERS
from document.domain.model import (
    ResourceRequest,
    WikiLink,
)
from document.markdown_transforms.link_regexes import (
    TA_MARKDOWN_HTTPS_LINK_RE,
    TA_PREFIXED_MARKDOWN_HTTPS_LINK_RE,
    TA_PREFIXED_MARKDOWN_LINK_RE,
    TA_WIKI_PREFIXED_RC_LINK_RE,
    TA_WIKI_RC_LINK_RE,
    TA_STAR_RC_LINK_RE,
    TN_MARKDOWN_RELATIVE_SCRIPTURE_LINK_RE,
    TN_MARKDOWN_RELATIVE_TO_CURRENT_BOOK_SCRIPTURE_LINK_RE,
    TN_MARKDOWN_RELATIVE_TO_CURRENT_BOOK_SCRIPTURE_LINK_RE_NO_PARENS,
    TN_MARKDOWN_SCRIPTURE_LINK_RE,
    TN_OBS_MARKDOWN_LINK_RE,
    TW_MARKDOWN_LINK_RE,
    TW_RC_LINK_RE,
    TW_STAR_RC_LINK_RE,
    TW_WIKI_PREFIXED_RC_LINK_RE,
    TW_WIKI_RC_LINK_RE,
    TW_WIKI_RC_LINK_RE2,
    WIKI_LINK_RE,
)
from document.utils.file_utils import read_file
from document.utils.tw_utils import localized_translation_word

logger = settings.logger(__name__)


def remove_md_section(source: str, section_name: str) -> str:
    """
    Given markdown and a header text, removes the header and the
    text under the header until the next header is encountered.
    """
    header_regex = re.compile("^#.*$")
    section_regex = re.compile("^#+ *{}.*".format(section_name))
    out_md = ""
    in_section = False
    for line in source.splitlines():
        if in_section:
            if header_regex.match(line):
                # We found a header.  The section is over.
                out_md += line + "\n"
                in_section = False
        else:
            if section_regex.match(line):
                # We found the section header.
                in_section = True
            else:
                out_md = "{}{}\n".format(out_md, line)
    return out_md


def remove_sections(
    source: str, sections_to_remove: list[str] = settings.MARKDOWN_SECTIONS_TO_REMOVE
) -> str:
    """
    Removes sections with specified headers. That is, remove the
    header and all its content until the next header is encountered.
    """
    if sections_to_remove:
        for header in sections_to_remove:
            source = remove_md_section(source, header)
    return source


def transform_tw_links(
    source: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
    translation_words_dict: dict[str, str],
) -> str:
    # Transform the '...PREFIXED...' version of regexes in each
    # resource_type group first before its non-'...PREFIXED...' version
    # of regex otherwise we could orphan the prefix portion of the
    # phrase, e.g., you could be left with (Veja: ) or (See: ) or
    # (Blah blah blah: ).
    for wiki_link in wiki_link_parser(source):
        source = transform_tw_rc_link(
            wiki_link, source, lang_code, resource_requests, translation_words_dict
        )
        source = transform_tw_star_rc_link(
            wiki_link, source, lang_code, resource_requests, translation_words_dict
        )
    # Handle links pointing at TW resource assets
    source = transform_tw_wiki_prefixed_rc_links(
        source, lang_code, resource_requests, translation_words_dict
    )
    source = transform_tw_wiki_rc_links(
        source, lang_code, resource_requests, translation_words_dict
    )
    source = transform_tw_wiki_rc_links2(
        source, lang_code, resource_requests, translation_words_dict
    )
    source = transform_tw_markdown_links(
        source, lang_code, resource_requests, translation_words_dict
    )
    return source


def transform_ta_and_tn_links(
    source: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
) -> str:
    # Transform the '...PREFIXED...' version of regexes in each
    # resource_type group first before its non-'...PREFIXED...' version
    # of regex otherwise we could orphan the prefix portion of the
    # phrase, e.g., you could be left with (Veja: ) or (See: ) or
    # (Blah blah blah: ).
    # Handle links pointing at TA resource assets
    source = transform_ta_prefixed_wiki_rc_links(source)
    source = transform_ta_wiki_rc_links(source)
    source = transform_ta_star_rc_links(source)
    source = transform_ta_prefixed_markdown_https_links(source)
    source = transform_ta_markdown_links(source)
    source = transform_ta_markdown_https_links(source)
    # Handle links pointing at TN resource assets
    source = transform_tn_prefixed_markdown_links(source, resource_requests)
    source = transform_tn_markdown_links(source, lang_code, resource_requests)
    # NOTE Haven't decided yet if we should use this next method or instead
    # have human translators use more explicit scripture reference that
    # includes the book_code, e.g., col, rather than leave it out. If
    # they did provide the book_code then this case would be picked up
    # by self.transform_tn_markdown_links.
    source = transform_tn_missing_book_code_markdown_links(
        source, lang_code, resource_requests
    )
    source = transform_tn_missing_book_code_markdown_links_no_paren(source)
    source = transform_tn_obs_markdown_links(source)
    return source


def transform_tw_rc_link(
    wikilink: WikiLink,
    source: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
    translation_words_dict: dict[str, str],
    tw: str = "tw",
    fmt_str: str = settings.TRANSLATION_WORD_ANCHOR_LINK_FMT_STR,
) -> str:
    """
    Transform the translation word rc wikilink into a Markdown
    source anchor link pointing to a destination anchor link for
    the translation word definition if it exists or replace the
    link with the non-localized word if it doesn't.
    """
    match = search(TW_RC_LINK_RE, wikilink.url)
    if match:
        # Determine if resource_type TW was one of the requested
        # resources.
        url = wikilink.url
        tw_resources_requests = [
            resource_request
            for resource_request in resource_requests
            if tw in resource_request.resource_type
        ]
        filename_sans_suffix = match.group("word")
        # Check that there are translation word asset files available for this
        # resource _and_ that the document request included a request for them.
        # The check is necessary because TW resource asset files might be
        # available on disk, in the cache, from a previous document request but
        # the current document request may not have requested them
        # - if it hasn't requested the TW resource in this document request then
        # we should not make links to TW word definitions. Hence the need to
        # also check tw_resources_requests.
        if filename_sans_suffix in translation_words_dict and tw_resources_requests:
            # Localize the translation word.
            file_content = read_file(translation_words_dict[filename_sans_suffix])
            # Get the localized name for the translation word.
            localized_translation_word_ = localized_translation_word(file_content)
            # Build the anchor link.
            url = url.replace(
                match.group(0),  # The whole match
                fmt_str.format(
                    localized_translation_word_,
                    lang_code,
                    localized_translation_word_,
                ),
            )
        else:
            url = url.replace(match.group(0), filename_sans_suffix)
        regexp = r"\[\[{}\]\]".format(wikilink.url)
        for match2 in finditer(regexp, source):
            source = source.replace(match2.group(0), url)
    return source


def remove_pagination_symbols(source: str) -> str:
    source = source.replace("<strong>| &gt;&gt;</strong>", "")
    source = source.replace("<p>__&lt;&lt; | __</p>", "")
    return source.replace("<strong>&lt;&lt; | &gt;&gt;</strong>", "")


def transform_tw_markdown_links(
    source: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
    translation_words_dict: dict[str, str],
    tw: str = "tw",
    fmt_str: str = settings.TRANSLATION_WORD_ANCHOR_LINK_FMT_STR,
) -> str:
    """
    Transform the translation word relative file link into a
    source anchor link pointing to a destination anchor link for
    the translation word definition.
    """
    # Determine if resource_type TW was one of the requested
    # resources.
    tw_resources_requests = [
        resource_request
        for resource_request in resource_requests
        if tw in resource_request.resource_type
    ]
    for match in finditer(TW_MARKDOWN_LINK_RE, source):
        match_text = match.group(0)
        filename_sans_suffix = match.group("word")
        if filename_sans_suffix in translation_words_dict and tw_resources_requests:
            # Localize non-English languages.
            file_content = read_file(translation_words_dict[filename_sans_suffix])
            # Get the localized name for the translation word
            localized_translation_word_ = localized_translation_word(file_content)
            # Build the anchor links
            source = source.replace(
                match_text,
                fmt_str.format(
                    localized_translation_word_,
                    lang_code,
                    localized_translation_word_,
                ),
            )
        else:
            logger.debug(
                "TW file for filename_sans_suffix: %s not found for lang_code: %s",
                filename_sans_suffix,
                lang_code,
            )
            # Search for translation word relative link
            # and remove it along with any trailing comma from
            # the source text.
            # NOTE Theoretically, this will leave a trailing comma after the link
            # if the link is not the last link in a list of links. I haven't
            # yet seen such a case in practice though.
            match_text_plus_preceding_dot_utf8_char = "· {}".format(match_text)
            source = source.replace(match_text_plus_preceding_dot_utf8_char, "")
    return source


def transform_tw_wiki_rc_links(
    source: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
    translation_words_dict: dict[str, str],
    tw: str = "tw",
    fmt_str: str = settings.TRANSLATION_WORD_ANCHOR_LINK_FMT_STR,
) -> str:
    """
    Transform the translation word rc link into source anchor link
    pointing to a destination anchor link for the translation word
    definition.
    """
    # Determine if resource_type TW was one of the requested
    # resources.
    tw_resources_requests = [
        resource_request
        for resource_request in resource_requests
        if tw in resource_request.resource_type
    ]
    for match in finditer(TW_WIKI_RC_LINK_RE, source):
        filename_sans_suffix = match.group("word")
        if filename_sans_suffix in translation_words_dict and tw_resources_requests:
            # Localize non-English languages.
            file_content = read_file(translation_words_dict[filename_sans_suffix])
            # Get the localized name for the translation word
            localized_translation_word_ = localized_translation_word(file_content)
            # Build the anchor links
            source = source.replace(
                match.group(0),  # The whole match
                fmt_str.format(
                    localized_translation_word_,
                    lang_code,
                    localized_translation_word_,
                ),
            )
        else:
            logger.debug(
                "TW file for filename_sans_suffix: %s not found for lang_code: %s",
                filename_sans_suffix,
                lang_code,
            )
            # Search for translation word relative link
            # and remove it along with any trailing comma from
            # the source text.
            # FIXME Theoretically, this will leave a trailing comma after the link
            # if the link is not the last link in a list of links. I haven't
            # actually seen this case though in practice.
            source = source.replace(match.group(0), "")
    return source


def transform_tw_wiki_rc_links2(
    source: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
    translation_words_dict: dict[str, str],
    tw: str = "tw",
    fmt_str: str = settings.TRANSLATION_WORD_ANCHOR_LINK_FMT_STR,
) -> str:
    """
    Transform the translation word rc link into source anchor link
    pointing to a destination anchor link for the translation word
    definition.
    """
    # Determine if resource_type TW was one of the requested
    # resources.
    tw_resources_requests = [
        resource_request
        for resource_request in resource_requests
        if tw in resource_request.resource_type
    ]
    for match in finditer(TW_WIKI_RC_LINK_RE2, source):
        filename_sans_suffix = match.group("word")
        if filename_sans_suffix in translation_words_dict and tw_resources_requests:
            # Localize non-English languages.
            file_content = read_file(translation_words_dict[filename_sans_suffix])
            # Get the localized name for the translation word
            localized_translation_word_ = localized_translation_word(file_content)
            # Build the anchor links
            source = source.replace(
                match.group(0),  # The whole match
                fmt_str.format(
                    localized_translation_word_,
                    lang_code,
                    localized_translation_word_,
                ),
            )
        else:
            logger.debug(
                "TW file for filename_sans_suffix: %s not found for lang_code: %s",
                filename_sans_suffix,
                lang_code,
            )
            # Search for translation word relative link
            # and remove it along with any trailing comma from
            # the source text.
            # FIXME Theoretically, this will leave a trailing comma after the link
            # if the link is not the last link in a list of links. I haven't
            # actually seen this case though in practice.
            source = source.replace(match.group(0), "")
    return source


def transform_tw_star_rc_link(
    wikilink: WikiLink,
    source: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
    translation_words_dict: dict[str, str],
    tw: str = "tw",
    fmt_str: str = settings.TRANSLATION_WORD_ANCHOR_LINK_FMT_STR,
) -> str:
    """
    Transform the translation word rc wikilink into a Markdown
    source anchor link pointing to a destination anchor link for
    the translation word definition if it exists or replace the
    link with the non-localized word if it doesn't.
    """
    match = search(TW_STAR_RC_LINK_RE, wikilink.url)
    if match:
        # Determine if resource_type TW was one of the requested
        # resources.
        url = wikilink.url
        tw_resources_requests = [
            resource_request
            for resource_request in resource_requests
            if tw in resource_request.resource_type
        ]
        filename_sans_suffix = match.group("word")
        # Check that there are translation word asset files available for this
        # resource _and_ that the document request included a request for them.
        # The check is necessary because TW resource asset files might be
        # available on disk, in the cache, from a previous document request but
        # the current document request may not have requested them
        # - if it hasn't requested the TW resource in this document request then
        # we should not make links to TW word definitions. Hence the need to
        # also check tw_resources_requests.
        if filename_sans_suffix in translation_words_dict and tw_resources_requests:
            # Localize the translation word.
            file_content = read_file(translation_words_dict[filename_sans_suffix])
            # Get the localized name for the translation word.
            localized_translation_word_ = localized_translation_word(file_content)
            # Build the anchor link.
            url = url.replace(
                match.group(0),  # The whole match
                fmt_str.format(
                    localized_translation_word_,
                    lang_code,
                    localized_translation_word_,
                ),
            )
        else:
            url = url.replace(match.group(0), filename_sans_suffix)
        regexp = r"\[\[{}\]\]".format(wikilink.url)
        for match2 in finditer(regexp, source):
            source = source.replace(match2.group(0), url)
    return source


# def transform_tw_star_rc_links(
#     source: str,
#     lang_code: str,
#     resource_requests: Sequence[ResourceRequest],
#     translation_words_dict: dict[str, str],
#     tw: str = "tw",
#     fmt_str: str = settings.TRANSLATION_WORD_ANCHOR_LINK_FMT_STR,
# ) -> str:
#     """
#     Transform the translation word rc link into source anchor link
#     pointing to a destination anchor link for the translation word
#     definition.
#     """
#     # Determine if resource_type TW was one of the requested
#     # resources.
#     tw_resources_requests = [
#         resource_request
#         for resource_request in resource_requests
#         if tw in resource_request.resource_type
#     ]
#     for match in finditer(TW_STAR_RC_LINK_RE, source):
#         filename_sans_suffix = match.group("word")
#         if filename_sans_suffix in translation_words_dict and tw_resources_requests:
#             # Localize non-English languages.
#             file_content = read_file(translation_words_dict[filename_sans_suffix])
#             # Get the localized name for the translation word
#             localized_translation_word_ = localized_translation_word(file_content)
#             # Build the anchor links
#             source = source.replace(
#                 match.group(0),  # The whole match
#                 fmt_str.format(
#                     localized_translation_word_,
#                     lang_code,
#                     localized_translation_word_,
#                 ),
#             )
#         else:
#             logger.debug(
#                 "TW file for filename_sans_suffix: %s not found for lang_code: %s",
#                 filename_sans_suffix,
#                 lang_code,
#             )
#             # Search for translation word relative link
#             # and remove it along with any trailing comma from
#             # the source text.
#             # FIXME Theoretically, this will leave a trailing comma after the link
#             # if the link is not the last link in a list of links. I haven't
#             # actually seen this case though in practice.
#             source = source.replace(match.group(0), "")
#     return source


def transform_tw_wiki_prefixed_rc_links(
    source: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
    translation_words_dict: dict[str, str],
    tw: str = "tw",
    fmt_str: str = settings.TRANSLATION_WORD_PREFIX_ANCHOR_LINK_FMT_STR,
) -> str:
    """
    Transform the translation word rc TW wikilink into source anchor link
    pointing to a destination anchor link for the translation word
    definition.
    """
    # Determine if resource_type TW was one of the requested
    # resources.
    tw_resources_requests = [
        resource_request
        for resource_request in resource_requests
        if tw in resource_request.resource_type
    ]
    for match in finditer(TW_WIKI_PREFIXED_RC_LINK_RE, source):
        filename_sans_suffix = match.group("word")
        if filename_sans_suffix in translation_words_dict and tw_resources_requests:
            # Need to localize non-English languages.
            file_content = read_file(translation_words_dict[filename_sans_suffix])
            # Get the localized name for the translation word
            localized_translation_word_ = localized_translation_word(file_content)
            # Build the anchor links
            source = source.replace(
                match.group(0),  # The whole match
                fmt_str.format(
                    match.group("prefix_text"),
                    localized_translation_word_,
                    lang_code,
                    localized_translation_word_,
                ),
            )
        else:
            logger.debug(
                "TW file for filename_sans_suffix: %s not found for lang_code: %s",
                filename_sans_suffix,
                lang_code,
            )
            # Search for translation word relative link and remove it along with any
            # trailing comma from the source text.
            source = source.replace(match.group(0), "")
    return source


def transform_ta_prefixed_wiki_rc_links(source: str) -> str:
    """
    Transform the translation academy rc wikilink into source anchor link
    pointing to a destination anchor link for the translation academy
    reference.
    """
    # FIXME When TA gets implemented we'll need to actually build
    # the anchor link.
    for match in finditer(TA_WIKI_PREFIXED_RC_LINK_RE, source):
        # For now, remove match text
        source = source.replace(match.group(0), "")
    return source


def transform_ta_wiki_rc_links(source: str) -> str:
    """
    Transform the translation academy rc wikilink into source anchor link
    pointing to a destination anchor link for the translation academy
    reference.
    """
    # FIXME When TA gets implemented we'll need to actually build
    # the anchor link.
    for match in finditer(TA_WIKI_RC_LINK_RE, source):
        # For now, remove match text the source text.
        source = source.replace(match.group(0), "")
    return source


def transform_ta_star_rc_links(source: str) -> str:
    """
    Transform the translation academy rc wikilink into source anchor link
    pointing to a destination anchor link for the translation academy
    reference.
    """
    # FIXME When TA gets implemented we'll need to actually build
    # the anchor link.
    for match in finditer(TA_STAR_RC_LINK_RE, source):
        # For now, remove match text the source text.
        source = source.replace(match.group(0), "")
    return source


def transform_ta_markdown_links(source: str) -> str:
    """
    Transform the translation academy markdown link into source anchor link
    pointing to a destination anchor link for the translation
    academy reference.
    """
    # FIXME When TA gets implemented we'll need to actually build
    # the anchor link.
    for match in finditer(TA_PREFIXED_MARKDOWN_LINK_RE, source):
        # For now, remove match text the source text.
        source = source.replace(match.group(0), "")
    return source


def transform_ta_prefixed_markdown_https_links(source: str) -> str:
    """
    Transform the translation academy markdown link into source anchor link
    pointing to a destination anchor link for the translation
    academy reference.
    """
    # FIXME When TA gets implemented we'll need to actually build
    # the anchor link.
    for match in finditer(TA_PREFIXED_MARKDOWN_HTTPS_LINK_RE, source):
        # For now, remove match text the source text.
        source = source.replace(match.group(0), "")
    return source


def transform_ta_markdown_https_links(source: str) -> str:
    """
    Transform the translation academy markdown link into source anchor link
    pointing to a destination anchor link for the translation
    academy reference.
    """
    # FIXME When TA gets implemented we'll need to actually build
    # the anchor link.
    for match in finditer(TA_MARKDOWN_HTTPS_LINK_RE, source):
        # For now, remove match text the source text.
        source = source.replace(match.group(0), "")
    return source


def transform_tn_prefixed_markdown_links(
    source: str,
    resource_requests: Sequence[ResourceRequest],
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    tn: str = "tn",
    fmt_str: str = settings.TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR,
) -> str:
    """
    Transform the translation note rc link into a link pointing to
    the anchor link for the translation note for chapter verse
    reference.
    """
    tn_resource_requests: list[ResourceRequest]
    tn_resource_request: ResourceRequest
    for match in finditer(TN_MARKDOWN_SCRIPTURE_LINK_RE, source):
        scripture_ref = match.group("scripture_ref")
        lang_code = match.group("lang_code")
        book_code = match.group("book_code")
        chapter_num = match.group("chapter_num")
        verse_ref = match.group("verse_ref")
        # NOTE(id:check_for_resource_request) To bother getting the TN resource
        # asset file referenced in the matched link we must know that said TN
        # resource identified by the lang_code/resource_type/book_code combo
        # in the link has been requested by the user in the DocumentRequest.
        tn_resource_requests = [
            resource_request
            for resource_request in resource_requests
            if resource_request.lang_code == lang_code
            and tn in resource_request.resource_type
            and resource_request.book_code == book_code
        ]
        if tn_resource_requests:
            tn_resource_request = tn_resource_requests[0]
            # Build a file path to the TN note being requested.
            first_resource_path_segment = "{}_{}".format(
                tn_resource_request.lang_code,
                tn_resource_request.resource_type,
            )
            second_resource_path_segment = "{}_tn".format(tn_resource_request.lang_code)
            path = "{}.md".format(
                join(
                    working_dir,
                    first_resource_path_segment,
                    second_resource_path_segment,
                    book_code,
                    chapter_num,
                    verse_ref,
                )
            )
            if exists(path):  # file path to TN note exists
                # Create anchor link to translation note
                new_link = fmt_str.format(
                    scripture_ref,
                    tn_resource_request.lang_code,
                    BOOK_NUMBERS[tn_resource_request.book_code].zfill(3),
                    chapter_num.zfill(3),
                    verse_ref.zfill(3),
                )
                # Replace the match text with the new anchor link
                source = source.replace(
                    match.group(0),  # The whole match
                    "({})".format(new_link),
                )
            else:  # TN note file does not exist.
                # Replace link with link text only.
                source = source.replace(match.group(0), scripture_ref)
        else:  # TN resource that link requested was not included as part of the DocumentRequest
            # Replace link with link text only.
            source = source.replace(match.group(0), scripture_ref)
    return source


def transform_tn_markdown_links(
    source: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
    tn: str = "tn",
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    fmt_str: str = settings.TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR,
) -> str:
    """
    Transform the translation note rc link into a link pointing to
    the anchor link for the translation note for chapter verse
    reference.
    """
    matching_resource_requests: list[ResourceRequest]
    matching_resource_request: ResourceRequest
    for match in finditer(TN_MARKDOWN_RELATIVE_SCRIPTURE_LINK_RE, source):
        scripture_ref = match.group("scripture_ref")
        book_code = match.group("book_code")
        chapter_num = match.group("chapter_num")
        verse_ref = match.group("verse_ref")
        # NOTE See id:check_for_resource_request above
        matching_resource_requests = [
            resource_request
            for resource_request in resource_requests
            if resource_request.lang_code == lang_code
            and tn in resource_request.resource_type
            and resource_request.book_code == book_code
        ]
        if matching_resource_requests:
            matching_resource_request = matching_resource_requests[0]
            # Build a file path to the TN note being requested.
            first_resource_path_segment = "{}_{}".format(
                matching_resource_request.lang_code,
                matching_resource_request.resource_type,
            )
            second_resource_path_segment = "{}_{}".format(
                matching_resource_request.lang_code, tn
            )
            path = "{}.md".format(
                join(
                    working_dir,
                    first_resource_path_segment,
                    second_resource_path_segment,
                    book_code,
                    chapter_num,
                    verse_ref,
                )
            )
            if exists(path):  # file path to TN note exists
                # Create anchor link to translation note
                new_link = fmt_str.format(
                    scripture_ref,
                    lang_code,
                    BOOK_NUMBERS[book_code].zfill(3),
                    chapter_num.zfill(3),
                    verse_ref.zfill(3),
                )
                # Replace the match text with the new anchor link
                source = source.replace(
                    match.group(0),  # The whole match
                    "({})".format(new_link),
                )
            else:  # TN note file does not exist.
                # Replace match text from the source text with the
                # link text only so that is not clickable.
                # The whole match plus surrounding parenthesis
                source = source.replace("({})".format(match.group(0)), scripture_ref)
        else:  # TN resource that link requested was not included as part of the
            # DocumentRequest Replace match text from the source text with the link
            # text only so that is not clickable.
            # The whole match plus surrounding parenthesis
            source = source.replace("({})".format(match.group(0)), scripture_ref)
    return source


def transform_tn_missing_book_code_markdown_links(
    source: str,
    lang_code: str,
    resource_requests: Sequence[ResourceRequest],
    tn: str = "tn",
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    fmt_str: str = settings.TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR,
) -> str:
    """
    Transform the translation note rc link into a link pointing to
    the anchor link for the translation note for chapter verse
    reference.
    """
    matching_resource_requests: list[ResourceRequest]
    matching_resource_request: ResourceRequest
    for match in finditer(
        TN_MARKDOWN_RELATIVE_TO_CURRENT_BOOK_SCRIPTURE_LINK_RE, source
    ):
        scripture_ref = match.group("scripture_ref")
        chapter_num = match.group("chapter_num")
        verse_ref = match.group("verse_ref")
        matching_resource_requests = [
            resource_request
            for resource_request in resource_requests
            if resource_request.lang_code == lang_code
            and tn in resource_request.resource_type
        ]
        book_code = ""
        if matching_resource_requests:
            matching_resource_request = matching_resource_requests[0]
            book_code = matching_resource_request.book_code
            # Build a file path to the TN note being requested.
            first_resource_path_segment = "{}_{}".format(
                matching_resource_request.lang_code,
                matching_resource_request.resource_type,
            )
            second_resource_path_segment = "{}_{}".format(
                matching_resource_request.lang_code, tn
            )
            path = "{}.md".format(
                join(
                    working_dir,
                    first_resource_path_segment,
                    second_resource_path_segment,
                    book_code,
                    chapter_num,
                    verse_ref,
                )
            )
            if exists(path):  # file path to TN note exists
                # Create anchor link to translation note
                new_link = fmt_str.format(
                    scripture_ref,
                    lang_code,
                    BOOK_NUMBERS[book_code].zfill(3),
                    chapter_num.zfill(3),
                    verse_ref.zfill(3),
                )
                # Replace the match text with the new anchor link
                source = source.replace(
                    match.group(0),  # The whole match
                    "({})".format(new_link),
                )
            else:  # TN note file does not exist.
                # Replace match text from the source text with the
                # link text only so that is not clickable.
                # The whole match plus surrounding parenthesis
                source = source.replace("({})".format(match.group(0)), scripture_ref)
        else:  # TN resource that link requested was not included as part of the
            # DocumentRequest Replace match text from the source text with the link
            # text only so that is not clickable.
            # The whole match plus surrounding parenthesis
            source = source.replace("({})".format(match.group(0)), scripture_ref)
    return source


def transform_tn_missing_book_code_markdown_links_no_paren(
    source: str,
    # tn: str = "tn",
    # working_dir: str = settings.RESOURCE_ASSETS_DIR,
) -> str:
    """
    Transform the translation note rc link into a non-linked scripture reference only.
    """
    # matching_resource_requests: list[ResourceRequest]
    # matching_resource_request: ResourceRequest
    # resource_requests = self._resource_requests
    # lang_code = self._lang_code
    for match in finditer(
        TN_MARKDOWN_RELATIVE_TO_CURRENT_BOOK_SCRIPTURE_LINK_RE_NO_PARENS, source
    ):
        scripture_ref = match.group("scripture_ref")
        # chapter_num = match.group("chapter_num")
        # verse_ref = match.group("verse_ref")
        # matching_resource_requests = [
        #     resource_request
        #     for resource_request in resource_requests
        #     if resource_request.lang_code == lang_code
        #     and tn in resource_request.resource_type
        # ]
        # book_code = ""
        # if matching_resource_requests:
        #     matching_resource_request = matching_resource_requests[0]
        #     book_code = matching_resource_request.book_code
        #     # Build a file path to the TN note being requested.
        #     first_resource_path_segment = "{}_{}".format(
        #         matching_resource_request.lang_code,
        #         matching_resource_request.resource_type,
        #     )
        #     second_resource_path_segment = "{}_{}".format(
        #         matching_resource_request.lang_code, tn
        #     )
        #     path = "{}.md".format(
        #         join(
        #             working_dir,
        #             first_resource_path_segment,
        #             second_resource_path_segment,
        #             book_code,
        #             chapter_num,
        #             verse_ref,
        #         )
        #     )
        #     if exists(path):  # file path to TN note exists
        #         # Create anchor link to translation note
        #         new_link = settings.TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR.format(
        #             scripture_ref,
        #             lang_code,
        #             BOOK_NUMBERS[book_code].zfill(3),
        #             chapter_num.zfill(3),
        #             verse_ref.zfill(3),
        #         )
        #         # Replace the match text with the new anchor link
        #         source = source.replace(
        #             match.group(0),  # The whole match
        #             "{}".format(new_link),
        #         )
        #     else:  # TN note file does not exist.
        #         # Replace match text from the source text with the
        #         # link text only so that is not clickable.
        #         # The whole match plus surrounding parenthesis
        #         source = source.replace("{}".format(match.group(0)), scripture_ref)
        # else:  # TN resource that link requested was not included as part of the
        #   source = source.replace("{}".format(match.group(0)), scripture_ref)
        source = source.replace("{}".format(match.group(0)), scripture_ref)
    return source


def transform_tn_obs_markdown_links(source: str) -> str:
    """
    Until OBS is supported, replace OBS TN link with just its link
    text.
    """
    for match in finditer(TN_OBS_MARKDOWN_LINK_RE, source):
        # Build the anchor links
        # FIXME Actually create a meaningful link rather than just
        # link text
        source = source.replace(match.group(0), match.group("link_text"))
    return source


def wiki_link_parser(source: str) -> list[WikiLink]:
    """Return a list of all Wiki links in source."""
    links = [
        WikiLink(
            url=link.group("url"),
        )
        for link in finditer(WIKI_LINK_RE, source)
    ]
    return links
