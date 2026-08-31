from selenium.common.exceptions import TimeoutException, WebDriverException

from app.logger import log
from app.models import Record
from app.services import Driver


def worker(cnpjs: list[Record]):
    log.info(f"Starting search {len(cnpjs)} CNPJs")

    driver = Driver()

    try:
        return driver.find_value(cnpjs)
    except (WebDriverException, TimeoutException) as e:
        log.exception(msg=e)
        raise e from e
    finally:
        log.info("Finished")
        driver.quit()


__all__ = ["worker"]
