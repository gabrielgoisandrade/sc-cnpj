from typing import Callable

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)

console = Console(emoji=True, style="white on blue", force_interactive=True)

progress_bar = [
    TextColumn("[progress.description]"),
    BarColumn(bar_width=None),
    MofNCompleteColumn("/"),
    TimeRemainingColumn(elapsed_when_finished=True, compact=True),
]

progress = Progress()

worker_progress = progress

worker_progress.columns = [
    TextColumn("[progress.description]"),
    BarColumn(bar_width=None),
    MofNCompleteColumn("/"),
    TimeRemainingColumn(elapsed_when_finished=True, compact=True),
]
worker_progress.expand = True


def make_progresses(workers_count: int):
    return [worker_progress for _ in range(workers_count)]
