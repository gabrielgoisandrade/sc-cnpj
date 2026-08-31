import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.logger import log
from app.models import Record
from app.services import Excel
from app.utils import make_chunks
from app.workers import worker


def main() -> None:
    try:
        path = r"C:\Users\gabriel.andrade\Documents\cnpjs_export.xlsx"

        excel = Excel(path)
        excel.load()

        column = excel.sheet["A"][1:]

        cnpjs = [Record(cell.row, cell.value) for cell in column]

        chunks = make_chunks(cnpjs)

        with ThreadPoolExecutor(max_workers=4, thread_name_prefix="worker") as executor:
            futures = [executor.submit(worker, chunk) for chunk in chunks]
            [
                excel.write(result)
                for future in as_completed(futures)
                for result in future.result()
            ]

    except Exception as e:
        print("Ups, deu ruim!", e)
        log.exception(msg=e)


# TODO: luz caiu e perdi o progresso, dessa forma, todos os 30mil itens precisariam ser buscados novamente, pois nao há um controle sobre isso.
# nesse caso, o ideal era continuar de onde parou, gravando o ultimo registro salvo no log e, a partir dele, refazer o processo.
# isso por worker: worker_1 -> parou em 3, worker_2 -> parou em 10 e assim por diante
# checkpoint, usando o proprio log pra rastreio
