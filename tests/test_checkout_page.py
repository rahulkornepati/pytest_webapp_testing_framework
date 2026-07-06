from __future__ import annotations
import pytest
from pages.cart_page import CartPage
from pages.checkout_complete_page import CheckoutCompletePage
from pages.checkout_information_page import CheckoutInformationPage
from pages.checkout_overview_page import CheckoutOverviewPage
from pages.header_page import HeaderPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.menu_page import MenuPage

class TestCheckoutPage:

    @pytest.mark.smoke
    def test_checkout_happy_path(self, logged_in_driver, checkout_customers):
        inventory_page = InventoryPage(logged_in_driver)
        header_page = HeaderPage(logged_in_driver)
        customer = checkout_customers["valid_customer"]

        inventory_page.add_backpack_to_cart()
        header_page.open_cart()
        CartPage(logged_in_driver).checkout()

        information_page = CheckoutInformationPage(logged_in_driver)
        information_page.enter_customer_information(customer["first_name"], customer["last_name"], customer["postal_code"])
        information_page.continue_checkout()

        overview_page = CheckoutOverviewPage(logged_in_driver)
        assert overview_page.is_loaded()
        assert "Sauce Labs Backpack" in overview_page.item_names()

        overview_page.finish()
        complete_page = CheckoutCompletePage(logged_in_driver)
        assert complete_page.is_loaded()
        assert complete_page.confirmation_header() == "Thank you for your order!"


    @pytest.mark.regression
    def test_checkout_missing_first_name_validation(self, logged_in_driver, checkout_customers):
        inventory_page = InventoryPage(logged_in_driver)
        header_page = HeaderPage(logged_in_driver)
        customer = checkout_customers["missing_first_name"]

        inventory_page.add_backpack_to_cart()
        header_page.open_cart()
        CartPage(logged_in_driver).checkout()

        information_page = CheckoutInformationPage(logged_in_driver)
        information_page.enter_customer_information(customer["first_name"], customer["last_name"], customer["postal_code"])
        information_page.continue_checkout()

        assert "First Name is required" in information_page.error_message()

    @pytest.mark.regression
    def test_sidebar_logout_returns_to_login_page(self, logged_in_driver):
        header_page = HeaderPage(logged_in_driver)
        header_page.open_menu()
        MenuPage(logged_in_driver).logout()

        assert LoginPage(logged_in_driver).is_loaded()



