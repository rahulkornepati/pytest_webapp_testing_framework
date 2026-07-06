from __future__ import annotations

from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from pages.base_page import BasePage


class InventoryPage(BasePage):
    INVENTORY_CONTAINER = (By.ID, "inventory_container")
    INVENTORY_ITEMS = (By.CLASS_NAME, "inventory_item")
    PRODUCT_NAMES = (By.CLASS_NAME, "inventory_item_name")
    PRODUCT_PRICES = (By.CLASS_NAME, "inventory_item_price")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")

    def is_loaded(self) -> bool:
        return self.is_visible(self.INVENTORY_CONTAINER)

    def product_names(self) -> list[str]:
        return [element.text for element in self.find_all(self.PRODUCT_NAMES)]

    def product_prices(self) -> list[Decimal]:
        return [
            Decimal(element.text.replace("$", ""))
            for element in self.find_all(self.PRODUCT_PRICES)
        ]

    def sort_by(self, visible_text: str) -> None:
        Select(self.visible(self.SORT_DROPDOWN)).select_by_visible_text(visible_text)

    @staticmethod
    def _product_slug(product_name: str) -> str:
        """
        Converts:
        'Sauce Labs Backpack'
        -> 'sauce-labs-backpack'
        """
        return product_name.lower().replace(" ", "-")

    def _add_to_cart_button(self, product_name: str):
        return (
            By.ID,
            f"add-to-cart-{self._product_slug(product_name)}"
        )

    def _remove_button(self, product_name: str):
        return (
            By.ID,
            f"remove-{self._product_slug(product_name)}"
        )

    def _product_link(self, product_name: str):
        return (
            By.XPATH,
            f"//a[.//*[@data-test='inventory-item-name' and normalize-space()='{product_name}']]"
        )

    def add_product_to_cart(self, product_name: str) -> None:
        self.click(self._add_to_cart_button(product_name))

    def remove_product(self, product_name: str) -> None:
        self.click(self._remove_button(product_name))

    def open_product(self, product_name: str) -> None:
        self.click(self._product_link(product_name))