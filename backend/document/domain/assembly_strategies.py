"""
This module provides the assembly strategies and sub-strategies,
otherwise known as layouts, that are used to assemble HTML documents
prior to their conversion to PDF form.


Currently, there are two levels of assembly strategies: one higher,
chosen by assembly strategy, and one lower, chosen by assembly layout.
These two levels of assembly strategies work together in the following
way: the higher level constrains the assembly algorithm by some
criteria, e.g., group content by language and then by book, and then
the lower level further organizes the assembly within those
constraints, e.g., by superimposing an order to when resource's are
interleaved thus affecting the structural layout of the content. It is
possible to have both multiple higher level, so-called 'assembly
strategies' and lower level, so-called 'layout', assembly strategies.

Architecturally, assembly strategies utilize the Strategy pattern:
https://github.com/faif/python-patterns/blob/master/patterns/behavioral/strategy.py
"""

from itertools import chain, groupby, zip_longest
from re import escape, search, sub
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

from document.config import settings
from document.domain.bible_books import BOOK_NAMES, BOOK_NUMBERS
from document.domain.model import (
    AssemblyLayoutEnum,
    AssemblyStrategyEnum,
    BCBook,
    BookContent,
    HtmlContent,
    TNBook,
    TQBook,
    TWBook,
    TWNameContentPair,
    TWUse,
    USFMBook,
)
from document.utils.number_utils import is_even
from document.utils.tw_utils import uniq

logger = settings.logger(__name__)

H1, H2, H3, H4, H5, H6 = "h1", "h2", "h3", "h4", "h5", "h6"
NUM_ZEROS = 3


def assembly_strategy_factory(
    assembly_strategy_kind: AssemblyStrategyEnum,
) -> Any:
    """
    Strategy pattern. Given an assembly_strategy_kind, returns the
    appropriate strategy function to run.
    """
    strategies = {
        AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER: assemble_content_by_lang_then_book,
        AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER: assemble_content_by_book_then_lang,
    }
    return strategies[assembly_strategy_kind]


def book_content_unit_resource_code(book_content_unit: BookContent) -> str:
    return book_content_unit.resource_code


def book_content_unit_lang_name(book_content_unit: BookContent) -> str:
    return book_content_unit.lang_name


