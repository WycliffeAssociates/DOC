"""
This module provides the assembly strategies and sub-strategies that
are used to assemble HTML documents prior to their conversion to PDF
form.

Assembly strategies utilize the Strategy pattern:
https://github.com/faif/python-patterns/blob/master/patterns/behavioral/strategy.py
"""

import itertools
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, Optional

from document.config import settings
from document.domain import bible_books, model
from document.utils import tw_utils

logger = settings.logger(__name__)


H1, H2, H3, H4, H5, H6 = "h1", "h2", "h3", "h4", "h5", "h6"


########################################################################
# Asseembly strategy and sub-strategy factories
#
# Currently, there are two levels of assembly strategies: one higher,
# chosen by assembly_strategy_factory, and one lower, chosen by
# assembly_sub_strategy_factory. These two levels of assembly
# strategies work together in the following way: the higher level
# constrains the assembly algorithm by some criteria, e.g., by
# language, and then the lower level further organizes the assembly
# within those constraints, e.g., by superimposing an order to when
# resource's are interleaved. It is possible to have both multiple
# higher level, so-called 'assembly strategies' and lower level,
# so-called 'sub strategies', assembly strategies.

# FIXME Proper return type that mypy likes.
def assembly_strategy_factory(
    assembly_strategy_kind: model.AssemblyStrategyEnum,
) -> Any:
    """
    Strategy pattern. Given an assembly_strategy_kind, returns the
    appropriate strategy function to run.
    """
    strategies = {
        model.AssemblyStrategyEnum.LANGUAGE_BOOK_ORDER: assemble_content_by_lang_then_book,
        model.AssemblyStrategyEnum.BOOK_LANGUAGE_ORDER: assemble_content_by_book_then_lang,
    }
    return strategies[assembly_strategy_kind]


