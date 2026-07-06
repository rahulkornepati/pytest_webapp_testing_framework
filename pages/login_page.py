from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")
    LOGIN_LOGO = (By.CLASS_NAME, "login_logo")

    def load(self, base_url: str) -> None:
        self.open_url(base_url)

    def login(self, username: str, password: str) -> None:
        self.type_text(self.USERNAME, username)
        self.type_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_loaded(self) -> bool:
        return self.is_visible(self.LOGIN_LOGO)
