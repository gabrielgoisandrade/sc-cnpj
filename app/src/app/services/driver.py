from pathlib import Path
from time import sleep

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from app.logger import log
from app.models import Record


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

            log.info("Driver found")

            return driver
        except (FileNotFoundError, TimeoutException) as e:
            log.exception(msg=e)
            raise e from e

    def find_value(self, criterias: list[Record]):
        try:
            results: list[list[Record]] = []

            self.__driver.get(self.__INDEX_URL)

            checkbox = self.__driver.find_element("id", "rTipoDocCNPJ")
            input = self.__driver.find_element("id", "tCNPJ")
            confirm = self.__driver.find_element("name", "btCGC")

            checkbox.click()

            for index, criteria in enumerate(criterias):
                sleep(1.5)

                log.info(f"Searching {index + 1}/{len(criterias)}")

                input.clear()
                input.send_keys(criteria.value)

                confirm.click()

                sleep(1.5)

                error_tooltip = self.__driver.find_elements(
                    By.CLASS_NAME,
                    "zion_rich_validation_box",
                )

                if len(error_tooltip):
                    log.error(f"{criteria.value} is invalid")

                    results.append([Record(criteria.row, "CNPJ inválido")])
                    input.clear()

                    continue

                sleep(1.5)

                spans = self.__driver.find_elements(
                    By.XPATH,
                    "//span[text()='Regime de Apuração:']/following-sibling::*[1]",
                )

                if self.__RESULT_PAGE_URL == self.__driver.current_url and not len(
                    spans
                ):
                    log.info(f"No results found for {criteria.value}")

                    results.append([Record(criteria.row, " ")])
                    self.__driver.back()

                    continue

                log.info(f"Results found: {len(results)} of {len(criterias)}")

                results.append([Record(criteria.row, spans[0].text)])

                self.__driver.back()

            return results
        except WebDriverException as e:
            log.exception(msg=e)
            raise e from e

    def quit(self):
        return self.__driver.quit()
