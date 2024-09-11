from typing import Iterator, Sequence

from annotated_types import T


def partition(arr: Sequence[T], size: int) -> Iterator[Sequence[T]]:
    """
    Splits an iterable into groups of size.

    Args:
        arr (Sequence): The sequence to split.
        size (int): The size of each group.

    Returns:
        Iterator[Sequence]: An iterator of groups of size.
    """

    for i in range(0, len(arr), size):
        yield arr[i : i + size]

def list_to_regex(arr: Sequence[str]) -> str:
    """
    Generates a regular expression pattern that matches any string
    that is preceded by any of the strings in the input array.

    Args:
        arr (Sequence[str]): A sequence of strings that.

    Returns:
        str: A regular expression pattern that matches any string that is
        preceded by any of the strings in the input array.
    """

    return r"(?<=(" + r"|".join(rf"(?<={c})" for c in arr) + r")[ +]).*"
