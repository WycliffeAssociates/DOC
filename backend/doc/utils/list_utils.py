from typing import Sequence, TypeVar


T = TypeVar("T", tuple[str, str], tuple[str, str, bool])


def unique_tuples(lst: list[T]) -> list[T]:
    """
    >>> data_2: list[tuple[str, str]] = [("a", "b"), ("c", "d"), ("a", "b"), ("e", "f")]
    >>> data_3: list[tuple[str, str, bool]] = [("x", "y", True), ("x", "y", False), ("a", "b", True), ("x", "y", True)]
    >>> assert unique_tuples(data_2) == [('a', 'b'), ('c', 'd'), ('e', 'f')]
    >>> assert unique_tuples(data_3) == [('x', 'y', True), ('x', 'y', False), ('a', 'b', True)]
    """
    return list(dict.fromkeys(lst))


def unique_book_codes(lst: list[T]) -> list[T]:
    """
    >>> input_list = [("lev", "value1"), ("lev", "value2", True), ("abc", "value3"), ("abc", "value4", False)]
    >>> result = unique_tuples(input_list)
    [('lev', 'value1'), ('abc', 'value3')]
    """
    seen = {}
    for item in lst:
        key = item[0]
        if key not in seen:
            seen[key] = item
    return list(seen.values())


def unique_list_of_strings(
    elements: Sequence[tuple[str, str]]
) -> Sequence[tuple[str, str]]:
    unique_strs = []
    added_strs = set()
    for key, val in elements:
        if key not in added_strs:
            unique_strs.append((key, val))
            added_strs.add(key)
    return unique_strs
