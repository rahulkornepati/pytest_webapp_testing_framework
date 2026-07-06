from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CartPage(BasePage):
    CART_LIST = (By.CLASS_NAME, "cart_list")
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    CART_ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    CONTINUE_SHOPPING_BUTTON = (By.ID, "continue-shopping")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    REMOVE_BACKPACK_BUTTON = (By.ID, "remove-sauce-labs-backpack")

    def is_loaded(self) -> bool:
        return self.is_visible(self.CART_LIST)

    def item_names(self) -> list[str]:
        return [item.text for item in self.driver.find_elements(*self.CART_ITEM_NAMES)]

    def item_count(self) -> int:
        return len(self.driver.find_elements(*self.CART_ITEMS))

    def remove_backpack(self) -> None:
        self.click(self.REMOVE_BACKPACK_BUTTON)

    def continue_shopping(self) -> None:
        self.click(self.CONTINUE_SHOPPING_BUTTON)

    def checkout(self) -> None:
        self.click(self.CHECKOUT_BUTTON)

    def has_product(self, product):
        return product in self.item_names()
