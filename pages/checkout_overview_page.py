from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutOverviewPage(BasePage):
    SUMMARY_CONTAINER = (By.ID, "checkout_summary_container")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    SUBTOTAL_LABEL = (By.CLASS_NAME, "summary_subtotal_label")
    TAX_LABEL = (By.CLASS_NAME, "summary_tax_label")
    TOTAL_LABEL = (By.CLASS_NAME, "summary_total_label")
    FINISH_BUTTON = (By.ID, "finish")
    CANCEL_BUTTON = (By.ID, "cancel")

    def is_loaded(self) -> bool:
        return self.is_visible(self.SUMMARY_CONTAINER)

    def item_names(self) -> list[str]:
        return [item.text for item in self.find_all(self.ITEM_NAMES)]

    def subtotal(self) -> str:
        return self.get_text(self.SUBTOTAL_LABEL)

    def tax(self) -> str:
        return self.get_text(self.TAX_LABEL)

    def total(self) -> str:
        return self.get_text(self.TOTAL_LABEL)

    def finish(self) -> None:
        self.click(self.FINISH_BUTTON)

    def cancel(self) -> None:
        self.click(self.CANCEL_BUTTON)