def assembly_sub_strategy_factory(
    usfm_book_content_unit: Optional[model.USFMBook],
    tn_book_content_unit: Optional[model.TNBook],
    tq_book_content_unit: Optional[model.TQBook],
    tw_book_content_unit: Optional[model.TWBook],
    # ta_resource: Optional[TAResource],
    usfm_book_content_unit2: Optional[model.USFMBook],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> Callable[
    [
        Optional[model.USFMBook],
        Optional[model.TNBook],
        Optional[model.TQBook],
        Optional[model.TWBook],
        # Optional[TAResource],
        Optional[model.USFMBook],
        model.AssemblySubstrategyEnum,
    ],
    Iterable[model.HtmlContent],
]:
    """
    Strategy pattern. Given the existence, i.e., exists or None, of each
    type of the possible resource instances (i.e., the resource parameters
    above) and an assembly sub-strategy kind, returns the appropriate
    sub-strategy function to run.

    This functions as a lookup table that will select the right
    assembly function to run. The impetus for it is to avoid messy
    conditional logic in an otherwise monolithic assembly algorithm
    that would be checking the existence of each resource.
    This makes adding new strategies straightforward, if a bit
    redundant. The redundancy is the cost of comprehension.
    """
    strategies: Mapping[
        tuple[
            bool,  # usfm_book_content_unit_exists
            bool,  # tn_book_content_unit_exists
            bool,  # tq_book_content_unit_exists
            bool,  # tw_book_content_unit_exists
            # bool,  # ta_resource_exists
            bool,  # usfm_book_content_unit2_exists
            model.AssemblySubstrategyEnum,  # assembly_strategy_kind
        ],
        Callable[
            [
                Optional[model.USFMBook],
                Optional[model.TNBook],
                Optional[model.TQBook],
                Optional[model.TWBook],
                # Optional[TAResource],
                Optional[model.USFMBook],
                model.AssemblySubstrategyEnum,
            ],
            Iterable[model.HtmlContent],
        ],
    ] = {  # This is a big truth table that ensures every case is handled explicitly.
        (
            True,
            True,
            True,
            True,
            # False,
            True,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            True,
            True,
            False,
            # False,
            True,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            False,
            True,
            False,
            # False,
            True,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            False,
            False,
            True,
            # False,
            True,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            True,
            False,
            False,
            # False,
            True,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            True,
            False,
            True,
            # False,
            True,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            False,
            True,
            True,
            # False,
            True,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            False,
            False,
            False,
            # False,
            True,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            False,
            False,
            False,
            False,
            # False,
            True,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        # (
        #     True,
        #     True,
        #     True,
        #     True,
        #     True,
        #     False,
        #     model.AssemblySubstrategyEnum.VERSE,
        # ): _assemble_usfm_tn_tq_tw_ta_content_by_verse,
        # ): _assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            True,
            True,
            True,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            True,
            False,
            True,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            False,
            True,
            True,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_tq_tw_content_by_verse,
        (
            True,
            False,
            False,
            True,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_tw_content_by_verse,
        (
            True,
            True,
            True,
            False,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            True,
            False,
            True,
            False,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_tq_content_by_verse,
        (
            True,
            True,
            False,
            False,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            False,
            True,
            True,
            True,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tn_as_iterator_content_by_verse,
        (
            False,
            True,
            False,
            True,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tn_as_iterator_content_by_verse,
        (
            False,
            True,
            True,
            False,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tn_as_iterator_content_by_verse,
        (
            False,
            False,
            True,
            True,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tq_tw_content_by_verse,
        (
            False,
            False,
            False,
            True,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tw_content_by_verse,
        (
            False,
            False,
            True,
            False,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tq_content_by_verse,
        (
            True,
            False,
            False,
            False,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse,
        (
            False,
            True,
            False,
            False,
            # False,
            False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tn_as_iterator_content_by_verse,
    }
    return strategies[
        (
            # Turn existence (exists or not) into a boolean for each instance, the
            # tuple of these together are an immutable, and thus hashable,
            # dictionary key into our function lookup/dispatch table.
            usfm_book_content_unit is not None,
            tn_book_content_unit is not None,
            tq_book_content_unit is not None,
            tw_book_content_unit is not None,
            # ta_resource is not None,
            usfm_book_content_unit2 is not None,
            assembly_substrategy_kind,
        )
    ]


def assembly_sub_strategy_factory_for_book_then_lang(
    usfm_book_content_units: Sequence[model.USFMBook],
    tn_book_content_units: Sequence[model.TNBook],
    tq_book_content_units: Sequence[model.TQBook],
    tw_book_content_units: Sequence[model.TWBook],
    # ta_resources: Sequence[TAResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> Callable[
    [
        Sequence[model.USFMBook],
        Sequence[model.TNBook],
        Sequence[model.TQBook],
        Sequence[model.TWBook],
        # list[TAResource],
        model.AssemblySubstrategyEnum,
    ],
    Iterable[model.HtmlContent],
]:
    """
    Strategy pattern. Given the existence, i.e., exists or emtpy, of each
    type of the possible resource instances and an
    assembly sub-strategy kind, returns the appropriate sub-strategy
    function to run.

    This functions as a lookup table that will select the right
    assembly function to run. The impetus for it is to avoid messy
    conditional logic in an otherwise monolithic assembly algorithm
    that would be checking the existence of each resource.
    This makes adding new strategies straightforward, if a bit
    redundant. The redundancy is the cost of comprehension.
    """
    strategies: Mapping[
        tuple[
            bool,  # usfm_book_content_units is non-empty
            bool,  # tn_book_content_units is non-empty
            bool,  # tq_book_content_units is non-empty
            bool,  # tw_book_content_units is non-empty
            # bool,  # ta_resources is non-empty
            model.AssemblySubstrategyEnum,  # assembly_strategy_kind
        ],
        Callable[
            [
                Sequence[model.USFMBook],
                Sequence[model.TNBook],
                Sequence[model.TQBook],
                Sequence[model.TWBook],
                # list[TAResource],
                model.AssemblySubstrategyEnum,
            ],
            Iterable[model.HtmlContent],
        ],
    ] = {
        (
            True,
            True,
            True,
            True,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse_for_book_then_lang,
        (
            True,
            True,
            True,
            False,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse_for_book_then_lang,
        (
            True,
            True,
            False,
            True,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse_for_book_then_lang,
        (
            True,
            True,
            False,
            False,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse_for_book_then_lang,
        (
            True,
            False,
            True,
            True,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse_for_book_then_lang,
        (
            True,
            False,
            True,
            False,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse_for_book_then_lang,
        (
            True,
            False,
            False,
            True,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse_for_book_then_lang,
        (
            True,
            False,
            False,
            False,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_usfm_as_iterator_content_by_verse_for_book_then_lang,
        (
            False,
            True,
            True,
            True,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tn_as_iterator_content_by_verse_for_book_then_lang,
        (
            False,
            True,
            True,
            False,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tn_as_iterator_content_by_verse_for_book_then_lang,
        (
            False,
            True,
            False,
            True,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tn_as_iterator_content_by_verse_for_book_then_lang,
        (
            False,
            True,
            False,
            False,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tn_as_iterator_content_by_verse_for_book_then_lang,
        (
            False,
            False,
            True,
            True,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tq_as_iterator_content_by_verse_for_book_then_lang,
        (
            False,
            False,
            True,
            False,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tq_as_iterator_content_by_verse_for_book_then_lang,
        (
            False,
            False,
            False,
            True,
            # False,
            model.AssemblySubstrategyEnum.VERSE,
        ): assemble_tw_as_iterator_content_by_verse_for_book_then_lang,
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
            # True if ta_resources else False,
            assembly_substrategy_kind,
        )
    ]


def assemble_content_by_lang_then_book(
    book_content_units: Iterable[model.BookContent],
    language_fmt_str: str = settings.LANGUAGE_FMT_STR,
    book_fmt_str: str = settings.BOOK_FMT_STR,
    default_assembly_substrategy: model.AssemblySubstrategyEnum = settings.DEFAULT_ASSEMBLY_SUBSTRATEGY,
) -> Iterable[str]:
    """
    Assemble by language then by book in lexicographical order before
    delegating more atomic ordering/interleaving to an assembly
    sub-strategy.
    """
    book_units_sorted_by_language = sorted(
        book_content_units,
        key=lambda book_content_unit: book_content_unit.lang_name,
    )
    language: str
    for language, group_by_lang in itertools.groupby(
        book_units_sorted_by_language,
        lambda book_content_unit: book_content_unit.lang_name,
    ):
        yield language_fmt_str.format(language)

        # For groupby's sake, we need to first sort
        # group_by_lang before doing a groupby operation on it so that
        # resources will be clumped together by resource code, i.e.,
        # by language, otherwise a new group will be created every time a new
        # resource_code is sequentially encountered.
        book_content_units_sorted_by_book = sorted(
            group_by_lang,
            key=lambda book_content_unit: book_content_unit.resource_code,
        )
        for book, book_content_units_grouped_by_book in itertools.groupby(
            book_content_units_sorted_by_book,
            lambda book_content_unit: book_content_unit.resource_code,
        ):
            yield book_fmt_str.format(bible_books.BOOK_NAMES[book])

            # Save grouper generator values in list since it will get exhausted
            # when used and exhausted generators cannot be reused.
            book_content_units_ = list(book_content_units_grouped_by_book)
            usfm_book_content_unit: Optional[
                model.USFMBook
            ] = first_usfm_book_content_unit(book_content_units_)
            tn_book_content_unit_: Optional[model.TNBook] = tn_book_content_unit(
                book_content_units_
            )
            tq_book_content_unit_: Optional[model.TQBook] = tq_book_content_unit(
                book_content_units_
            )
            tw_book_content_unit_: Optional[model.TWBook] = tw_book_content_unit(
                book_content_units_
            )
            # ta_resource: Optional[TAResource] = _ta_resource(resources)
            usfm_book_content_unit2: Optional[
                model.USFMBook
            ] = second_usfm_book_content_unit(book_content_units_)

            # We've got the resources, now we can use the sub-strategy factory
            # method to choose the right function to use from here on out.
            assembly_sub_strategy = assembly_sub_strategy_factory(
                usfm_book_content_unit,
                tn_book_content_unit_,
                tq_book_content_unit_,
                tw_book_content_unit_,
                # ta_resource,
                usfm_book_content_unit2,
                default_assembly_substrategy,
            )

            logger.debug("assembly_sub_strategy: %s", str(assembly_sub_strategy))

            # Now that we have the sub-strategy, let's run it and
            # generate the HTML output.
            yield from assembly_sub_strategy(
                usfm_book_content_unit,
                tn_book_content_unit_,
                tq_book_content_unit_,
                tw_book_content_unit_,
                # ta_resource,
                usfm_book_content_unit2,
                # Currently there is only one sub-strategy so we just get it from a
                # config value. If we get more later then we'll thread the user's choice
                # as a param through method/functions.
                default_assembly_substrategy,
            )


def assemble_content_by_book_then_lang(
    book_content_units: Iterable[model.BookContent],
    book_as_grouper_fmt_str: str = settings.BOOK_AS_GROUPER_FMT_STR,
    default_assembly_substrategy: model.AssemblySubstrategyEnum = settings.DEFAULT_ASSEMBLY_SUBSTRATEGY,
) -> Iterable[str]:
    """
    Assemble by book then by language in alphabetic order before
    delegating more atomic ordering/interleaving to an assembly
    sub-strategy.
    """
    book_content_units_sorted_by_book = sorted(
        book_content_units,
        key=lambda book_content_unit: book_content_unit.resource_code,
    )
    book: str
    for book, group_by_book in itertools.groupby(
        book_content_units_sorted_by_book,
        lambda book_content_unit: book_content_unit.resource_code,
    ):
        yield book_as_grouper_fmt_str.format(bible_books.BOOK_NAMES[book])

        # Save grouper generator values in list since it will get exhausted
        # when used and exhausted generators cannot be reused.
        book_content_units_grouped_by_book = list(group_by_book)
        usfm_book_content_units: Sequence[model.USFMBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, model.USFMBook)
        ]
        tn_book_content_units: Sequence[model.TNBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, model.TNBook)
        ]
        tq_book_content_units: Sequence[model.TQBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, model.TQBook)
        ]
        tw_book_content_units: Sequence[model.TWBook] = [
            book_content_unit
            for book_content_unit in book_content_units_grouped_by_book
            if isinstance(book_content_unit, model.TWBook)
        ]
        # ta_resources: list[TAResource] = [
        #     resource for resource in resources if isinstance(resource, TAResource)
        # ]

        # We've got the resources, now we can use the sub-strategy factory
        # method to choose the right function to use from here on out.
        assembly_sub_strategy_for_book_then_lang = assembly_sub_strategy_factory_for_book_then_lang(
            usfm_book_content_units,
            tn_book_content_units,
            tq_book_content_units,
            tw_book_content_units,
            # ta_resources,
            default_assembly_substrategy,
        )

        logger.debug(
            "assembly_sub_strategy_for_book_then_lang: %s",
            str(assembly_sub_strategy_for_book_then_lang),
        )

        # Now that we have the sub-strategy, let's run it and
        # generate the HTML output.
        yield from assembly_sub_strategy_for_book_then_lang(
            usfm_book_content_units,
            tn_book_content_units,
            tq_book_content_units,
            tw_book_content_units,
            # ta_resources,
            default_assembly_substrategy,
        )


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
# strategy algo puts that USFM resource in usfm_book_content_unit position rather
# than usfm_book_content_unit2 position. If two USFM resources are requested then
# the second one in the DocumentRequest gets put in usfm_book_content_unit2
# position. Only the first USFM resource in the DocumentRequest has any
# subsequent TN, TQ, TW, and TA resources referencing it. A second
# USFMResource, e.g., udb, stands alone without referencing resources.
# This seems to work out fine in practice, but may be changed later by
# forcing usfm_book_content_unit to be of a particular resource_type, e.g., ulb,
# cuv, nav, and usfm_book_content_unit2 to be of another, e.g., udb.


def assemble_usfm_as_iterator_content_by_verse(
    usfm_book_content_unit: Optional[model.USFMBook],
    tn_book_content_unit: Optional[model.TNBook],
    tq_book_content_unit: Optional[model.TQBook],
    tw_book_content_unit: Optional[model.TWBook],
    # ta_resource: Optional[TAResource],
    usfm_book_content_unit2: Optional[model.USFMBook],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
    resource_type_name_fmt_str: str = settings.RESOURCE_TYPE_NAME_FMT_STR,
    resource_type_name_with_ref_fmt_str: str = settings.RESOURCE_TYPE_NAME_WITH_REF_FMT_STR,
    footnotes_heading: model.HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[model.HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein at least one
    USFM resource (e.g., ulb, nav, cuv, etc.) exists, and TN, TQ, TW,
    and a second USFM (e.g., probably always udb) may exist. If only
    one USFM exists then it will be used as the first
    USFM resource even if it is of udb resource type. Non-USFM
    resources, e.g., TN, TQ, TW, and TA will reference (and link where
    applicable) the first USFM resource and come after it in the
    interleaving strategy. The second USFM resource is displayed last
    in this interleaving strategy.
    """
    if tn_book_content_unit:
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield model.HtmlContent(book_intro)

    if usfm_book_content_unit:
        # Scripture type for usfm_book_content_unit, e.g., ulb, cuv, nav, reg, etc.
        yield model.HtmlContent(
            resource_type_name_fmt_str.format(usfm_book_content_unit.resource_type_name)
        )
        for (
            chapter_num,
            chapter,
        ) in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = model.HtmlContent("")
            chapter_heading = chapter.chapter_content[0]
            yield chapter_heading
            tn_verses: Optional[dict[str, model.HtmlContent]] = None
            tq_verses: Optional[dict[str, model.HtmlContent]] = None
            if tn_book_content_unit:
                # Add the translation notes chapter intro.
                yield chapter_intro(tn_book_content_unit, chapter_num)

                tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # PEP526 disallows declaration of types in for loops.
            verse_num: str
            verse: model.HtmlContent
            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.chapter_verses.items():
                # Add header
                yield model.HtmlContent(
                    resource_type_name_with_ref_fmt_str.format(
                        usfm_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                    )
                )

                # Add scripture verse
                yield verse
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
            if chapter.chapter_footnotes:
                yield footnotes_heading
                yield chapter.chapter_footnotes
        if tw_book_content_unit:
            # Add the translation words definition section.
            yield from translation_words_section(tw_book_content_unit)

    if usfm_book_content_unit2:
        # Scripture type for usfm_book_content_unit2, e.g., udb
        yield model.HtmlContent(
            resource_type_name_fmt_str.format(
                usfm_book_content_unit2.resource_type_name
            )
        )

        # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
        for (
            chapter_num_,
            chapter_,
        ) in usfm_book_content_unit2.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = model.HtmlContent("")
            chapter_heading = chapter_.chapter_content[0]
            yield chapter_heading
            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter_.chapter_verses.items():
                # Add header
                yield model.HtmlContent(
                    resource_type_name_with_ref_fmt_str.format(
                        usfm_book_content_unit2.resource_type_name,
                        chapter_num_,
                        verse_num,
                    )
                )

                # Add scripture verse
                yield verse


def assemble_usfm_tq_tw_content_by_verse(
    usfm_book_content_unit: Optional[model.USFMBook],
    tn_book_content_unit: Optional[model.TNBook],
    tq_book_content_unit: Optional[model.TQBook],
    tw_book_content_unit: Optional[model.TWBook],
    # ta_resource: Optional[TAResource],
    usfm_book_content_unit2: Optional[model.USFMBook],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
    resource_type_name_with_ref_fmt_str: str = settings.RESOURCE_TYPE_NAME_WITH_REF_FMT_STR,
    footnotes_heading: model.HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[model.HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM, TQ,
    and TW exist.
    """

    if usfm_book_content_unit:
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = model.HtmlContent("")
            chapter_heading = chapter.chapter_content[0]
            yield chapter_heading

            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # PEP526 disallows declaration of types in for loops.
            verse_num: str
            verse: model.HtmlContent
            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.chapter_verses.items():
                # Add header
                yield model.HtmlContent(
                    resource_type_name_with_ref_fmt_str.format(
                        usfm_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                    )
                )

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
            if chapter.chapter_footnotes:
                yield footnotes_heading
                yield chapter.chapter_footnotes
    if tw_book_content_unit:
        # Add the translation words definition section.
        yield from translation_words_section(tw_book_content_unit)


def assemble_usfm_tw_content_by_verse(
    usfm_book_content_unit: Optional[model.USFMBook],
    tn_book_content_unit: Optional[model.TNBook],
    tq_book_content_unit: Optional[model.TQBook],
    tw_book_content_unit: Optional[model.TWBook],
    # ta_resource: Optional[TAResource],
    usfm_book_content_unit2: Optional[model.USFMBook],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
    resource_type_name_with_ref_fmt_str: str = settings.RESOURCE_TYPE_NAME_WITH_REF_FMT_STR,
    footnotes_heading: model.HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[model.HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein USFM and TW
    exist.
    """

    if usfm_book_content_unit:
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = model.HtmlContent("")
            chapter_heading = chapter.chapter_content[0]
            yield chapter_heading

            # PEP526 disallows declaration of types in for
            # loops, but allows this.
            verse_num: str
            verse: model.HtmlContent
            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.chapter_verses.items():
                # Add scripture verse header
                yield model.HtmlContent(
                    resource_type_name_with_ref_fmt_str.format(
                        usfm_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                    )
                )

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
            if chapter.chapter_footnotes:
                yield footnotes_heading
                yield chapter.chapter_footnotes
    if tw_book_content_unit:
        # Add the translation words definition section.
        yield from translation_words_section(tw_book_content_unit)


def assemble_usfm_tq_content_by_verse(
    usfm_book_content_unit: Optional[model.USFMBook],
    tn_book_content_unit: Optional[model.TNBook],
    tq_book_content_unit: Optional[model.TQBook],
    tw_book_content_unit: Optional[model.TWBook],
    # ta_resource: Optional[TAResource],
    usfm_book_content_unit2: Optional[model.USFMBook],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
    resource_type_name_with_ref_fmt_str: str = settings.RESOURCE_TYPE_NAME_WITH_REF_FMT_STR,
    footnotes_heading: model.HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[model.HtmlContent]:
    """Construct the HTML for a 'by verse' strategy wherein only USFM and TQ exist."""

    if usfm_book_content_unit:
        for chapter_num, chapter in usfm_book_content_unit.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = model.HtmlContent("")
            chapter_heading = chapter.chapter_content[0]
            yield chapter_heading

            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # PEP526 disallows declaration of types in for
            # loops, but allows this.
            verse_num: str
            verse: model.HtmlContent
            # Now let's interleave USFM verse with its
            # translation note if available.
            for verse_num, verse in chapter.chapter_verses.items():
                # Add scripture verse heading
                yield model.HtmlContent(
                    resource_type_name_with_ref_fmt_str.format(
                        usfm_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                    )
                )

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
            if chapter.chapter_footnotes:
                yield footnotes_heading
                yield chapter.chapter_footnotes


def assemble_tn_as_iterator_content_by_verse(
    usfm_book_content_unit: Optional[model.USFMBook],
    tn_book_content_unit: Optional[model.TNBook],
    tq_book_content_unit: Optional[model.TQBook],
    tw_book_content_unit: Optional[model.TWBook],
    # ta_resource: Optional[TAResource],
    usfm_book_content_unit2: Optional[model.USFMBook],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
    resource_type_name_with_ref_fmt_str: str = settings.RESOURCE_TYPE_NAME_WITH_REF_FMT_STR,
) -> Iterable[model.HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TN, TQ,
    and TW exists.
    """
    if tn_book_content_unit:
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield book_intro

        for chapter_num in tn_book_content_unit.chapters:
            # How to get chapter heading for Translation notes when USFM is not
            # requested? For now we'll use non-localized chapter heading. Add in the
            # USFM chapter heading.
            yield model.HtmlContent(
                chapter_header_fmt_str.format(
                    tn_book_content_unit.lang_code,
                    bible_books.BOOK_NUMBERS[tn_book_content_unit.resource_code].zfill(
                        3
                    ),
                    str(chapter_num).zfill(3),
                    chapter_num,
                )
            )

            # Add the translation notes chapter intro.
            yield chapter_intro(tn_book_content_unit, chapter_num)

            tn_verses = verses_for_chapter_tn(tn_book_content_unit, chapter_num)
            tq_verses = None
            if tq_book_content_unit:
                tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # PEP526 disallows declaration of types in for loops, but allows this.
            verse_num: str
            verse: model.HtmlContent
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

    if tw_book_content_unit:
        # Add the translation words definition section.
        yield from translation_words_section(
            tw_book_content_unit, include_uses_section=False
        )
    if usfm_book_content_unit2:
        # Add the usfm_book_content_unit2, e.g., udb, scripture verses.
        for (
            chapter_num,
            chapter,
        ) in usfm_book_content_unit2.chapters.items():
            # Add in the USFM chapter heading.
            chapter_heading = model.HtmlContent("")
            chapter_heading = chapter.chapter_content[0]
            yield chapter_heading
            # Now let's interleave USFM verse with its translation note, translation
            # questions, and translation words if available.
            for verse_num, verse in chapter.chapter_verses.items():
                # Add header
                yield model.HtmlContent(
                    resource_type_name_with_ref_fmt_str.format(
                        usfm_book_content_unit2.resource_type_name,
                        chapter_num,
                        verse_num,
                    )
                )

                # Add scripture verse
                yield verse


def assemble_tq_content_by_verse(
    usfm_book_content_unit: Optional[model.USFMBook],
    tn_book_content_unit: Optional[model.TNBook],
    tq_book_content_unit: Optional[model.TQBook],
    tw_book_content_unit: Optional[model.TWBook],
    # ta_resource: Optional[TAResource],
    usfm_book_content_unit2: Optional[model.USFMBook],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
) -> Iterable[model.HtmlContent]:
    """Construct the HTML for a 'by verse' strategy wherein only TQ exists."""
    # Make mypy happy. We know, due to how we got here, that book_content_unit objects are not None.

    if tq_book_content_unit:
        for chapter_num in tq_book_content_unit.chapters:
            # How to get chapter heading for Translation questions when there is
            # not USFM requested? For now we'll use non-localized chapter heading.
            # Add in the USFM chapter heading.
            yield model.HtmlContent(
                chapter_header_fmt_str.format(
                    tq_book_content_unit.lang_code,
                    bible_books.BOOK_NUMBERS[tq_book_content_unit.resource_code].zfill(
                        3
                    ),
                    str(chapter_num).zfill(3),
                    chapter_num,
                )
            )

            # Get TQ chapter verses
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # PEP526 disallows declaration of types in for loops, but allows this.
            verse_num: str
            verse: model.HtmlContent
            # Now let's get all the verse translation notes available.
            if tq_verses:
                for verse_num, verse in tq_verses.items():
                    yield from format_tq_verse(
                        tq_book_content_unit.resource_type_name,
                        chapter_num,
                        verse_num,
                        verse,
                    )


def assemble_tq_tw_content_by_verse(
    usfm_book_content_unit: Optional[model.USFMBook],
    tn_book_content_unit: Optional[model.TNBook],
    tq_book_content_unit: Optional[model.TQBook],
    tw_book_content_unit: Optional[model.TWBook],
    # ta_resource: Optional[TAResource],
    usfm_book_content_unit2: Optional[model.USFMBook],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
    chapter_header_fmt_str: str = settings.CHAPTER_HEADER_FMT_STR,
) -> Iterable[model.HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein only TQ and
    TW exists.
    """
    if tq_book_content_unit:
        for chapter_num in tq_book_content_unit.chapters:
            # How to get chapter heading for Translation questions when there is
            # not USFM requested? For now we'll use non-localized chapter heading.
            # Add in the USFM chapter heading.
            yield model.HtmlContent(
                chapter_header_fmt_str.format(
                    tq_book_content_unit.lang_code,
                    bible_books.BOOK_NUMBERS[tq_book_content_unit.resource_code].zfill(
                        3
                    ),
                    str(chapter_num).zfill(3),
                    chapter_num,
                )
            )

            # Get TQ chapter verses
            tq_verses = verses_for_chapter_tq(tq_book_content_unit, chapter_num)

            # PEP526 disallows declaration of types in for loops, but allows this.
            verse_num: str
            verse: model.HtmlContent
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
    if tw_book_content_unit:
        # Add the translation words definition section.
        yield from translation_words_section(
            tw_book_content_unit, include_uses_section=False
        )


def assemble_tw_content_by_verse(
    usfm_book_content_unit: Optional[model.USFMBook],
    tn_book_content_unit: Optional[model.TNBook],
    tq_book_content_unit: Optional[model.TQBook],
    tw_book_content_unit: Optional[model.TWBook],
    # ta_resource: Optional[TAResource],
    usfm_book_content_unit2: Optional[model.USFMBook],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> Iterable[model.HtmlContent]:
    """Construct the HTML for a 'by verse' strategy wherein only TW exists."""
    if tw_book_content_unit:
        # Add the translation words definition section.
        yield from translation_words_section(
            tw_book_content_unit, include_uses_section=False
        )


#########################################################################
# Assembly sub-strategy implementations for book then language strategy


def assemble_usfm_as_iterator_content_by_verse_for_book_then_lang(
    usfm_book_content_units: Sequence[model.USFMBook],
    tn_book_content_units: Sequence[model.TNBook],
    tq_book_content_units: Sequence[model.TQBook],
    tw_book_content_units: Sequence[model.TWBook],
    # ta_resources: list[TAResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
    resource_type_name_with_ref_fmt_str: str = settings.RESOURCE_TYPE_NAME_WITH_REF_FMT_STR,
    footnotes_heading: model.HtmlContent = settings.FOOTNOTES_HEADING,
) -> Iterable[model.HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein at least one
    USFM resource (e.g., ulb, nav, cuv, etc.) exists, and TN, TQ, and
    TW may exist.

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

    # Sort resources by language
    key = lambda resource: resource.lang_code
    usfm_book_content_units = sorted(usfm_book_content_units, key=key)
    tn_book_content_units = sorted(tn_book_content_units, key=key)
    tq_book_content_units = sorted(tq_book_content_units, key=key)
    tw_book_content_units = sorted(tw_book_content_units, key=key)
    # ta_resources = sorted(ta_resources, key=key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        # Add the book intro
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield model.HtmlContent(book_intro)

    # NOTE A note regarding chapter and verse pumps used in loops
    # below:
    #
    # Instead of usfm_book_content_units[0] being used by default as the chapter and
    # verse pump in the next loop, we could use the usfm_book_content_unit with the
    # most chapters or verses for the chapter_num or verse_num pump
    # respectively:
    #
    # usfm_with_most_chapters = max(
    #     usfm_book_content_units,
    #     key=lambda usfm_book_content_unit: usfm_book_content_unit.chapter_content
    # )
    #
    # and:
    #
    # usfm_with_most_verses = max(
    #     usfm_book_content_units,
    #     key=lambda usfm_book_content_unit: usfm_book_content_unit.chapter_content[
    #         chapter_num
    #     ].chapter_verses.items(),
    # )
    #
    # Care would need to be taken with subsequent logic if this is used. Why
    # even consider such a change? A: In order to realize the most amount of
    # content displayed to user.

    # NOTE Assumption (which may need to change): usfm_book_content_units[0] is the
    # right usfm_book_content_unit instance to use for chapter_num pump. However, if
    # usfm_book_content_unit[n] where n is not 0 has more chapters then it should
    # probably be used instead. Still thinking about this one. Hasn't been
    # an issue in practice so far. See note above about
    # usfm_with_most_chapters for a possible different approach.
    for chapter_num, chapter in usfm_book_content_units[0].chapters.items():
        # Add the first USFM resource's chapter heading. We ignore
        # chapter headings for other usfm_book_content_units because it would
        # be strange to have more than one chapter heading per chapter
        # for this assembly sub-strategy.
        chapter_heading = model.HtmlContent("")
        chapter_heading = chapter.chapter_content[0]
        yield model.HtmlContent(chapter_heading)

        # Add chapter intro for each language
        for tn_book_content_unit2 in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield model.HtmlContent(chapter_intro(tn_book_content_unit2, chapter_num))

        # NOTE If we add macro-weave feature, it would go here, see
        # notes for code.
        # Use the first usfm_book_content_unit as a verse_num pump
        for verse_num in (
            usfm_book_content_units[0]
            .chapters[chapter_num]
            .chapter_verses.keys()
            # See note above about usfm_with_most_verses for why this
            # is here. Here for possible future use.
            # usfm_with_most_verses.chapter_content[chapter_num].chapter_verses.items()
        ):
            # Add the interleaved USFM verses
            for usfm_book_content_unit in usfm_book_content_units:
                if (
                    chapter_num in usfm_book_content_unit.chapters
                    and verse_num
                    in usfm_book_content_unit.chapters[chapter_num].chapter_verses
                ):

                    # Add header
                    yield model.HtmlContent(
                        resource_type_name_with_ref_fmt_str.format(
                            usfm_book_content_unit.resource_type_name,
                            chapter_num,
                            verse_num,
                        )
                    )

                    # Add scripture verse
                    yield usfm_book_content_unit.chapters[chapter_num].chapter_verses[
                        verse_num
                    ]

            # Add the interleaved tn notes
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
                usfm_book_content_unit_: Optional[model.USFMBook]
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
                    in usfm_book_content_unit_.chapters[chapter_num].chapter_verses
                ):
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        usfm_book_content_unit_.chapters[chapter_num].chapter_verses[
                            verse_num
                        ],
                    )
                else:
                    logger.debug(
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
                ].chapter_footnotes
                if chapter_footnotes:
                    yield footnotes_heading
                    yield chapter_footnotes
            except KeyError:
                logger.debug(
                    "usfm_book_content_unit: %s, does not have chapter: %s",
                    usfm_book_content_unit,
                    chapter_num,
                )
                logger.exception("Caught exception:")

    # Add the translation word definitions
    for tw_book_content_unit in tw_book_content_units:
        # Add the translation words definition section.
        yield from translation_words_section(tw_book_content_unit)


def assemble_tn_as_iterator_content_by_verse_for_book_then_lang(
    usfm_book_content_units: Sequence[model.USFMBook],
    tn_book_content_units: Sequence[model.TNBook],
    tq_book_content_units: Sequence[model.TQBook],
    tw_book_content_units: Sequence[model.TWBook],
    # ta_resources: list[TAResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> Iterable[model.HtmlContent]:
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
    key = lambda resource: resource.lang_code
    usfm_book_content_units = sorted(usfm_book_content_units, key=key)
    tn_book_content_units = sorted(tn_book_content_units, key=key)
    tq_book_content_units = sorted(tq_book_content_units, key=key)
    tw_book_content_units = sorted(tw_book_content_units, key=key)
    # ta_resources = sorted(ta_resources, key=key)

    # Add book intros for each tn_book_content_unit
    for tn_book_content_unit in tn_book_content_units:
        # Add the book intro
        book_intro = tn_book_content_unit.intro_html
        book_intro = adjust_book_intro_headings(book_intro)
        yield model.HtmlContent(book_intro)

    # Use the first tn_book_content_unit as a chapter_num pump.
    for chapter_num in tn_book_content_units[0].chapters.keys():
        yield model.HtmlContent("Chapter {}".format(chapter_num))

        # Add chapter intro for each language
        for tn_book_content_unit in tn_book_content_units:
            # Add the translation notes chapter intro.
            yield from chapter_intro(tn_book_content_unit, chapter_num)

        # Use the first tn_book_content_unit as a verse_num pump
        for verse_num in (
            tn_book_content_units[0].chapters[chapter_num].verses_html.keys()
        ):
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
                usfm_book_content_unit_: Optional[model.USFMBook]
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
                    in usfm_book_content_unit_.chapters[chapter_num].chapter_verses
                ):
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        usfm_book_content_unit_.chapters[chapter_num].chapter_verses[
                            verse_num
                        ],
                    )

    # Add the translation word definitions
    for tw_book_content_unit in tw_book_content_units:
        # Add the translation words definition section.
        yield from translation_words_section(tw_book_content_unit)


def assemble_tq_as_iterator_content_by_verse_for_book_then_lang(
    usfm_book_content_units: Sequence[model.USFMBook],
    tn_book_content_units: Sequence[model.TNBook],
    tq_book_content_units: Sequence[model.TQBook],
    tw_book_content_units: Sequence[model.TWBook],
    # ta_resources: list[TAResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> Iterable[model.HtmlContent]:
    """
    Construct the HTML for a 'by verse' strategy wherein at least
    tq_book_content_units exists, and TQ, and TW may exist.
    """

    # Sort resources by language
    key = lambda resource: resource.lang_code
    usfm_book_content_units = sorted(usfm_book_content_units, key=key)
    tn_book_content_units = sorted(tn_book_content_units, key=key)
    tq_book_content_units = sorted(tq_book_content_units, key=key)
    tw_book_content_units = sorted(tw_book_content_units, key=key)
    # ta_resources = sorted(ta_resources, key=key)

    # Use the first tn_book_content_unit as a chapter_num pump.
    for chapter_num in tq_book_content_units[0].chapters.keys():
        yield model.HtmlContent("Chapter {}".format(chapter_num))

        # Use the first tq_book_content_unit as a verse_num pump
        for verse_num in (
            tq_book_content_units[0].chapters[chapter_num].verses_html.keys()
        ):
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
                usfm_book_content_unit_: Optional[model.USFMBook]
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
                    in usfm_book_content_unit_.chapters[chapter_num].chapter_verses
                ):
                    yield from translation_word_links(
                        tw_book_content_unit,
                        chapter_num,
                        verse_num,
                        usfm_book_content_unit_.chapters[chapter_num].chapter_verses[
                            verse_num
                        ],
                    )

    # Add the translation word definitions
    for tw_book_content_unit in tw_book_content_units:
        # Add the translation words definition section.
        yield from translation_words_section(tw_book_content_unit)


def assemble_tw_as_iterator_content_by_verse_for_book_then_lang(
    usfm_book_content_units: Sequence[model.USFMBook],
    tn_book_content_units: Sequence[model.TNBook],
    tq_book_content_units: Sequence[model.TQBook],
    tw_book_content_units: Sequence[model.TWBook],
    # ta_resources: list[TAResource],
    assembly_substrategy_kind: model.AssemblySubstrategyEnum,
) -> Iterable[model.HtmlContent]:
    """Construct the HTML for a only TW."""

    # Sort resources by language
    key = lambda resource: resource.lang_code
    usfm_book_content_units = sorted(usfm_book_content_units, key=key)
    tn_book_content_units = sorted(tn_book_content_units, key=key)
    tq_book_content_units = sorted(tq_book_content_units, key=key)
    tw_book_content_units = sorted(tw_book_content_units, key=key)
    # ta_resources = sorted(ta_resources, key=key)

    # Add the translation word definitions
    for tw_book_content_unit in tw_book_content_units:
        # Add the translation words definition section.
        yield from translation_words_section(
            tw_book_content_unit, include_uses_section=False
        )


######################
## Utility functions


def format_tq_verse(
    resource_type_name: str,
    chapter_num: int,
    verse_num: str,
    verse: model.HtmlContent,
    resource_type_name_with_ref_fmt_str: str = settings.RESOURCE_TYPE_NAME_WITH_REF_FMT_STR,
) -> Iterable[model.HtmlContent]:
    yield model.HtmlContent(
        resource_type_name_with_ref_fmt_str.format(
            resource_type_name, chapter_num, verse_num
        )
    )

    # Change H1 HTML elements to H4 HTML elements in each translation
    # question.
    yield model.HtmlContent(re.sub(H1, H4, verse))


def first_usfm_book_content_unit(
    book_content_units: Sequence[model.BookContent],
) -> Optional[model.USFMBook]:
    """
    Return the first USFMBook instance, if any, contained in book_content_units,
    else return None.
    """
    usfm_books = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, model.USFMBook)
        # NOTE If you wanted to force only certain USFM resource types
        # in the usfm_book_content_unit position then you could do something
        # like:
        # resource for resource in resources if isinstance(resource,
        # USFMResource) and resource.resource_type in ["ulb", "cuv",
        # "nav", "ugnt", "uhb", "rsb", "f10", "blv", "ust"]
        # You'd have to choose which USFM resource types based on
        # which ones make sense for TN, TQ, TW, and TA to reference
        # them.
        # NOTE See note on _second_usfm_book_content_unit for what else
        # would need to be done to support this alternative.
    ]
    return usfm_books[0] if usfm_books else None


def second_usfm_book_content_unit(
    book_content_units: Sequence[model.BookContent],
) -> Optional[model.USFMBook]:
    """
    Return the second USFMBook instance, if any, contained in book_content_units,
    else return None.
    """
    usfm_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, model.USFMBook)
    ]
    return usfm_book_content_units[1] if len(usfm_book_content_units) > 1 else None
    # NOTE This is just a sketch of what you could do if you wanted to
    # only allow certain USFM resource types to be in usfm_book_content_unit
    # position in the interleaving strategy. Currently, the
    # interleaving strategy shows usfm_book_content_unit at the end of other
    # resources in each chapter, i.e., no TN, TQ, TW, or TA resource
    # referencing it.
    # usfm_book_content_units = [
    #     resource for resource in resources if isinstance(resource,
    #     USFMResource) and resource.resource_type in ["udb"]
    # ]
    # return usfm_book_content_units[0] if usfm_book_content_units else None


def tn_book_content_unit(
    book_content_units: Sequence[model.BookContent],
) -> Optional[model.TNBook]:
    """
    Return the TNBook instance, if any, contained in book_content_units,
    else return None.
    """
    tn_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, model.TNBook)
    ]
    return tn_book_content_units[0] if tn_book_content_units else None


def tw_book_content_unit(
    book_content_units: Sequence[model.BookContent],
) -> Optional[model.TWBook]:
    """
    Return the TWBook instance, if any, contained in book_content_units,
    else return None.
    """
    tw_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, model.TWBook)
    ]
    return tw_book_content_units[0] if tw_book_content_units else None


def tq_book_content_unit(
    book_content_units: Sequence[model.BookContent],
) -> Optional[model.TQBook]:
    """
    Return the TQBook instance, if any, contained in book_content_units,
    else return None.
    """
    tq_book_content_units = [
        book_content_unit
        for book_content_unit in book_content_units
        if isinstance(book_content_unit, model.TQBook)
    ]
    return tq_book_content_units[0] if tq_book_content_units else None


def adjust_book_intro_headings(book_intro: str) -> model.HtmlContent:
    """Change levels on headings."""
    # Move the H2 out of the way, we'll deal with it last.
    book_intro = re.sub(H2, H6, book_intro)
    book_intro = re.sub(H1, H2, book_intro)
    book_intro = re.sub(H3, H4, book_intro)
    # Now adjust the temporary H6s.
    return model.HtmlContent(re.sub(H6, H3, book_intro))


def adjust_chapter_intro_headings(chapter_intro: str) -> model.HtmlContent:
    """Change levels on headings."""
    # Move the H4 out of the way, we'll deal with it last.
    chapter_intro = re.sub(H4, H6, chapter_intro)
    chapter_intro = re.sub(H3, H4, chapter_intro)
    chapter_intro = re.sub(H1, H3, chapter_intro)
    chapter_intro = re.sub(H2, H4, chapter_intro)
    # Now adjust the temporary H6s.
    return model.HtmlContent(re.sub(H6, H5, chapter_intro))


def chapter_intro(
    tn_book_content_unit: model.TNBook, chapter_num: int
) -> model.HtmlContent:
    """Get the chapter intro."""
    if tn_book_content_unit and chapter_num in tn_book_content_unit.chapters:
        chapter_intro = tn_book_content_unit.chapters[chapter_num].intro_html
    else:
        chapter_intro = model.HtmlContent("")
    # NOTE I am not sure that the 'Links:' section of chapter
    # intro makes sense anymore with the way documents
    # are interleaved.
    # Remove the Links: section of the markdown.
    # chapter_intro = markdown_utils.remove_md_section(chapter_intro, "Links:")
    return adjust_chapter_intro_headings(chapter_intro)


def format_tn_verse(
    book_content_unit: model.TNBook,
    chapter_num: int,
    verse_num: str,
    verse: model.HtmlContent,
    format_str: str = settings.TN_RESOURCE_TYPE_NAME_WITH_ID_AND_REF_FMT_STR,
) -> Iterable[model.HtmlContent]:
    """
    This is a slightly different form of TNResource.tn_verse that is used
    when no USFM has been requested.
    """
    yield model.HtmlContent(
        format_str.format(
            book_content_unit.lang_code,
            bible_books.BOOK_NUMBERS[book_content_unit.resource_code].zfill(3),
            str(chapter_num).zfill(3),
            verse_num.zfill(3),
            book_content_unit.resource_type_name,
            chapter_num,
            verse_num,
        )
    )

    # Change H1 HTML elements to H4 HTML elements in each translation note.
    yield model.HtmlContent(re.sub(H1, H4, verse))


def verses_for_chapter_tn(
    book_content_unit: model.TNBook, chapter_num: int
) -> Optional[dict[str, model.HtmlContent]]:
    """
    Return the HTML for verses that are in the chapter with
    chapter_num.
    """
    verses_html = None
    if chapter_num in book_content_unit.chapters:
        verses_html = book_content_unit.chapters[chapter_num].verses_html
    return verses_html


def verses_for_chapter_tq(
    book_content_unit: model.TQBook,
    chapter_num: int,
) -> Optional[dict[str, model.HtmlContent]]:
    """Return the HTML for verses in chapter_num."""
    verses_html = None
    if chapter_num in book_content_unit.chapters:
        verses_html = book_content_unit.chapters[chapter_num].verses_html
    return verses_html


def translation_word_links(
    book_content_unit: model.TWBook,
    chapter_num: int,
    verse_num: str,
    verse: model.HtmlContent,
    resource_type_name_with_ref_fmt_str: str = settings.RESOURCE_TYPE_NAME_WITH_REF_FMT_STR,
    unordered_list_begin_str: str = settings.UNORDERED_LIST_BEGIN_STR,
    translation_word_list_item_fmt_str: str = settings.TRANSLATION_WORD_LIST_ITEM_FMT_STR,
    unordered_list_end_str: str = settings.UNORDERED_LIST_END_STR,
) -> Iterable[model.HtmlContent]:
    """
    Add the translation word links section which provides links from words
    used in the current verse to their definition.
    """
    uses: list[model.TWUse] = []
    name_content_pair: model.TWNameContentPair
    for name_content_pair in book_content_unit.name_content_pairs:
        # This checks that the word occurs as an exact sub-string in
        # the verse.
        if re.search(
            r"\b{}\b".format(re.escape(name_content_pair.localized_word)), verse
        ):
            use = model.TWUse(
                lang_code=book_content_unit.lang_code,
                book_id=book_content_unit.resource_code,
                book_name=bible_books.BOOK_NAMES[book_content_unit.resource_code],
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
        # Add header
        yield model.HtmlContent(
            resource_type_name_with_ref_fmt_str.format(
                book_content_unit.resource_type_name, chapter_num, verse_num
            )
        )

        # Start list formatting
        yield unordered_list_begin_str
        # Append word links.
        uses_list_items = [
            translation_word_list_item_fmt_str.format(
                book_content_unit.lang_code,
                use.localized_word,
                use.localized_word,
            )
            for use in list(tw_utils.uniq(uses))  # Get the unique uses
        ]
        yield model.HtmlContent("\n".join(uses_list_items))
        # End list formatting
        yield unordered_list_end_str


def translation_words_section(
    book_content_unit: model.TWBook,
    include_uses_section: bool = True,
    resource_type_name_fmt_str: str = settings.RESOURCE_TYPE_NAME_FMT_STR,
    opening_h3_fmt_str: str = settings.OPENING_H3_FMT_STR,
    opening_h3_with_id_fmt_str: str = settings.OPENING_H3_WITH_ID_FMT_STR,
) -> Iterable[model.HtmlContent]:
    """
    Build and return the translation words definition section, i.e.,
    the list of all translation words for this language, book
    combination. Include a 'Uses:' section that points from the
    translation word back to the verses which include the translation
    word if include_uses_section is True.
    """
    yield model.HtmlContent(
        resource_type_name_fmt_str.format(book_content_unit.resource_type_name)
    )

    for name_content_pair in book_content_unit.name_content_pairs:
        # NOTE Another approach to including all translation words would be to
        # only include words in the translation section which occur in current
        # lang_code, book verses. The problem with this is that translation note
        # 'See also' sections often refer to translation words that are not part
        # of the lang_code/book content and thus those links are dead unless we
        # include them even if they don't have any 'Uses' section. In other
        # words, by limiting the translation words we limit the ability of those
        # using the interleaved document to gain deeper understanding of the
        # interrelationships of words.

        # Make linking work: have to add ID to tags for anchor
        # links to work.
        name_content_pair.content = model.HtmlContent(
            name_content_pair.content.replace(
                opening_h3_fmt_str.format(name_content_pair.localized_word),
                opening_h3_with_id_fmt_str.format(
                    book_content_unit.lang_code,
                    name_content_pair.localized_word,
                    name_content_pair.localized_word,
                ),
            )
        )
        uses_section_ = model.HtmlContent("")

        # See comment above.
        if (
            include_uses_section
            and name_content_pair.localized_word in book_content_unit.uses
        ):
            uses_section_ = uses_section(
                book_content_unit.uses[name_content_pair.localized_word]
            )
            name_content_pair.content = model.HtmlContent(
                name_content_pair.content + uses_section_
            )
        yield name_content_pair.content


def uses_section(
    uses: Sequence[model.TWUse],
    translation_word_verse_section_header_str: str = settings.TRANSLATION_WORD_VERSE_SECTION_HEADER_STR,
    unordered_list_begin_str: str = settings.UNORDERED_LIST_BEGIN_STR,
    translation_word_verse_ref_item_fmt_str: str = settings.TRANSLATION_WORD_VERSE_REF_ITEM_FMT_STR,
    unordered_list_end_str: str = settings.UNORDERED_LIST_END_STR,
) -> model.HtmlContent:
    """
    Construct and return the 'Uses:' section which comes at the end of
    a translation word definition and wherein each item points to
    verses (as targeted by lang_code, book_id, chapter_num, and
    verse_num) wherein the word occurs.
    """
    html: list[model.HtmlContent] = []
    html.append(translation_word_verse_section_header_str)
    html.append(unordered_list_begin_str)
    for use in uses:
        html_content_str = model.HtmlContent(
            translation_word_verse_ref_item_fmt_str.format(
                use.lang_code,
                bible_books.BOOK_NUMBERS[use.book_id].zfill(3),
                str(use.chapter_num).zfill(3),
                str(use.verse_num).zfill(3),
                bible_books.BOOK_NAMES[use.book_id],
                use.chapter_num,
                use.verse_num,
            )
        )
        html.append(html_content_str)
    html.append(unordered_list_end_str)
    return model.HtmlContent("\n".join(html))