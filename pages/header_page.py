from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HeaderPage(BasePage):
    APP_LOGO = (By.CLASS_NAME, "app_logo")
    PAGE_TITLE = (By.CLASS_NAME, "title")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")

    def page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def open_cart(self) -> None:
        self.click(self.CART_LINK)

    def open_menu(self) -> None:
        self.click(self.MENU_BUTTON)

    def cart_badge_count(self) -> int:
        if not self.is_visible(self.CART_BADGE):
            return 0
        return int(self.get_text(self.CART_BADGE))
