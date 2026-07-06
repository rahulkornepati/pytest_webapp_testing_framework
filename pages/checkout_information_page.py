from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutInformationPage(BasePage):
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    CANCEL_BUTTON = (By.ID, "cancel")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def enter_customer_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.type_text(self.FIRST_NAME, first_name)
        self.type_text(self.LAST_NAME, last_name)
        self.type_text(self.POSTAL_CODE, postal_code)

    def continue_checkout(self) -> None:
        self.click(self.CONTINUE_BUTTON)

    def cancel(self) -> None:
        self.click(self.CANCEL_BUTTON)

    def error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)
