import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from rich import print as fprint
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

from app.logger import create_log, log
from app.models import Record
from app.services import Excel
from app.state import thread_state
from app.utils import make_chunks

from .excel_worker import excel_worker
from .selenium_worker import selenium_worker


class LogView:
    def __init__(self, logs: deque[Text]):
        self.logs = logs

    def __rich__(self):
        return Group(*self.logs)


def initializer(worker_progresses: list[Progress], worker_log: list[Text]):
    worker_name = threading.current_thread().name
    worker_id = worker_name.split("_")[1]
    worker_name = worker_name.replace(worker_id, str(int(worker_id) + 1))

    thread_state.log = create_log(worker_name)

    thread_state.visual_log = worker_log[int(worker_id)]

    thread_state.log.info("Created worker")

    progress = worker_progresses[int(worker_id)]

    thread_state.progress = progress
    thread_state.worker_task = progress.add_task(worker_name, total=None)


def create_workers():
    path = r"C:\Users\gabriel.andrade\Documents\cnpjs_export.xlsx"

    excel = Excel(path)
    excel.load()

    column = excel.sheet["A"][1:20]

    cnpjs = [Record(cell.row, cell.value) for cell in column]

    log.info(f"Found {len(cnpjs)} values from spreadsheet")

    chunks = make_chunks(cnpjs, 5)

    progress_bars = [
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        MofNCompleteColumn("/"),
        TimeRemainingColumn(elapsed_when_finished=True, compact=True),
    ]

    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)

    worker_progresses = [
        Progress(*progress_bars, expand=True, auto_refresh=False),
        Progress(*progress_bars, expand=True, auto_refresh=False),
        Progress(*progress_bars, expand=True, auto_refresh=False),
        Progress(*progress_bars, expand=True, auto_refresh=False),
    ]

    worker_logs: list[deque[Text]] = [deque(maxlen=5) for _ in range(4)]

    worker_views = [
        Panel(
            Group(worker_progresses[i], LogView(worker_logs[i])),
            title=f"Worker_{i + 1}",
            title_align="left",
            height=10,
        )
        for i in range(4)
    ]

    grid.add_row(worker_views[0], worker_views[1])
    grid.add_row(worker_views[2], worker_views[3])

    with Live(grid):
        thread_props = {
            "max_workers": 4,
            "thread_name_prefix": "worker",
            "initializer": initializer,
            "initargs": (worker_progresses, worker_logs),
        }

        with ThreadPoolExecutor(**thread_props) as executor:
            futures = []

            for chunk in chunks:
                futures.append(executor.submit(selenium_worker, chunk))

    excel_worker(futures, excel)


__all__ = ["create_workers"]
