from typing import TypeVar

T = TypeVar("T", tuple[str, str], tuple[str, str, bool])


def unique_tuples(lst: list[T]) -> list[T]:
    """
    >>> data_2: list[tuple[str, str]] = [("a", "b"), ("c", "d"), ("a", "b"), ("e", "f")]
    >>> data_3: list[tuple[str, str, bool]] = [("x", "y", True), ("x", "y", False), ("a", "b", True), ("x", "y", True)]
    >>> assert unique_tuples(data_2) == [('a', 'b'), ('c', 'd'), ('e', 'f')]
    >>> assert unique_tuples(data_3) == [('x', 'y', True), ('x', 'y', False), ('a', 'b', True)]
    """
    return list(dict.fromkeys(lst))
