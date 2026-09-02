from app.logger import log
from app.workers import create_workers


def main() -> None:
    try:
        create_workers()
    except Exception as e:  # noqa: BLE001
        log.exception(msg=e)
