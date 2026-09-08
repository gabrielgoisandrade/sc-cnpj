from collections import deque
from logging import Logger
from threading import local

from rich.layout import Layout
from rich.progress import Progress, TaskID
from rich.text import Text


class ThreadState(local):
    log: Logger
    worker_progresses: list[Progress]
    visual_log: list[deque[Text]]
    worker_layout: Layout
    progress: Progress
    worker_task: TaskID


thread_state = ThreadState()
