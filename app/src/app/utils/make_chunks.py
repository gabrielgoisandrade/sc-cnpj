from typing import Any

from app.logger import log


def make_chunks(iterable: list[Any], chunk_size=1_000):
    chunks = [iterable[i : i + chunk_size] for i in range(0, len(iterable), chunk_size)]

    log.info(f"Created a chunk with {chunk_size} items each")
    return chunks
