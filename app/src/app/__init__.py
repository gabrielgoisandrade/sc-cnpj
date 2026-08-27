from time import sleep

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def find_value_by_cnpj(cnpjs: list[str]) -> list[dict[str, str]]:
    try:
        options = Options()
        options.add_argument("--headless=new")
        driver = Chrome(options)

        driver.get("https://appasp.sefaz.go.gov.br/Sintegra/Consulta/default.html")
        checkbox = driver.find_element("id", "rTipoDocCNPJ")
        checkbox.click()

        input = driver.find_element("id", "tCNPJ")

        confirm = driver.find_element("name", "btCGC")

        results = []

        for cnpj in cnpjs:
            input.click()
            input.send_keys(cnpj)

            sleep(1)

            confirm.click()

            sleep(1)

            span = driver.find_element(
                By.XPATH, "//span[text()='Regime de Apuração:']/following-sibling::*[1]"
            )

            results.append({"cnpj": cnpj, "situation": span.text})

            driver.back()

            sleep(1.5)

        return results
    except ValueError as e:
        raise e from e
    finally:
        driver.quit()


def main() -> None:
    try:
        cnpjs = [
            "02757995000165",
            "00294421000172",
            "19258309000104",
            "12561303000162",
            "47387347000100",
        ]

        values = find_value_by_cnpj(cnpjs)

        with open("../output.txt", "w+") as f:
            [f.write(f"{value['cnpj']} - {value['situation']}\n") for value in values]

    except ValueError as e:
        print(e)