def assemble_content_by_lang_then_book(
    book_content_units: Iterable[BookContent],
    assembly_layout_kind: AssemblyLayoutEnum,
    language_fmt_str: str = settings.LANGUAGE_FMT_STR,
    book_fmt_str: str = settings.BOOK_FMT_STR,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> Iterable[str]:
    """
    Assemble by language then by book in lexicographical order before
    delegating more atomic ordering/interleaving to an assembly
    sub-strategy.
    """

    ldebug = logger.debug

    book_units_sorted_by_language = sorted(
        book_content_units,
        key=lambda book_content_unit: book_content_unit.lang_name,
    )
    language: str

    usfm_book_content_unit: Optional[USFMBook]
    tn_book_content_unit_: Optional[TNBook]
    tq_book_content_unit_: Optional[TQBook]
    tw_book_content_unit_: Optional[TWBook]
    usfm_book_content_unit2: Optional[USFMBook]
    bc_book_content_unit_: Optional[BCBook]

    book_id_map = dict((id, pos) for pos, id in enumerate(BOOK_NAMES.keys()))

    for language, group_by_lang in groupby(
        book_units_sorted_by_language,
        book_content_unit_lang_name,
    ):
        yield language_fmt_str.format(language)

        # Sort the books in canonical order for groupby's sake.
        book_content_units_sorted_by_book = sorted(
            group_by_lang,
            key=lambda book_content_unit: book_id_map[book_content_unit.resource_code],
        )
        for book, book_content_units_grouped_by_book in groupby(
            book_content_units_sorted_by_book,
            book_content_unit_resource_code,
        ):
            yield book_fmt_str.format(book_names[book])

            # Save grouper generator values in list since it will get exhausted
            # when first used and exhausted generators cannot be reused.
            book_content_units_ = list(book_content_units_grouped_by_book)
            usfm_book_content_unit = first_usfm_book_content_unit(book_content_units_)
            tn_book_content_unit_ = tn_book_content_unit(book_content_units_)
            tq_book_content_unit_ = tq_book_content_unit(book_content_units_)
            tw_book_content_unit_ = tw_book_content_unit(book_content_units_)
            usfm_book_content_unit2 = second_usfm_book_content_unit(book_content_units_)
            bc_book_content_unit_ = bc_book_content_unit(book_content_units_)

            # We've got the resources, now we can use the sub-strategy factory
            # method to choose the right function to use from here on out.
            assembly_layout_strategy = assembly_factory_for_lang_then_book_strategy(
                usfm_book_content_unit,
                tn_book_content_unit_,
                tq_book_content_unit_,
                tw_book_content_unit_,
                usfm_book_content_unit2,
                bc_book_content_unit_,
                assembly_layout_kind,
            )

            ldebug("assembly_layout_strategy: %s", str(assembly_layout_strategy))

            # Now that we have the sub-strategy, let's run it and
            # generate the HTML output.
            yield from assembly_layout_strategy(
                usfm_book_content_unit,
                tn_book_content_unit_,
                tq_book_content_unit_,
                tw_book_content_unit_,
                usfm_book_content_unit2,
                bc_book_content_unit_,
            )


def assembly_factory_for_lang_then_book_strategy(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    assembly_layout_kind: AssemblyLayoutEnum,
) -> Callable[
    [
        Optional[USFMBook],
        Optional[TNBook],
        Optional[TQBook],
        Optional[TWBook],
        Optional[USFMBook],
        Optional[BCBook],
    ],
    Iterable[HtmlContent],
]:
    """
    Strategy pattern. Given the existence, i.e., exists or None, of each
    type of the possible resource instances (i.e., the resource parameters
    above) and an assembly layout kind, returns the appropriate
    layout/assembly function to run.

    This functions as a lookup table that will select the right
    assembly function to run. The impetus for it is to avoid messy
    conditional logic in an otherwise monolithic assembly algorithm
    that would be checking the existence of each resource.
    This makes adding new strategies straightforward, if a bit
    redundant. The redundancy is the cost for comprehension.
    """
    strategies: Mapping[
        tuple[
            bool,  # usfm_book_content_unit_exists
            bool,  # tn_book_content_unit_exists
            bool,  # tq_book_content_unit_exists
            bool,  # tw_book_content_unit_exists
            bool,  # usfm_book_content_unit2_exists
            bool,  # bc_book_content_unit_exists
            AssemblyLayoutEnum,  # assembly_layout_kind
        ],
        Callable[
            [
                Optional[USFMBook],
                Optional[TNBook],
                Optional[TQBook],
                Optional[TWBook],
                Optional[USFMBook],
                Optional[BCBook],
            ],
            Iterable[HtmlContent],
        ],
    ] = {  # This is a big truth/dispatch table that ensures every case is handled explicitly.
        (
            True,
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            False,
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            False,
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            False,
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            False,
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_tq_tw_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_tq_tw_for_lang_then_book_1c_c,
        (
            True,
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_tw_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_tw_for_lang_then_book_1c_c,
        (
            True,
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_tq_for_lang_then_book_1c,
        (
            True,
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_tq_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            True,
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            False,
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_lang_then_book_1c_c,
        (
            False,
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_lang_then_book_1c_c,
        (
            False,
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_lang_then_book_1c,
        (
            False,
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_lang_then_book_1c,
        (
            False,
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_lang_then_book_1c_c,
        (
            False,
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_lang_then_book_1c_c,
        (
            False,
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_lang_then_book_1c,
        (
            False,
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_lang_then_book_1c_c,
        (
            False,
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_lang_then_book_1c_c,
        (
            False,
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tq_tw_for_lang_then_book_1c,
        (
            False,
            False,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tq_tw_for_lang_then_book_1c,
        (
            False,
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tq_tw_for_lang_then_book_1c_c,
        (
            False,
            False,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tq_tw_for_lang_then_book_1c_c,
        (
            False,
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tw_as_iterator_for_lang_then_book,
        (
            False,
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tw_as_iterator_for_lang_then_book,
        (
            False,
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tq_as_iterator_for_lang_then_book,
        (
            False,
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tq_as_iterator_for_lang_then_book,
        (
            True,
            False,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c,
        (
            True,
            False,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_by_usfm_as_iterator_for_lang_then_book_1c_c,
        (
            False,
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_lang_then_book_1c,
        (
            False,
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_lang_then_book_1c_c,
    }
    # logger.debug(
    #     "usfm_book_content_unit is not None: %s", usfm_book_content_unit is not None
    # )
    # logger.debug(
    #     "tn_book_content_unit is not None: %s", tn_book_content_unit is not None
    # )
    # logger.debug(
    #     "tq_book_content_unit is not None: %s", tq_book_content_unit is not None
    # )
    # logger.debug(
    #     "tw_book_content_unit is not None: %s", tw_book_content_unit is not None
    # )
    # logger.debug(
    #     "usfm_book_content_unit2 is not None: %s", usfm_book_content_unit2 is not None
    # )
    return strategies[
        (
            # Turn existence (exists or not) into a boolean for each instance, the
            # tuple of these together are an immutable, and thus hashable,
            # dictionary key into our function lookup/dispatch table.
            usfm_book_content_unit is not None,
            tn_book_content_unit is not None,
            tq_book_content_unit is not None,
            tw_book_content_unit is not None,
            usfm_book_content_unit2 is not None,
            bc_book_content_unit is not None,
            assembly_layout_kind,
        )
    ]


def assemble_content_by_book_then_lang(
    book_content_units: Iterable[BookContent],
    assembly_layout_kind: AssemblyLayoutEnum,
    book_as_grouper_fmt_str: str = settings.BOOK_AS_GROUPER_FMT_STR,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> Iterable[str]:
    """
    Assemble by book then by language in alphabetic order before
    delegating more atomic ordering/interleaving to an assembly
    sub-strategy.
    """

    ldebug = logger.debug

    # Sort the books in canonical order.
    book_id_map = dict((id, pos) for pos, id in enumerate(BOOK_NAMES.keys()))
    book_content_units_sorted_by_book = sorted(
        book_content_units,
        key=lambda book_content_unit: book_id_map[book_content_unit.resource_code],
    )
    book: str
    usfm_book_content_units: Sequence[USFMBook]
    for book, group_by_book in groupby(
        book_content_units_sorted_by_book,
        book_content_unit_resource_code,
    ):
        yield book_as_grouper_fmt_str.format(book_names[book])

        # Save grouper generator values in list since it will get exhausted
        # when used and exhausted generators cannot be reused.
        book_content_units_grouped_by_book = list(group_by_book)
        usfm_book_content_units = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, USFMBook)
        ]
        tn_book_content_units: Sequence[TNBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, TNBook)
        ]
        tq_book_content_units: Sequence[TQBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, TQBook)
        ]
        tw_book_content_units: Sequence[TWBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, TWBook)
        ]
        bc_book_content_units: Sequence[BCBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, BCBook)
        ]

        # We've got the resources, now we can use the layout factory
        # function to choose the right function to use from here on out.
        assembly_layout_for_book_then_lang_strategy = (
            assembly_factory_for_book_then_lang_strategy(
                usfm_book_content_units,
                tn_book_content_units,
                tq_book_content_units,
                tw_book_content_units,
                bc_book_content_units,
                assembly_layout_kind,
            )
        )

        ldebug(
            "assembly_layout_for_book_then_lang_strategy: %s",
            str(assembly_layout_for_book_then_lang_strategy),
        )

        # Now that we have the sub-strategy, let's run it and
        # generate the HTML output.
        yield from assembly_layout_for_book_then_lang_strategy(
            usfm_book_content_units,
            tn_book_content_units,
            tq_book_content_units,
            tw_book_content_units,
            bc_book_content_units,
        )


def assembly_factory_for_book_then_lang_strategy(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    assembly_layout_kind: AssemblyLayoutEnum,
) -> Callable[
    [
        Sequence[USFMBook],
        Sequence[TNBook],
        Sequence[TQBook],
        Sequence[TWBook],
        Sequence[BCBook],
    ],
    Iterable[HtmlContent],
]:
    """
    Strategy pattern. Given the existence, i.e., exists or empty, of each
    type of the possible resource instances and an
    assembly layout kind, returns the appropriate layout
    function to run.

    This functions as a lookup table that will select the right
    assembly function to run. The impetus for it is to avoid messy
    conditional logic in an otherwise monolithic assembly algorithm
    that would be checking the existence of each resource.
    This makes adding new strategies straightforward, if a bit
    redundant. The redundancy is the cost for comprehension.
    """
    strategies: Mapping[
        tuple[
            bool,  # usfm_book_content_units is non-empty
            bool,  # tn_book_content_units is non-empty
            bool,  # tq_book_content_units is non-empty
            bool,  # tw_book_content_units is non-empty
            bool,  # bc_book_content_units is non-empty
            AssemblyLayoutEnum,  # assembly_layout_kind
        ],
        Callable[
            [
                Sequence[USFMBook],
                Sequence[TNBook],
                Sequence[TQBook],
                Sequence[TWBook],
                Sequence[BCBook],
            ],
            Iterable[HtmlContent],
        ],
    ] = {
        (
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.TWO_COLUMN_SCRIPTURE_LEFT_SCRIPTURE_RIGHT_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr,
        (
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c,
        (
            True,
            False,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            True,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_usfm_as_iterator_for_book_then_lang_1c_c,
        (
            False,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_book_then_lang,
        (
            False,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_book_then_lang,
        (
            False,
            True,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_book_then_lang_c,
        (
            False,
            True,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_book_then_lang_c,
        (
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_book_then_lang,
        (
            False,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_book_then_lang,
        (
            False,
            True,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_book_then_lang_c,
        (
            False,
            True,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_book_then_lang_c,
        (
            False,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_book_then_lang,
        (
            False,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_book_then_lang,
        (
            False,
            True,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_book_then_lang_c,
        (
            False,
            True,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_book_then_lang_c,
        (
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_book_then_lang,
        (
            False,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tn_as_iterator_for_book_then_lang,
        (
            False,
            True,
            False,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_book_then_lang_c,
        (
            False,
            True,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tn_as_iterator_for_book_then_lang_c,
        (
            False,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tq_as_iterator_for_book_then_lang,
        (
            False,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tq_as_iterator_for_book_then_lang,
        (
            False,
            False,
            True,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tq_as_iterator_for_book_then_lang_c,
        (
            False,
            False,
            True,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tq_as_iterator_for_book_then_lang_c,
        (
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tq_as_iterator_for_book_then_lang,
        (
            False,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tq_as_iterator_for_book_then_lang,
        (
            False,
            False,
            True,
            False,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tq_as_iterator_for_book_then_lang_c,
        (
            False,
            False,
            True,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tq_as_iterator_for_book_then_lang_c,
        (
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tw_as_iterator_for_book_then_lang,
        (
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tw_as_iterator_for_book_then_lang,
        (
            False,
            False,
            False,
            True,
            False,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tw_as_iterator_for_book_then_lang,
        (
            False,
            False,
            False,
            True,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tw_as_iterator_for_book_then_lang,
        (
            False,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN,
        ): assemble_tw_as_iterator_for_book_then_lang,
        (
            False,
            False,
            False,
            False,
            True,
            AssemblyLayoutEnum.ONE_COLUMN_COMPACT,
        ): assemble_tw_as_iterator_for_book_then_lang,
    }
    return strategies[
        # Turn existence (exists or not) into a boolean for each
        # instance, the tuple of these together are an immutable,
        # and hashable dictionary key into our function lookup table.
        (
            True if usfm_book_content_units else False,
            True if tn_book_content_units else False,
            True if tq_book_content_units else False,
            True if tw_book_content_units else False,
            True if bc_book_content_units else False,
            assembly_layout_kind,
        )
    ]


#########################################################################
# Assembly sub-strategy implementations for language then book strategy
#
# Possible combinations with usfm (e.g., ulb, ulb-wa, cuv, nav, etc), tn,
# tq, tw, usfm2 (e.g., udb) expressed as a truth table to make sure no
# cases are missed:
#
#
#  | usfm | tn | tq | tw | usfm2 | combination as string | complete | test      | comment    |
#  |------+----+----+----+-------+-----------------------+----------+-----------+------------|
#  |    0 |  0 |  0 |  0 |     1 | usfm2                 | y        | y         | See note * |
#  |    0 |  0 |  0 |  1 |     0 | tw                    | y        | y         |            |
#  |    0 |  0 |  0 |  1 |     1 | tw,usfm2              | y        | y         | See note * |
#  |    0 |  0 |  1 |  0 |     0 | tq                    | y        | y         |            |
#  |    0 |  0 |  1 |  0 |     1 | tq,usfm2              | y        | y         | See note * |
#  |    0 |  0 |  1 |  1 |     0 | tq,tw                 | y        | y         |            |
#  |    0 |  0 |  1 |  1 |     1 | tq,tw,usfm2           | y        | y         | See note * |
#  |    0 |  1 |  0 |  0 |     0 | tn                    | y        | y         |            |
#  |    0 |  1 |  0 |  0 |     1 | tn,usfm2              | y        | y         | See note * |
#  |    0 |  1 |  0 |  1 |     0 | tn,tw                 | y        | y         |            |
#  |    0 |  1 |  0 |  1 |     1 | tn,tw,usfm2           | y        | y         | See note * |
#  |    0 |  1 |  1 |  0 |     0 | tn,tq                 | y        | y         |            |
#  |    0 |  1 |  1 |  0 |     1 | tn,tq,usfm2           | y        | y         | See note * |
#  |    0 |  1 |  1 |  1 |     0 | tn,tq,tw              | y        | y         |            |
#  |    0 |  1 |  1 |  1 |     1 | tn,tq,tw,usfm2        | y        | y         | See note * |
#  |    1 |  0 |  0 |  0 |     0 | usfm                  | y        | y         |            |
#  |    1 |  0 |  0 |  0 |     1 | usfm,usfm2            | y        | y         |            |
#  |    1 |  0 |  0 |  1 |     0 | usfm,tw               | y        | y         |            |
#  |    1 |  0 |  0 |  1 |     1 | usfm,tw,usfm2         | y        | y         |            |
#  |    1 |  0 |  1 |  0 |     0 | usfm,tq               | y        | y         |            |
#  |    1 |  0 |  1 |  0 |     1 | usfm,tq,usfm2         | y        | y         |            |
#  |    1 |  0 |  1 |  1 |     0 | usfm,tq,tw            | y        | y         |            |
#  |    1 |  0 |  1 |  1 |     1 | usfm,tq,tw,usfm2      | y        | y         |            |
#  |    1 |  1 |  0 |  0 |     0 | usfm,tn               | y        | y         |            |
#  |    1 |  1 |  0 |  0 |     1 | usfm,tn,usfm2         | y        | y         |            |
#  |    1 |  1 |  0 |  1 |     0 | usfm,tn,tw            | y        | y         |            |
#  |    1 |  1 |  0 |  1 |     1 | usfm,tn,tw,usfm2      | y        | y         |            |
#  |    1 |  1 |  1 |  0 |     0 | usfm,tn,tq            | y        | y         |            |
#  |    1 |  1 |  1 |  0 |     1 | usfm,tn,tq,usfm2      | y        | y         |            |
#  |    1 |  1 |  1 |  1 |     0 | usfm,tn,tq,tw         | y        | y         |            |
#  |    1 |  1 |  1 |  1 |     1 | usfm,tn,tq,tw,usfm2   | y        | y         |            |
#
# Note *:
#
# If there is only one USFM resource requested then the assembly
# strategy algo puts that USFM resource in usfm_book_content_unit
# position rather than usfm_book_content_unit2 position. If two USFM
# resources are requested then the second one in the DocumentRequest
# gets put in usfm_book_content_unit2 position. Only the first USFM
# resource in the DocumentRequest has any subsequent TN, TQ, and TW. A
# second USFMResource, e.g., udb, stands alone without referencing
# resources. This seems to work out fine in practice, but may be changed
# later by forcing usfm_book_content_unit to be of a particular
# resource_type, e.g., ulb, cuv, nav, and usfm_book_content_unit2 to be
# of another, e.g., udb.
#


def tn_book_intro(tn_book_content_unit: TNBook) -> Iterable[HtmlContent]:
    "Yield the book intro for the TNBook given."
    book_intro = tn_book_content_unit.intro_html
    book_intro = adjust_book_intro_headings(book_intro)
    yield HtmlContent(book_intro)


def assemble_by_usfm_as_iterator_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML wherein at least one USFM resource (e.g., ulb,
    nav, cuv, etc.) exists, and TN, TQ, TW, and a second USFM (e.g.,
    probably always udb) may exist. If only one USFM exists then it will
    be used as the first USFM resource even if it is of udb resource type.
    Non-USFM resources, e.g., TN, TQ, and TW will reference (and link
    where applicable) the first USFM resource. The second USFM resource is
    displayed last in this interleaving strategy.
    """

    if tn_book_content_unit:
        yield from tn_book_intro(tn_book_content_unit)

    if bc_book_content_unit:
        yield book_intro_commentary(bc_book_content_unit)

    if usfm_book_content_unit:

        tn_verses: Optional[dict[str, HtmlContent]]
        tq_verses: Optional[dict[str, HtmlContent]]
        verse_num: str
        verse: HtmlContent
        for (
            chapter_num,
            chapter,
        ) in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading
            tn_verses = None
            tq_verses = None
            if tn_book_content_unit:
                # Add the translation notes chapter intro.
                yield chapter_intro(tn_book_content_unit, chapter_num)
                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            if bc_book_content_unit:
                yield chapter_commentary(bc_book_content_unit, chapter_num)
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():

                # Add scripture verse
                yield verse

                if usfm_book_content_unit2:
                    # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
                    # Add scripture verse
                    if (
                        chapter_num in usfm_book_content_unit2.chapters
                        and verse_num
                        in usfm_book_content_unit2.chapters[chapter_num].verses
                    ):
                        verse_ = usfm_book_content_unit2.chapters[chapter_num].verses[
                            verse_num
                        ]
                        yield verse_

                # Add TN verse content, if any
                if (
                    tn_book_content_unit
                    and tn_verses is not None
                    and tn_verses
                    and verse_num in tn_verses
                ):
                    yield from format_tn_verse(
                        tn_book_content_unit,
                        chapter_num,
                        verse_num,
                        tn_verses[verse_num],
                    )
                # Add TQ verse content, if any
                if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )

                if tw_book_content_unit:
                    # Add the translation words links section.
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        verse,
                    )

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes

    if not usfm_book_content_unit and usfm_book_content_unit2:
        # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
        for (
            chapter_num_,
            chapter_,
        ) in usfm_book_content_unit2.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter_.content[0]
            yield chapter_heading
            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter_.verses.items():
                # Add scripture verse
                yield verse


def assemble_by_usfm_as_iterator_for_lang_then_book_1c_c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML wherein at least one USFM resource (e.g., ulb,
    nav, cuv, etc.) exists, and TN, TQ, TW, and a second USFM (e.g.,
    probably always udb) may exist. If only one USFM exists then it will
    be used as the first USFM resource even if it is of udb resource type.
    Non-USFM resources, e.g., TN, TQ, and TW will reference (and link
    where applicable) the first USFM resource. The second USFM resource is
    displayed last in this interleaving strategy.
    """

    if tn_book_content_unit:
        yield from tn_book_intro(tn_book_content_unit)

    if bc_book_content_unit:
        yield book_intro_commentary(bc_book_content_unit)

    if usfm_book_content_unit:
        tn_verses: Optional[dict[str, HtmlContent]]
        tq_verses: Optional[dict[str, HtmlContent]]
        verse_num: str
        verse: HtmlContent
        for (
            chapter_num,
            chapter,
        ) in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading
            tn_verses = None
            tq_verses = None
            if tn_book_content_unit:
                # Add the translation notes chapter intro.
                yield chapter_intro(tn_book_content_unit, chapter_num)

                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            if bc_book_content_unit:
                yield chapter_commentary(bc_book_content_unit, chapter_num)
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                if usfm_book_content_unit2:
                    # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
                    # Add scripture verse
                    if (
                        chapter_num in usfm_book_content_unit2.chapters
                        and verse_num
                        in usfm_book_content_unit2.chapters[chapter_num].verses
                    ):
                        verse_ = usfm_book_content_unit2.chapters[chapter_num].verses[
                            verse_num
                        ]
                        yield verse_

                # Add TN verse content, if any
                if (
                    tn_book_content_unit
                    and tn_verses is not None
                    and tn_verses
                    and verse_num in tn_verses
                ):
                    yield from format_tn_verse(
                        tn_book_content_unit,
                        chapter_num,
                        verse_num,
                        tn_verses[verse_num],
                    )
                # Add TQ verse content, if any
                if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes

    if not usfm_book_content_unit and usfm_book_content_unit2:
        # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
        for (
            chapter_num_,
            chapter_,
        ) in usfm_book_content_unit2.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter_.content[0]
            yield chapter_heading
            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter_.verses.items():
                # Add scripture verse
                yield verse


def assemble_usfm_tq_tw_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM, TQ,
    and TW exist.
    """

    if usfm_book_content_unit:
        verse_num: str
        verse: HtmlContent
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading

            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                # Add TN verse content, if any
                if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )
                if tw_book_content_unit:
                    # Add the translation words links section
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        verse,
                    )

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes


def assemble_usfm_tq_tw_for_lang_then_book_1c_c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM, TQ,
    and TW exist.
    """

    if usfm_book_content_unit:
        verse_num: str
        verse: HtmlContent
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading

            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                # Add TN verse content, if any
                if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes


def assemble_usfm_tw_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM and TW
    exist.
    """

    if usfm_book_content_unit:
        verse_num: str
        verse: HtmlContent
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                if tw_book_content_unit:
                    # Add the translation words links section
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        verse,
                    )

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes


def assemble_usfm_tw_for_lang_then_book_1c_c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM and TW
    exist.
    """

    if usfm_book_content_unit:
        verse_num: str
        verse: HtmlContent
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading

            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes


def assemble_usfm_tq_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """Construct the HTML for a 'by verse' strategy wherein only USFM and TQ exist."""

    if usfm_book_content_unit:

        verse_num: str
        verse: HtmlContent
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = HtmlContent("")
            chapter_heading = chapter.content[0]
            yield chapter_heading

            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's interleave USFM verse with its
            # translation note if available.
            for verse_num, verse in chapter.verses.items():
                # Add scripture verse
                yield verse

                # Add TQ verse content, if any
                if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )

            # Add scripture footnotes if available
            if chapter.footnotes:
                yield footnotes_heading
                yield chapter.footnotes


def book_number(
    resource_code: str,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = NUM_ZEROS,
) -> str:
    return book_numbers[resource_code].zfill(num_zeros)


def assemble_tn_as_iterator_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN, TQ,
    and TW exists.
    """

    verse_num: str
    verse: HtmlContent

    if tn_book_content_unit:
        yield from tn_book_intro(tn_book_content_unit)

        for chapter_num in tn_book_content_unit.chapters:
            # How to get chapter heading for Translation notes when USFM is not
            # requested? For now we'll use non-localized chapter heading. Add in the
            # USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tn_book_content_unit.lang_code,
                    book_number(tn_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit, chapter_num)

            if bc_book_content_unit:
                # Add the chapter commentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)

            tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's get all the verse level content.
            # iterator = tn_verses or tq_verses
            # if iterator:
            if tn_verses:
                for verse_num, verse in tn_verses.items():
                    # Add TN verse content, if any
                    if tn_verses and verse_num in tn_verses:
                        yield from format_tn_verse(
                            tn_book_content_unit,
                            chapter_num,
                            verse_num,
                            tn_verses[verse_num],
                        )

                    # Add TQ verse content, if any
                    if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                        yield from format_tq_verse(
                            tq_book_content_unit.resource_type_name,
                            chapter_num,
                            verse_num,
                            tq_verses[verse_num],
                        )
                    if tw_book_content_unit:
                        # Add the translation words links section.
                        yield from translation_word_links(
                            tw_book_content_unit,
                            chapter_num,
                            verse_num,
                            verse,
                        )


def assemble_tn_as_iterator_for_lang_then_book_1c_c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN, TQ,
    and TW exists.
    """
    if tn_book_content_unit:
        yield from tn_book_intro(tn_book_content_unit)

        verse_num: str
        verse: HtmlContent
        for chapter_num in tn_book_content_unit.chapters:
            # How to get chapter heading for Translation notes when USFM is not
            # requested? For now we'll use non-localized chapter heading. Add in the
            # USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tn_book_content_unit.lang_code,
                    book_number(tn_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit, chapter_num)

            if bc_book_content_unit:
                # Add the chapter commentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)

            tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's get all the verse level content.
            # iterator = tn_verses or tq_verses
            # if iterator:
            if tn_verses:
                for verse_num, verse in tn_verses.items():
                    # Add TN verse content, if any
                    if tn_verses and verse_num in tn_verses:
                        yield from format_tn_verse(
                            tn_book_content_unit,
                            chapter_num,
                            verse_num,
                            tn_verses[verse_num],
                        )

                    # Add TQ verse content, if any
                    if tq_book_content_unit and tq_verses and verse_num in tq_verses:
                        yield from format_tq_verse(
                            tq_book_content_unit.resource_type_name,
                            chapter_num,
                            verse_num,
                            tq_verses[verse_num],
                        )


def assemble_tq_as_iterator_for_lang_then_book(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """Construct the HTML for a 'by verse' strategy wherein only TQ exists."""
    # Make mypy happy. We know, due to how we got here, that book_content_unit objects are not None.

    if tq_book_content_unit:
        verse_num: str
        verse: HtmlContent
        for chapter_num in tq_book_content_unit.chapters:
            if bc_book_content_unit:
                # Add chapter commentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)

            # How to get chapter heading for Translation questions when there is
            # not USFM requested? For now we'll use non-localized chapter heading.
            # Add in the USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tq_book_content_unit.lang_code,
                    book_number(tq_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Get TQ chapter verses
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's get all the verse translation notes available.
            if tq_verses:
                for verse_num, verse in tq_verses.items():
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        verse,
                    )


def assemble_tq_tw_for_lang_then_book_1c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TQ and
    TW exists.
    """

    if tq_book_content_unit:

        verse_num: str
        verse: HtmlContent
        for chapter_num in tq_book_content_unit.chapters:
            if bc_book_content_unit:
                # Add chapter commmentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)
            # How to get chapter heading for Translation questions when there is
            # not USFM requested? For now we'll use non-localized chapter heading.
            # Add in the USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tq_book_content_unit.lang_code,
                    book_number(tq_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Get TQ chapter verses
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's get all the verse translation notes available.
            if tq_verses:
                for verse_num, verse in tq_verses.items():
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        verse,
                    )

                    if tw_book_content_unit:
                        # Add the translation words links section.
                        yield from translation_word_links(
                            tw_book_content_unit,
                            chapter_num,
                            verse_num,
                            verse,
                        )


def assemble_tq_tw_for_lang_then_book_1c_c(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TQ and
    TW exists.
    """

    if tq_book_content_unit:
        verse_num: str
        verse: HtmlContent
        for chapter_num in tq_book_content_unit.chapters:
            if bc_book_content_unit:
                # Add chapter commmentary.
                yield chapter_commentary(bc_book_content_unit, chapter_num)
            # How to get chapter heading for Translation questions when there is
            # not USFM requested? For now we'll use non-localized chapter heading.
            # Add in the USFM chapter heading.
            yield HtmlContent(
                chapter_header_fmt_str.format(
                    tq_book_content_unit.lang_code,
                    book_number(tq_book_content_unit.resource_code),
                    str(chapter_num).zfill(num_zeros),
                    chapter_num,
                )
            )

            # Get TQ chapter verses
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # Now let's get all the verse translation notes available.
            if tq_verses:
                for verse_num, verse in tq_verses.items():
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        verse,
                    )


# FIXME Eventually remove this. When you do you will have to also
# remove its entries from its respective dispatch table.
def assemble_tw_as_iterator_for_lang_then_book(
    usfm_book_content_unit: Optional[USFMBook],
    tn_book_content_unit: Optional[TNBook],
    tq_book_content_unit: Optional[TQBook],
    tw_book_content_unit: Optional[TWBook],
    usfm_book_content_unit2: Optional[USFMBook],
    bc_book_content_unit: Optional[BCBook],
) -> Iterable[HtmlContent]:
    """Construct the HTML for a 'by verse' strategy wherein only TW exists."""
    yield HtmlContent("")


#########################################################################
# Assembly sub-strategy/layout implementations for book then language strategy


def assemble_usfm_as_iterator_for_book_then_lang_2c_sl_sr(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
    html_row_begin: str = settings.HTML_ROW_BEGIN,
    html_column_begin: str = settings.HTML_COLUMN_BEGIN,
    html_column_left_begin: str = settings.HTML_COLUMN_LEFT_BEGIN,
    html_column_right_begin: str = settings.HTML_COLUMN_RIGHT_BEGIN,
    html_column_end: str = settings.HTML_COLUMN_END,
    html_row_end: str = settings.HTML_ROW_END,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for the two column scripture left scripture
    right layout.

    Ensure that different languages' USFMs ends up next to each other
    in the two column layout.

    Discussion:

    First let's find all possible USFM combinations for two languages
    that have both a primary USFM, e.g., ulb-wa, available and a secondary
    USFM, e.g., udb-wa, available for selection:

    primary_lang0, primary_lang1, secondary_lang0, secondary_lang1

    0                 0                0             1
    0                 0                1             0
    0                 0                1             1
    0                 1                0             0
    0                 1                0             1
    0                 1                1             0
    0                 1                1             1
    1                 0                0             0
    1                 0                0             1
    1                 0                1             0
    1                 0                1             1
    1                 1                0             1
    1                 1                1             0
    1                 1                1             1

    of which we can eliminate those that do not have the minimum of
    two languages and eliminate those that do not have USFMs
    for both languages yielding:

    primary_lang0, primary_lang1, secondary_lang0, secondary_lang1

    0                 0                1             1
    0                 1                1             0
    0                 1                1             1
    1                 0                0             1
    1                 0                1             1
    1                 1                0             1
    1                 1                1             0
    1                 1                1             1

    Let's now reorder columns to make the subsequent step easier:

    primary_lang0, secondary_lang0, primary_lang1, secondary_lang1

    0                   1             0              1
    0                   1             1              0
    0                   1             1              1
    1                   0             0              1
    1                   1             0              1
    1                   0             1              1
    1                   1             1              0
    1                   1             1              1

    which yields the following possible USFM layouts when we fix
    that lang0 always appears on the left and lang1 always appears on
    the right of the two column layout:

    secondary_lang0     | secondary_lang1

    or

    secondary_lang0     | primary_lang1

    or

    secondary_lang0     | primary_lang1
                        | secondary_lang1

    or

    primary_lang0       | secondary_lang1

    or

    primary_lang0       | secondary_lang1
    secondary_lang0     |

    or

    primary_lang0       | primary_lang1
                        | secondary_lang1

    or

    primary_lang0       | primary_lang1
    secondary_lang0     |

    or

    primary_lang0       | primary_lang1
    secondary_lang0     | secondary_lang1
    """

    ldebug = logger.debug
    lexception = logger.exception

    tn_verses: Optional[dict[str, HtmlContent]]
    tq_verses: Optional[dict[str, HtmlContent]]
    usfm_book_content_unit_: Optional[USFMBook]

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    tw_book_content_units = sorted(tw_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Order USFM book content units so that they are in language pairs
    # for side by side display.
    zipped_usfm_book_content_units = (
        ensure_primary_usfm_books_for_different_languages_are_adjacent(
            usfm_book_content_units
        )
    )

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        # Add the book intro
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield HtmlContent(book_intro)

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)

    # Use the usfm_book_content_unit that has the most chapters as a
    # chapter_num pump.
    usfm_with_most_chapters = max(
        usfm_book_content_units,
        key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters.keys(),
    )
    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        # Add the first USFM resource's chapter heading. We ignore
        # chapter headings for other usfm_book_content_units because it would
        # be strange to have more than one chapter heading per chapter
        # for this assembly sub-strategy.
        chapter_heading = HtmlContent("")
        chapter_heading = chapter.content[0]
        yield HtmlContent(chapter_heading)

        # Add chapter intro for each language
        for tn_book_content_unit2 in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit2, chapter_num)

        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)

        # Use the usfm_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump.
        # I.e., realize the most amount of content displayed to user.
        # usfm_with_most_verses = max(
        #     usfm_book_content_units,
        #     key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters[
        #         chapter_num
        #     ].verses.keys(),
        # )
        # for verse_num in usfm_with_most_verses.chapters[chapter_num].verses.keys():
        for verse_num in chapter.verses.keys():
            # Get lang_code of first USFM so that we can use it later
            # to make sure USFMs of the same language are on the same
            # side of the two column layout.
            lang0_code = zipped_usfm_book_content_units[0].lang_code
            # Add the interleaved USFM verses
            for idx, usfm_book_content_unit in enumerate(
                zipped_usfm_book_content_units
            ):
                # If the number of non-None USFM book content unit instances
                # The conditions for beginning a row are a simple
                # result of the fact that we can have between 2 and 4
                # non-None USFM content units in the collection one of which
                # could be a None (due to an earlier use of
                # itertools.zip_longest in the call to
                # ensure_primary_usfm_books_for_different_languages_are_adjacent)
                # in the case when there are 3 non-None items, but 4
                # total counting the None.
                if is_even(idx) or idx == 3:
                    yield html_row_begin

                if (
                    usfm_book_content_unit
                    and chapter_num in usfm_book_content_unit.chapters
                    and verse_num in usfm_book_content_unit.chapters[chapter_num].verses
                ):
                    # lang0's USFM content units should always be on the
                    # left and lang1's should always be on the right.
                    if lang0_code == usfm_book_content_unit.lang_code:
                        yield html_column_left_begin
                    else:
                        yield html_column_right_begin

                    # Add scripture verse
                    yield usfm_book_content_unit.chapters[chapter_num].verses[verse_num]
                yield html_column_end
                if not is_even(
                    idx
                ):  # Non-even indexes signal the end of the current row.
                    yield html_row_end

            # Add the interleaved tn notes, making sure to put lang0
            # notes on the left and lang1 notes on the right.
            tn_verses = None
            for idx, tn_book_content_unit3 in enumerate(tn_book_content_units):
                tn_verses = verses_for_chapter_tn(tn_book_content_unit3, chapter_num)
                if tn_verses and verse_num in tn_verses:
                    if is_even(idx):
                        yield html_row_begin
                    yield html_column_begin
                    yield from format_tn_verse(
                        tn_book_content_unit3,
                        chapter_num,
                        verse_num,
                        tn_verses[verse_num],
                    )
                    yield html_column_end
            yield html_row_end

            # Add the interleaved tq questions, making sure to put lang0
            # questions on the left and lang1 questions on the right.
            tq_verses = None
            for idx, tq_book_content_unit in enumerate(tq_book_content_units):
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    if is_even(idx):
                        yield html_row_begin
                    yield html_column_begin
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )
                    yield html_column_end
            yield html_row_end

            # Add the interleaved translation word links, making sure to put lang0
            # word links on the left and lang1 word links on the right.
            for idx, tw_book_content_unit in enumerate(tw_book_content_units):
                # Get the usfm_book_content_unit instance associated with the
                # tw_book_content_unit, i.e., having same lang_code and
                # resource_code.
                usfm_book_content_unit_lst = [
                    usfm_book_content_unit
                    for usfm_book_content_unit in usfm_book_content_units
                    if usfm_book_content_unit.lang_code
                    == tw_book_content_unit.lang_code
                    and usfm_book_content_unit.resource_code
                    == tw_book_content_unit.resource_code
                ]
                if usfm_book_content_unit_lst:
                    usfm_book_content_unit_ = usfm_book_content_unit_lst[0]
                else:
                    usfm_book_content_unit_ = None
                # Add the translation words links section.
                if (
                    usfm_book_content_unit_ is not None
                    and verse_num
                    in usfm_book_content_unit_.chapters[chapter_num].verses
                ):
                    if is_even(idx):
                        yield html_row_begin
                        yield html_column_begin

                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        usfm_book_content_unit_.chapters[chapter_num].verses[verse_num],
                    )
                    yield html_column_end
                else:
                    ldebug(
                        "usfm for chapter %s, verse %s likely could not be parsed by usfm parser for language %s and book %s",
                        chapter_num,
                        verse_num,
                        tw_book_content_unit.lang_code,
                        tw_book_content_unit.resource_code,
                    )
            yield html_row_end

        # Add the footnotes
        for usfm_book_content_unit in usfm_book_content_units:
            try:
                chapter_footnotes = usfm_book_content_unit.chapters[
                    chapter_num
                ].footnotes
                if chapter_footnotes:
                    yield footnotes_heading
                    yield chapter_footnotes
            except KeyError:
                ldebug(
                    "usfm_book_content_unit: %s, does not have chapter: %s",
                    usfm_book_content_unit,
                    chapter_num,
                )
                lexception("Caught exception:")


def assemble_usfm_as_iterator_for_book_then_lang_1c(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML wherein at least one USFM resource (e.g., ulb,
    nav, cuv, etc.) exists, and TN, TQ, and TW may exist. One column
    layout.

    Rough sketch of algo that follows:
    English book intro
    French book intro
    chapter heading, e.g., Chapter 1
        english chapter intro goes here
        french chaptre entre qui
            Unlocked Literal Bible (ULB) 1:1
            a verse goes here
            French ULB 1:1
            a verse goes here
            ULB Translation Helps 1:1
            translation notes for English goes here
            French Translation notes 1:1
            translation notes for French goes here
            etc for tq, tw links, footnotes, followed by tw definitions
    """

    ldebug = logger.debug
    lexception = logger.exception

    usfm_book_content_unit_: Optional[USFMBook]
    tn_verses: Optional[dict[str, HtmlContent]]
    tq_verses: Optional[dict[str, HtmlContent]]

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    tw_book_content_units = sorted(tw_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        # Add the book intro
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield HtmlContent(book_intro)

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)

    # Use the usfm_book_content_unit that has the most chapters as a
    # chapter_num pump.
    # Realize the most amount of content displayed to user.
    usfm_with_most_chapters = max(
        usfm_book_content_units,
        key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters.keys(),
    )
    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        # Add the first USFM resource's chapter heading. We ignore
        # chapter headings for other usfm_book_content_units because it would
        # be strange to have more than one chapter heading per chapter
        # for this assembly sub-strategy.
        chapter_heading = HtmlContent("")
        chapter_heading = chapter.content[0]
        yield HtmlContent(chapter_heading)

        # Add chapter intro for each language
        for tn_book_content_unit2 in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit2, chapter_num)

        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)

        # Use the usfm_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump.
        # I.e., realize the most amount of content displayed to user.
        # usfm_with_most_verses = max(
        #     usfm_book_content_units,
        #     key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters[
        #         chapter_num
        #     ].verses.keys(),
        # )
        # for verse_num in usfm_with_most_verses.chapters[chapter_num].verses.keys():
        for verse_num in chapter.verses.keys():
            # Add the interleaved USFM verses
            for usfm_book_content_unit in usfm_book_content_units:
                if (
                    chapter_num in usfm_book_content_unit.chapters
                    and verse_num in usfm_book_content_unit.chapters[chapter_num].verses
                ):
                    # Add scripture verse
                    yield usfm_book_content_unit.chapters[chapter_num].verses[verse_num]

            # Add the interleaved tn notes
            tn_verses = None
            for tn_book_content_unit3 in tn_book_content_units:
                tn_verses = verses_for_chapter_tn(tn_book_content_unit3, chapter_num)
                if tn_verses and verse_num in tn_verses:
                    yield from format_tn_verse(
                        tn_book_content_unit3,
                        chapter_num,
                        verse_num,
                        tn_verses[verse_num],
                    )

            # Add the interleaved tq questions
            tq_verses = None
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )

            # Add the interleaved translation word links
            for tw_book_content_unit in tw_book_content_units:
                # Get the usfm_book_content_unit instance associated with the
                # tw_book_content_unit, i.e., having same lang_code and
                # resource_code.
                usfm_book_content_unit_lst = [
                    usfm_book_content_unit
                    for usfm_book_content_unit in usfm_book_content_units
                    if usfm_book_content_unit.lang_code
                    == tw_book_content_unit.lang_code
                    and usfm_book_content_unit.resource_code
                    == tw_book_content_unit.resource_code
                ]
                if usfm_book_content_unit_lst:
                    usfm_book_content_unit_ = usfm_book_content_unit_lst[0]
                else:
                    usfm_book_content_unit_ = None
                # Add the translation words links section.
                if (
                    usfm_book_content_unit_ is not None
                    and verse_num
                    in usfm_book_content_unit_.chapters[chapter_num].verses
                ):
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        usfm_book_content_unit_.chapters[chapter_num].verses[verse_num],
                    )
                else:
                    ldebug(
                        "usfm for chapter %s, verse %s likely could not be parsed by usfm parser for language %s and book %s",
                        chapter_num,
                        verse_num,
                        tw_book_content_unit.lang_code,
                        tw_book_content_unit.resource_code,
                    )

        # Add the footnotes
        for usfm_book_content_unit in usfm_book_content_units:
            try:
                chapter_footnotes = usfm_book_content_unit.chapters[
                    chapter_num
                ].footnotes
                if chapter_footnotes:
                    yield footnotes_heading
                    yield chapter_footnotes
            except KeyError:
                ldebug(
                    "usfm_book_content_unit: %s, does not have chapter: %s",
                    usfm_book_content_unit,
                    chapter_num,
                )
                lexception("Caught exception:")


def assemble_usfm_as_iterator_for_book_then_lang_1c_c(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
    footnotes_heading: HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[HtmlContent]:
    """
    Construct the HTML wherein at least one USFM resource (e.g., ulb,
    nav, cuv, etc.) exists, and TN, TQ, and TW may exist. One column
    layout compacted for printing: fewer translation words, no
    linking.

    Rough sketch of algo that follows:
    English book intro
    French book intro
    chapter heading, e.g., Chapter 1
        english chapter intro goes here
        french chaptre entre qui
            Unlocked Literal Bible (ULB) 1:1
            a verse goes here
            French ULB 1:1
            a verse goes here
            ULB Translation Helps 1:1
            translation notes for English goes here
            French Translation notes 1:1
            translation notes for French goes here
            etc for tq, tw links, footnotes, followed by tw definitions
    """

    ldebug = logger.debug
    lexception = logger.exception

    tn_verses: Optional[dict[str, HtmlContent]]
    tq_verses: Optional[dict[str, HtmlContent]]

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    tw_book_content_units = sorted(tw_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        # Add the book intro
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield HtmlContent(book_intro)

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)

    # Use the usfm_book_content_unit that has the most chapters as a
    # chapter_num pump.
    # Realize the most amount of content displayed to user.
    usfm_with_most_chapters = max(
        usfm_book_content_units,
        key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters.keys(),
    )
    for chapter_num, chapter in usfm_with_most_chapters.chapters.items():
        # Add the first USFM resource's chapter heading. We ignore
        # chapter headings for other usfm_book_content_units because it would
        # be strange to have more than one chapter heading per chapter
        # for this assembly sub-strategy.
        chapter_heading = HtmlContent("")
        chapter_heading = chapter.content[0]
        yield HtmlContent(chapter_heading)

        # Add chapter intro for each language
        for tn_book_content_unit2 in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield HtmlContent(chapter_intro(tn_book_content_unit2, chapter_num))

        for bc_book_content_unit in bc_book_content_units:
            # Add the commentary for chapter.
            yield HtmlContent(chapter_commentary(bc_book_content_unit, chapter_num))

        # Use the usfm_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump.
        # I.e., realize the most amount of content displayed to user.
        # usfm_with_most_verses = max(
        #     usfm_book_content_units,
        #     key=lambda usfm_book_content_unit: usfm_book_content_unit.chapters[
        #         chapter_num
        #     ].verses.keys(),
        # )
        # for verse_num in usfm_with_most_verses.chapters[chapter_num].verses.keys():
        for verse_num in chapter.verses.keys():
            # Add the interleaved USFM verses
            for usfm_book_content_unit in usfm_book_content_units:
                if (
                    chapter_num in usfm_book_content_unit.chapters
                    and verse_num in usfm_book_content_unit.chapters[chapter_num].verses
                ):
                    # Add scripture verse
                    yield usfm_book_content_unit.chapters[chapter_num].verses[verse_num]

            # Add the interleaved tn notes
            tn_verses = None
            for tn_book_content_unit3 in tn_book_content_units:
                tn_verses = verses_for_chapter_tn(tn_book_content_unit3, chapter_num)
                if tn_verses and verse_num in tn_verses:
                    yield from format_tn_verse(
                        tn_book_content_unit3,
                        chapter_num,
                        verse_num,
                        tn_verses[verse_num],
                    )

            # Add the interleaved tq questions
            tq_verses = None
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )

        # Add the footnotes
        for usfm_book_content_unit in usfm_book_content_units:
            try:
                chapter_footnotes = usfm_book_content_unit.chapters[
                    chapter_num
                ].footnotes
                if chapter_footnotes:
                    yield footnotes_heading
                    yield chapter_footnotes
            except KeyError:
                ldebug(
                    "usfm_book_content_unit: %s, does not have chapter: %s",
                    usfm_book_content_unit,
                    chapter_num,
                )
                lexception("Caught exception:")


def assemble_tn_as_iterator_for_book_then_lang(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein at least
    tn_book_content_units exists, and TN, TQ, and TW may exist.


    Rough sketch of algo that follows:
    English book intro
    French book intro
    chapter heading, e.g., Chapter 1
        english chapter intro goes here
        french chapter intro goes here
            ULB Translation Helps 1:1
            translation notes for English goes here
            French Translation notes 1:1
            translation notes for French goes here
            etc for tq, tw links, followed by tw definitions
    """

    usfm_book_content_unit_: Optional[USFMBook]

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    tw_book_content_units = sorted(tw_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        # Add the book intro
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield HtmlContent(book_intro)

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)

    # Use the tn_book_content_unit that has the most chapters as a
    # chapter_num pump.
    # Realize the most amount of content displayed to user.
    tn_with_most_chapters = max(
        tn_book_content_units,
        key=lambda tn_book_content_unit: tn_book_content_unit.chapters.keys(),
    )
    for chapter_num in tn_with_most_chapters.chapters.keys():
        yield HtmlContent("Chapter {}".format(chapter_num))

        # Add chapter intro for each language
        for tn_book_content_unit in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield from chapter_intro(tn_book_content_unit, chapter_num)

        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)

        # Use the tn_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump.
        # I.e., realize the most amount of content displayed to user.
        tn_with_most_verses = max(
            tn_book_content_units,
            key=lambda tn_book_content_unit: tn_book_content_unit.chapters[
                chapter_num
            ].verses.keys(),
        )
        for verse_num in tn_with_most_verses.chapters[chapter_num].verses.keys():
            # Add the interleaved tn notes
            for tn_book_content_unit in tn_book_content_units:
                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
                if tn_verses and verse_num in tn_verses:
                    yield from format_tn_verse(
                        tn_book_content_unit,
                        chapter_num,
                        verse_num,
                        tn_verses[verse_num],
                    )

            # Add the interleaved tq questions
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )

            # Add the interleaved translation word links
            for tw_book_content_unit in tw_book_content_units:
                # Get the usfm_book_content_unit instance associated with the
                # tw_book_content_unit, i.e., having same lang_code and
                # resource_code.
                usfm_book_content_unit_lst = [
                    usfm_book_content_unit
                    for usfm_book_content_unit in usfm_book_content_units
                    if usfm_book_content_unit.lang_code
                    == tw_book_content_unit.lang_code
                    and usfm_book_content_unit.resource_code
                    == tw_book_content_unit.resource_code
                ]
                if usfm_book_content_unit_lst:
                    usfm_book_content_unit_ = usfm_book_content_unit_lst[0]
                else:
                    usfm_book_content_unit_ = None
                # Add the translation words links section.
                if (
                    usfm_book_content_unit_ is not None
                    and verse_num
                    in usfm_book_content_unit_.chapters[chapter_num].verses
                ):
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        usfm_book_content_unit_.chapters[chapter_num].verses[verse_num],
                    )


def assemble_tn_as_iterator_for_book_then_lang_c(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein at least
    tn_book_content_units exists, and TN, TQ, and TW may exist.


    Rough sketch of algo that follows:
    English book intro
    French book intro
    chapter heading, e.g., Chapter 1
        english chapter intro goes here
        french chapter intro goes here
            ULB Translation Helps 1:1
            translation notes for English goes here
            French Translation notes 1:1
            translation notes for French goes here
            etc for tq, tw links, followed by tw definitions
    """
    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    tw_book_content_units = sorted(tw_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        # Add the book intro
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield HtmlContent(book_intro)

    for bc_book_content_unit in bc_book_content_units:
        yield book_intro_commentary(bc_book_content_unit)

    # Use the tn_book_content_unit that has the most chapters as a
    # chapter_num pump.
    # Realize the most amount of content displayed to user.
    chapters_key = lambda tn_book_content_unit: tn_book_content_unit.chapters.keys()
    tn_with_most_chapters = max(tn_book_content_units, key=chapters_key)
    for chapter_num in tn_with_most_chapters.chapters.keys():
        yield HtmlContent("Chapter {}".format(chapter_num))

        # Add chapter intro for each language
        for tn_book_content_unit in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield from chapter_intro(tn_book_content_unit, chapter_num)

        for bc_book_content_unit in bc_book_content_units:
            # Add chapter commentary.
            yield from chapter_commentary(bc_book_content_unit, chapter_num)

        # Use the tn_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump.
        # I.e., realize the most amount of content displayed to user.
        tn_with_most_verses = max(
            tn_book_content_units,
            key=lambda tn_book_content_unit: tn_book_content_unit.chapters[
                chapter_num
            ].verses.keys(),
        )
        for verse_num in tn_with_most_verses.chapters[chapter_num].verses.keys():
            # Add the interleaved tn notes
            for tn_book_content_unit in tn_book_content_units:
                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
                if tn_verses and verse_num in tn_verses:
                    yield from format_tn_verse(
                        tn_book_content_unit,
                        chapter_num,
                        verse_num,
                        tn_verses[verse_num],
                    )

            # Add the interleaved tq questions
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )


def assemble_tq_as_iterator_for_book_then_lang(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein at least
    tq_book_content_units exists, and TQ, and TW may exist.
    """

    usfm_book_content_unit_: Optional[USFMBook]

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    tn_book_content_units = sorted(tn_book_content_units, key=sort_key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    tw_book_content_units = sorted(tw_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Use the tq_book_content_unit that has the most chapters as a
    # chapter_num pump.
    # Realize the most amount of content displayed to user.
    # chapter_key = lambda tq_book_content_unit: tq_book_content_unit.chapters.keys()
    tq_with_most_chapters = max(
        tq_book_content_units,
        key=lambda tq_book_content_unit: tq_book_content_unit.chapters.keys(),
    )
    for chapter_num in tq_with_most_chapters.chapters.keys():
        yield HtmlContent("Chapter {}".format(chapter_num))

        for bc_book_content_unit in bc_book_content_units:
            # Add the chapter commentary.
            yield chapter_commentary(bc_book_content_unit, chapter_num)

        # Use the tn_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump.
        # I.e., realize the most amount of content displayed to user.
        tq_with_most_verses = max(
            tq_book_content_units,
            key=lambda tq_book_content_unit: tq_book_content_unit.chapters[
                chapter_num
            ].verses.keys(),
        )
        for verse_num in tq_with_most_verses.chapters[chapter_num].verses.keys():
            # Add the interleaved tq questions
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )

            # Add the interleaved translation word links
            for tw_book_content_unit in tw_book_content_units:
                # Get the usfm_book_content_unit instance associated with the
                # tw_book_content_unit, i.e., having same lang_code and
                # resource_code.
                usfm_book_content_unit_lst = [
                    usfm_book_content_unit
                    for usfm_book_content_unit in usfm_book_content_units
                    if usfm_book_content_unit.lang_code
                    == tw_book_content_unit.lang_code
                    and usfm_book_content_unit.resource_code
                    == tw_book_content_unit.resource_code
                ]
                if usfm_book_content_unit_lst:
                    usfm_book_content_unit_ = usfm_book_content_unit_lst[0]
                else:
                    usfm_book_content_unit_ = None
                # Add the translation words links section.
                if (
                    usfm_book_content_unit_ is not None
                    and verse_num
                    in usfm_book_content_unit_.chapters[chapter_num].verses
                ):
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        usfm_book_content_unit_.chapters[chapter_num].verses[verse_num],
                    )


def assemble_tq_as_iterator_for_book_then_lang_c(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Iterable[HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein at least
    tq_book_content_units exists, and TQ, and TW may exist.
    """

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    usfm_book_content_units = sorted(usfm_book_content_units, key=sort_key)
    # tn_book_content_units = sorted(tn_book_content_units, key=key)
    tq_book_content_units = sorted(tq_book_content_units, key=sort_key)
    tw_book_content_units = sorted(tw_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Use the tq_book_content_unit that has the most chapters as a
    # chapter_num pump.
    # Realize the most amount of content displayed to user.
    # chapter_key = lambda tq_book_content_unit: tq_book_content_unit.chapters.keys()
    tq_with_most_chapters = max(
        tq_book_content_units,
        key=lambda tq_book_content_unit: tq_book_content_unit.chapters.keys(),
    )
    for chapter_num in tq_with_most_chapters.chapters.keys():
        yield HtmlContent("Chapter {}".format(chapter_num))

        for bc_book_content_unit in bc_book_content_units:
            # Add chapter commentary
            yield chapter_commentary(bc_book_content_unit, chapter_num)

        # Use the tn_book_content_unit that has the most verses for
        # this chapter_num chapter as a verse_num pump.
        # I.e., realize the most amount of content displayed to user.
        tq_with_most_verses = max(
            tq_book_content_units,
            key=lambda tq_book_content_unit: tq_book_content_unit.chapters[
                chapter_num
            ].verses.keys(),
        )
        for verse_num in tq_with_most_verses.chapters[chapter_num].verses.keys():
            # Add the interleaved tq questions
            for tq_book_content_unit in tq_book_content_units:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)
                # Add TQ verse content, if any
                if tq_verses and verse_num in tq_verses:
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        tq_verses[verse_num],
                    )


def assemble_tw_as_iterator_for_book_then_lang(
    usfm_book_content_units: Sequence[USFMBook],
    tn_book_content_units: Sequence[TNBook],
    tq_book_content_units: Sequence[TQBook],
    tw_book_content_units: Sequence[TWBook],
    bc_book_content_units: Sequence[BCBook],
) -> Iterable[HtmlContent]:
    """Construct the HTML for BC and TW."""

    # Sort resources by language
    def sort_key(resource: BookContent) -> str:
        return resource.lang_code

    tw_book_content_units = sorted(tw_book_content_units, key=sort_key)
    bc_book_content_units = sorted(bc_book_content_units, key=sort_key)

    # Add the bible commentary
    for bc_book_content_unit in bc_book_content_units:
        yield bc_book_content_unit.book_intro
        for chapter in bc_book_content_unit.chapters.values():
            yield chapter.commentary


######################
## Utility functions


def format_tq_verse(
    resource_type_name: str,
    chapter_num: int,
    verse_num: str,
    verse: HtmlContent,
) -> Iterable[HtmlContent]:

    # Change H1 HTML elements to H4 HTML elements in each translation
    # question.
    yield HtmlContent(sub(H1, H4, verse))


def first_usfm_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[USFMBook]:
    """
    Return the first USFMBook instance, if any, contained in book_content_units,
    else return None.
    """
    usfm_books = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, USFMBook)
        # NOTE If you wanted to force only certain USFM resource types
        # in the usfm_book_content_unit position then you could do something
        # like:
        # resource for resource in resources if isinstance(resource,
        # USFMResource) and resource.resource_type in ["ulb", "cuv",
        # "nav", "ugnt", "uhb", "rsb", "f10", "blv", "ust"]
        # You'd have to choose which USFM resource types based on
        # which ones make sense for TN, TQ, and TW to reference
        # them.
        # NOTE See note on _second_usfm_book_content_unit for what else
        # would need to be done to support this alternative.
    ]
    return usfm_books[0] if usfm_books else None


def second_usfm_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[USFMBook]:
    """
    Return the second USFMBook instance, if any, contained in book_content_units,
    else return None.
    """
    usfm_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, USFMBook)
    ]
    return usfm_book_content_units[1] if len(usfm_book_content_units) > 1 else None
    # NOTE This is just a sketch of what you could do if you wanted to
    # only allow certain USFM resource types to be in usfm_book_content_unit
    # position in the interleaving strategy. Currently, the
    # interleaving strategy shows usfm_book_content_unit at the end of other
    # resources in each chapter, i.e., no TN, TQ, or TW resource
    # referencing it.
    # usfm_book_content_units = [
    #     resource for resource in resources if isinstance(resource,
    #     USFMResource) and resource.resource_type in ["udb"]
    # ]
    # return usfm_book_content_units[0] if usfm_book_content_units else None


def tn_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[TNBook]:
    """
    Return the TNBook instance, if any, contained in book_content_units,
    else return None.
    """
    tn_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, TNBook)
    ]
    return tn_book_content_units[0] if tn_book_content_units else None


def tw_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[TWBook]:
    """
    Return the TWBook instance, if any, contained in book_content_units,
    else return None.
    """
    tw_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, TWBook)
    ]
    return tw_book_content_units[0] if tw_book_content_units else None


def tq_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[TQBook]:
    """
    Return the TQBook instance, if any, contained in book_content_units,
    else return None.
    """
    tq_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, TQBook)
    ]
    return tq_book_content_units[0] if tq_book_content_units else None


def bc_book_content_unit(
    book_content_units: Sequence[BookContent],
) -> Optional[BCBook]:
    """
    Return the BCBook instance, if any, contained in book_content_units,
    else return None.
    """
    bc_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, BCBook)
    ]
    return bc_book_content_units[0] if bc_book_content_units else None


def adjust_book_intro_headings(book_intro: str) -> HtmlContent:
    """Change levels on headings."""
    # Move the H2 out of the way, we'll deal with it last.
    book_intro = sub(H2, H6, book_intro)
    book_intro = sub(H1, H2, book_intro)
    book_intro = sub(H3, H4, book_intro)
    # Now adjust the temporary H6s.
    return HtmlContent(sub(H6, H3, book_intro))


def adjust_chapter_intro_headings(chapter_intro: str) -> HtmlContent:
    """Change levels on headings."""
    # Move the H4 out of the way, we'll deal with it last.
    chapter_intro = sub(H4, H6, chapter_intro)
    chapter_intro = sub(H3, H4, chapter_intro)
    chapter_intro = sub(H1, H3, chapter_intro)
    chapter_intro = sub(H2, H4, chapter_intro)
    # Now adjust the temporary H6s.
    return HtmlContent(sub(H6, H5, chapter_intro))


def adjust_commentary_headings(chapter_commentary: str) -> HtmlContent:
    """Change levels on headings."""
    # logger.debug("commentary parser: %s", parser)
    # Move the H4 out of the way, we'll deal with it last.
    chapter_commentary = sub(H4, H6, chapter_commentary)
    chapter_commentary = sub(H3, H4, chapter_commentary)
    chapter_commentary = sub(H1, H3, chapter_commentary)
    chapter_commentary = sub(H2, H4, chapter_commentary)
    # Now adjust the temporary H6s.
    return HtmlContent(sub(H6, H5, chapter_commentary))


def chapter_intro(tn_book_content_unit: TNBook, chapter_num: int) -> HtmlContent:
    """Get the chapter intro."""
    if tn_book_content_unit and chapter_num in tn_book_content_unit.chapters:
        chapter_intro = tn_book_content_unit.chapters[chapter_num].intro_html
    else:
        chapter_intro = HtmlContent("")
    return adjust_chapter_intro_headings(chapter_intro)


def book_intro_commentary(bc_book_content_unit: BCBook) -> HtmlContent:
    if bc_book_content_unit:
        book_intro_commentary = bc_book_content_unit.book_intro
    else:
        book_intro_commentary = HtmlContent("")
    return adjust_commentary_headings(book_intro_commentary)


def chapter_commentary(bc_book_content_unit: BCBook, chapter_num: int) -> HtmlContent:
    """Get the chapter commentary."""
    if bc_book_content_unit and chapter_num in bc_book_content_unit.chapters:
        chapter_commentary = bc_book_content_unit.chapters[chapter_num].commentary
    else:
        chapter_commentary = HtmlContent("")
    return adjust_commentary_headings(chapter_commentary)


def format_tn_verse(
    book_content_unit: TNBook,
    chapter_num: int,
    verse_num: str,
    verse: HtmlContent,
    book_numbers: Mapping[str, str] = BOOK_NUMBERS,
    num_zeros: int = NUM_ZEROS,
) -> Iterable[HtmlContent]:
    """
    This is a slightly different form of TNResource.tn_verse that is used
    when no USFM has been requested.
    """
    # Change H1 HTML elements to H4 HTML elements in each translation note.
    yield HtmlContent(sub(H1, H4, verse))


def verses_for_chapter_tn(
    book_content_unit: TNBook, chapter_num: int
) -> Optional[dict[str, HtmlContent]]:
    """
    Return the HTML for verses that are in the chapter with
    chapter_num.
    """
    verses_html = None
    if chapter_num in book_content_unit.chapters:
        verses_html = book_content_unit.chapters[chapter_num].verses
    return verses_html


def verses_for_chapter_tq(
    book_content_unit: TQBook,
    chapter_num: int,
) -> Optional[dict[str, HtmlContent]]:
    """Return the HTML for verses in chapter_num."""
    verses_html = None
    if chapter_num in book_content_unit.chapters:
        verses_html = book_content_unit.chapters[chapter_num].verses
    return verses_html


def translation_word_links(
    book_content_unit: TWBook,
    chapter_num: int,
    verse_num: str,
    verse: HtmlContent,
    unordered_list_begin_str: str = settings.UNORDERED_LIST_BEGIN_STR,
    translation_word_list_item_fmt_str: str = settings.TRANSLATION_WORD_LIST_ITEM_FMT_STR,
    unordered_list_end_str: str = settings.UNORDERED_LIST_END_STR,
    book_names: Mapping[str, str] = BOOK_NAMES,
) -> Iterable[HtmlContent]:
    """
    Add the translation word links section which provides links from words
    used in the current verse to their definition.
    """
    uses: list[TWUse] = []
    name_content_pair: TWNameContentPair
    for name_content_pair in book_content_unit.name_content_pairs:
        # This checks that the word occurs as an exact sub-string in
        # the verse.
        if search(r"\b{}\b".format(escape(name_content_pair.localized_word)), verse):
            use = TWUse(
                lang_code=book_content_unit.lang_code,
                book_id=book_content_unit.resource_code,
                book_name=book_names[book_content_unit.resource_code],
                chapter_num=chapter_num,
                verse_num=verse_num,
                localized_word=name_content_pair.localized_word,
            )
            uses.append(use)
            # Store reference for use in 'Uses:' section that
            # comes later.
            if name_content_pair.localized_word in book_content_unit.uses:
                book_content_unit.uses[name_content_pair.localized_word].append(use)
            else:
                book_content_unit.uses[name_content_pair.localized_word] = [use]

    if uses:
        # Start list formatting
        yield unordered_list_begin_str
        # Append word links.
        uses_list_items = [
            translation_word_list_item_fmt_str.format(
                book_content_unit.lang_code,
                use.localized_word,
                use.localized_word,
            )
            for use in list(uniq(uses))  # Get the unique uses
        ]
        yield HtmlContent("\n".join(uses_list_items))
        # End list formatting
        yield unordered_list_end_str


def languages_in_books(
    usfm_book_content_units: Sequence[BookContent],
) -> Sequence[str]:
    """Return the distinct languages in the usfm_book_content_units."""
    languages = sorted(
        list(
            set(
                [
                    lang_group[0]
                    for lang_group in groupby(
                        usfm_book_content_units,
                        key=lambda unit: unit.lang_code,
                    )
                ]
            )
        )
    )
    logger.debug("languages: %s", languages)
    # Invariant: if we got this far, then we know there are at
    # least two languages being requested (see
    # document_generator.select_assembly_layout_kind).
    return languages


def ensure_primary_usfm_books_for_different_languages_are_adjacent(
    usfm_book_content_units: Sequence[USFMBook],
) -> Sequence[USFMBook]:
    """
    Interleave/zip USFM book content units such that they are
    juxtaposed language to language in pairs.
    """
    languages = languages_in_books(usfm_book_content_units)
    # Get book content units for language 0.
    usfm_lang0_book_content_units = [
        usfm_book_content_unit
        for usfm_book_content_unit in usfm_book_content_units
        if usfm_book_content_unit.lang_code == languages[0]
    ]
    # Get book content units for language 1.
    usfm_lang1_book_content_units = [
        usfm_book_content_unit
        for usfm_book_content_unit in usfm_book_content_units
        if usfm_book_content_unit.lang_code == languages[1]
    ]
    return list(
        # Flatten iterable of tuples into regular flat iterable.
        chain.from_iterable(
            # Interleave the two different languages usfm units.
            zip_longest(usfm_lang0_book_content_units, usfm_lang1_book_content_units)
        )
    )
