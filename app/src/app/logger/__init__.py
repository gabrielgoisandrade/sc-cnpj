import logging
from pathlib import Path

path = Path("logs")
path.mkdir(exist_ok=True)


def create_log(name: str):
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)

    handler = logging.FileHandler(
        filename=path / f"{name}.log", mode="a", encoding="utf-8"
    )

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler.setFormatter(formatter)
    log.addHandler(handler)

    return log


log = create_log("app")  # default app.log


__all__ = ["create_log", "log"]
