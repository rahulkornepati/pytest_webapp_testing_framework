from __future__ import annotations

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_url(self, url: str) -> None:
        self.driver.get(url)

    def find(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator: tuple[str, str]) -> list[WebElement]:
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def visible(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def clickable(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator: tuple[str, str]) -> None:
        element = self.clickable(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        if element.tag_name.lower() in {"button", "a"} or element.get_attribute("type") in {"button", "submit"}:
            self.driver.execute_script("arguments[0].click();", element)
        else:
            element.click()

    def type_text(self, locator: tuple[str, str], text: str) -> None:
        element = self.visible(locator)
        element.click()
        element.clear()
        element.send_keys(text)
        self.driver.execute_script(
            """
            const element = arguments[0];
            const value = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(
                Object.getPrototypeOf(element),
                'value'
            ).set;
            setter.call(element, value);
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            element,
            text,
        )

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.visible(locator).text

    def get_attribute(self, locator: tuple[str, str], attribute: str) -> str | None:
        return self.find(locator).get_attribute(attribute)

    def is_visible(self, locator: tuple[str, str], timeout: int = 10) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def wait_for_url_contains(self, text: str) -> bool:
        return self.wait.until(EC.url_contains(text))

    def scroll_to(self, locator: tuple[str, str]) -> None:
        element = self.find(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
