from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ProductDetailsPage(BasePage):
    PRODUCT_NAME = (By.CLASS_NAME, "inventory_details_name")
    PRODUCT_PRICE = (By.CLASS_NAME, "inventory_details_price")
    ADD_TO_CART_BUTTON = (By.ID, "add-to-cart")
    REMOVE_BUTTON = (By.ID, "remove")
    BACK_TO_PRODUCTS_BUTTON = (By.ID, "back-to-products")

    def product_name(self) -> str:
        return self.get_text(self.PRODUCT_NAME)

    def product_price(self) -> str:
        return self.get_text(self.PRODUCT_PRICE)

    def add_to_cart(self) -> None:
        self.click(self.ADD_TO_CART_BUTTON)

    def remove_from_cart(self) -> None:
        self.click(self.REMOVE_BUTTON)

    def back_to_products(self) -> None:
        self.click(self.BACK_TO_PRODUCTS_BUTTON)

    def is_product_image_displayed(self, product_name: str) -> bool:
        product_image = (
            By.XPATH,
            f"//img[@alt='{product_name}']"
        )
        return self.driver.find_element(*product_image).is_displayed()