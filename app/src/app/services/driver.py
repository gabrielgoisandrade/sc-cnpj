from pathlib import Path
from time import sleep

from rich.text import Text
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from app.models import Record
from app.state import thread_state


class Driver:
    __driver: WebDriver
    __path: str

    __INDEX_URL = "https://appasp.sefaz.go.gov.br/Sintegra/Consulta/default.html"

    __RESULT_PAGE_URL = "https://appasp.sefaz.go.gov.br/Sintegra/Consulta/consultar.asp"

    def __init__(self, path="src/driver/chromedriver.exe") -> None:
        self.__path = str(Path(path).resolve())
        self.__driver = self.__get_driver()

    def __get_driver(self):
        try:
            executable_path = str(Path(self.__path).resolve())
            options = Options()
            options.add_argument("--headless=new")

            service = Service(executable_path)

            driver = Chrome(options, service)
            driver.set_page_load_timeout(10)

            thread_state.log.info("Driver found")

            return driver
        except (FileNotFoundError, TimeoutException) as e:
            thread_state.log.exception(msg=e)
            raise e from e

    def find_value(self, criterias: list[Record]):
        try:
            results: list[list[Record]] = []
            thread_state.progress.reset(thread_state.worker_task, total=len(criterias))

            self.__driver.get(self.__INDEX_URL)

            checkbox = self.__driver.find_element("id", "rTipoDocCNPJ")
            input = self.__driver.find_element("id", "tCNPJ")
            confirm = self.__driver.find_element("name", "btCGC")

            checkbox.click()

            for criteria in criterias:
                sleep(1.5)

                thread_state.progress.advance(thread_state.worker_task)

                thread_state.log.info(f"Searching {criteria.value}")

                thread_state.visual_log.append(
                    Text.from_markup(f':mag: [bold][blue] Buscando "{criteria.value}"')
                )

                input.clear()
                input.send_keys(criteria.value)

                confirm.click()

                sleep(1.5)

                error_tooltip = self.__driver.find_elements(
                    By.CLASS_NAME,
                    "zion_rich_validation_box",
                )

                if len(error_tooltip):
                    thread_state.log.error(f"{criteria.value} is invalid")

                    thread_state.visual_log.append(
                        Text.from_markup(
                            f':x: [bold][red] CNPJ "{criteria.value}" inválido'
                        )
                    )

                    results.append([Record(criteria.row, "CNPJ inválido")])
                    input.clear()

                    continue

                spans = self.__driver.find_elements(
                    By.XPATH,
                    "//span[text()='Regime de Apuração:']/following-sibling::*[1]",
                )

                if self.__RESULT_PAGE_URL == self.__driver.current_url and not len(
                    spans
                ):
                    thread_state.log.info(f"No results found for {criteria.value}")

                    thread_state.visual_log.append(
                        Text.from_markup(
                            f':warning: [bold][yellow] Nenhum resultado encontrado para o CNPJ "{criteria.value}"',
                        )
                    )

                    results.append([Record(criteria.row, " ")])
                    self.__driver.back()

                    continue

                thread_state.log.info(
                    f"Results found: {len(results)} of {len(criterias)}"
                )

                results.append([Record(criteria.row, spans[0].text)])

                self.__driver.back()

            thread_state.visual_log.append(
                Text.from_markup(
                    ":white_heavy_check_mark: [bold][green] Processo finalizado"
                )
            )

            return results
        except WebDriverException as e:
            thread_state.log.exception(msg=e)
            raise e from e

    def quit(self):
        return self.__driver.quit()
