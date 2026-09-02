from concurrent.futures import Future, as_completed

from rich.progress import (
    Progress,
)

from app.models import Record
from app.services import Excel


def excel_worker(
    _futures: list[Future[list[list[Record]]]], excel: Excel, progress: Progress
):
    results = [
        results for futures in as_completed(_futures) for results in futures.result()
    ]

    total = sum([len(result) for result in results])

    task = progress.add_task("writer", total=total)

    for records in results:
        progress.advance(task)
        excel.write(records)
