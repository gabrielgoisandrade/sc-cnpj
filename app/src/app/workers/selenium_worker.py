from selenium.common.exceptions import TimeoutException, WebDriverException

from app.models import Record
from app.services import Driver
from app.state import thread_state


def selenium_worker(cnpjs: list[Record]):
    thread_state.log.info(f"Starting search {len(cnpjs)} CNPJs")
    driver = Driver()

    try:
        return driver.find_value(cnpjs)
    except (WebDriverException, TimeoutException) as e:
        thread_state.log.exception(msg=e)
        raise e from e
    finally:
        thread_state.log.info("Finished")
        driver.quit()
