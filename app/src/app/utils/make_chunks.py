from typing import Any


def make_chunks(iterable: list[Any], chunk_size=1_000):
    return [iterable[i : i + chunk_size] for i in range(0, len(iterable), chunk_size)]
