from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class MenuPage(BasePage):
    MENU_CONTAINER = (By.CLASS_NAME, "bm-menu")
    ALL_ITEMS_LINK = (By.ID, "inventory_sidebar_link")
    ABOUT_LINK = (By.ID, "about_sidebar_link")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")
    RESET_APP_STATE_LINK = (By.ID, "reset_sidebar_link")
    CLOSE_BUTTON = (By.ID, "react-burger-cross-btn")

    def is_loaded(self) -> bool:
        return self.is_visible(self.MENU_CONTAINER)

    def all_items(self) -> None:
        self.click(self.ALL_ITEMS_LINK)

    def logout(self) -> None:
        self.click(self.LOGOUT_LINK)

    def reset_app_state(self) -> None:
        self.click(self.RESET_APP_STATE_LINK)

    def close(self) -> None:
        self.click(self.CLOSE_BUTTON)
