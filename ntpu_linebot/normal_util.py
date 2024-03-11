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
