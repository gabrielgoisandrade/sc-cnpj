from concurrent.futures import Future, as_completed

from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    Progress,
)

from app.models import Record
from app.services import Excel


# TODO: remover TODO o rich daqui e separar num arquivo próprio de ui.
def excel_worker(_futures: list[Future[list[list[Record]]]], excel: Excel):
    progress = Progress(expand=True)
    task = progress.add_task("writer", total=None, visible=False)

    panel = Panel(title="Writing", renderable=progress)

    with Live(panel):
        results = [
            results
            for futures in as_completed(_futures)
            for results in futures.result()
        ]

        total = sum([len(result) for result in results])
        progress.reset(task, total=total, visible=True)

        for records in results:
            excel.write(records)
            progress.advance(task)
