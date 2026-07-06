from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    COMPLETE_CONTAINER = (By.ID, "checkout_complete_container")
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
    COMPLETE_TEXT = (By.CLASS_NAME, "complete-text")
    BACK_HOME_BUTTON = (By.ID, "back-to-products")

    def is_loaded(self) -> bool:
        return self.is_visible(self.COMPLETE_CONTAINER)

    def confirmation_header(self) -> str:
        return self.get_text(self.COMPLETE_HEADER)

    def confirmation_text(self) -> str:
        return self.get_text(self.COMPLETE_TEXT)

    def back_home(self) -> None:
        self.click(self.BACK_HOME_BUTTON)
