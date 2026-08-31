from zipfile import BadZipFile

from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from app.logger import log
from app.models import Record


class Excel:
    __path: str
    __workbook: Workbook
    __sheet: Worksheet

    def __init__(self, path: str) -> None:
        self.__path = path

    def load(self):
        try:
            self.__workbook = load_workbook(filename=self.__path)

            if self.__workbook.active is None:
                raise ValueError("Sheet cannot be None")

            self.__sheet = self.__workbook.active
        except (FileNotFoundError, BadZipFile) as e:
            log.exception(msg=e)
            raise e from e

    def write(self, records: list[Record]):
        try:
            for record in records:
                self.__sheet[f"E{record.row}"] = record.value

            self.__workbook.save(self.__path)
        except OSError as e:
            log.exception(msg=e)
            raise OSError(e) from e

    @property
    def workbook(self) -> Workbook:
        return self.__workbook

    @property
    def sheet(self) -> Worksheet:
        return self.__sheet
