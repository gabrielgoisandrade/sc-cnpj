import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)

from app.logger import create_log, log
from app.models import Record
from app.services import Excel
from app.state import thread_state
from app.utils import make_chunks
from app.workers import worker


def initializer(progress: Progress):
    worker_name = threading.current_thread().name
    id = worker_name.split("_")[1]
    worker_name = worker_name.replace(id, str(int(id) + 1))

    thread_state.log = create_log(worker_name)
    thread_state.log.info("Created worker")

    thread_state.progress = progress
    thread_state.worker_task = progress.add_task(worker_name, total=None)


def main() -> None:
    try:
        path = r"C:\Users\gabriel.andrade\Documents\cnpjs_export.xlsx"

        excel = Excel(path)
        excel.load()

        column = excel.sheet["A"][1:10]

        cnpjs = [Record(cell.row, cell.value) for cell in column]
        log.info(f"Found {len(cnpjs)} values from spreadsheet")

        chunks = make_chunks(cnpjs, 10)

        with (
            Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=None),
                MofNCompleteColumn("/"),
                TimeRemainingColumn(elapsed_when_finished=True, compact=True),
                expand=True,
            ) as progress,
            ThreadPoolExecutor(
                max_workers=4,
                thread_name_prefix="worker",
                initializer=initializer,
                initargs=(progress,),
            ) as executor,
        ):
            futures = [executor.submit(worker, chunk) for chunk in chunks]

            task = progress.add_task("writing", total=None)
            for future in as_completed(futures):
                if future._result:
                    progress.reset(task, total=len(future._result))

                for result in future.result():
                    excel.write(result)
                    progress.advance(task)

    except Exception as e:  # noqa: BLE001
        log.exception(msg=e)
