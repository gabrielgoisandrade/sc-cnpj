import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from rich.console import Console, Group
from rich.layout import Layout
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
from app.ui import console, make_progresses
from app.utils import make_chunks

from .excel_worker import excel_worker
from .selenium_worker import selenium_worker

MAX_WORKERS = 4


# TODO: entender o isso faz
class LogView:
    def __init__(self, logs: deque[Text]):
        self.logs = logs

    def finish(self):
        self.finished = True

    def __rich__(self):
        return Group(*self.logs)


def initializer(
    worker_progresses: list[Progress],
    worker_log: list[Text],
    worker_layouts: list[Layout],
):
    [thread_name, thread_index] = threading.current_thread().name.split("_")

    id = int(thread_index) + 1

    worker_name = f"{thread_name}_{id}"

    thread_state.log = create_log(worker_name)
    thread_state.log.info("Log file created")

    thread_state.visual_log = worker_log[id]
    thread_state.worker_layout = worker_layouts[id]

    progress = worker_progresses[id]
    thread_state.progress = progress
    thread_state.worker_task = progress.add_task(worker_name, total=None)

    thread_state.log.info("Worker created")


def create_workers():
    path = console.input(":file_folder: Selecionar base: ")

    excel = Excel(path.strip())
    excel.load()

    column = excel.sheet["A"][1:1]

    cnpjs = [Record(cell.row, cell.value) for cell in column]

    log.info(f"Found {len(cnpjs)} CNPJs")

    chunks = make_chunks(cnpjs, 5)

    # TODO: remover TODO o rich daqui e separar num arquivo próprio de ui.

    grid = Table.grid(expand=True, padding=0)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)

    worker_progresses = make_progresses(MAX_WORKERS)

    worker_logs: list[deque[Text]] = [deque(maxlen=5) for _ in range(4)]

    worker_layouts = []
    worker_panels = []

    for i in range(MAX_WORKERS):
        content = Layout()
        content.split_column(
            Layout(LogView(worker_logs[i]), name="logs"),
            Layout(worker_progresses[i], name="progess", size=1),
        )

        worker_layouts.append(content)

        worker_panels.append(
            Panel(
                renderable=content,
                title=f"Worker_{i + 1}",
                title_align="left",
                height=10,
                highlight=True,
            )
        )

    grid.add_row(worker_panels[0], worker_panels[1])
    grid.add_row(worker_panels[2], worker_panels[3])

    with Live(grid):
        thread_props = {
            "max_workers": MAX_WORKERS,
            "thread_name_prefix": "worker",
            "initializer": initializer,
            "initargs": (worker_progresses, worker_logs, worker_layouts),
        }

        with ThreadPoolExecutor(**thread_props) as executor:
            futures = []

            for chunk in chunks:
                futures.append(executor.submit(selenium_worker, chunk))

    excel_worker(futures, excel)


__all__ = ["create_workers"]
