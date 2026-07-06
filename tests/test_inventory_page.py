import allure
import pytest

from pages.cart_page import CartPage
from pages.footer_page import FooterPage
from pages.header_page import HeaderPage
from pages.inventory_page import InventoryPage
from pages.product_details_page import ProductDetailsPage
from pages.product_data import ProductData

class TestInventoryPage:

    @pytest.fixture(autouse=True)
    def setup_pages(self, logged_in_driver):
        self.driver = logged_in_driver
        self.inventory_page = InventoryPage(logged_in_driver)
        self.header_page = HeaderPage(logged_in_driver)
        self.footer_page = FooterPage(logged_in_driver)

    @pytest.mark.regression
    def test_add_product_in_inventory_page(self):

        with allure.step("Add Backpack to cart"):
            self.inventory_page.add_product_to_cart(ProductData.BACKPACK)

        with allure.step("Verify cart badge count"):
            assert self.header_page.cart_badge_count() == 1, \
                f"Expected cart count to be 1 but found {self.header_page.cart_badge_count()}"

        with allure.step("Open Cart page"):
            self.header_page.open_cart()
            cart_page = CartPage(self.driver)

        with allure.step("Verify Cart page is loaded"):
            assert cart_page.is_loaded(), \
                "Failed: Cart page failed to load"

        with allure.step("Verify Backpack is added into cart"):
            assert ProductData.BACKPACK in cart_page.item_names(), \
                "Failed: Backpack not added to cart"

    @pytest.mark.regression
    def test_remove_btn_functionality(self):

        with allure.step("Add Bike Light to cart"):
            self.inventory_page.add_product_to_cart(ProductData.BIKE_LIGHT)

        with allure.step("Verify cart badge count"):
            assert self.header_page.cart_badge_count() == 1, \
                "Failed: Item is not added to cart"

        with allure.step("Remove Bike Light from cart"):
            self.inventory_page.remove_product(ProductData.BIKE_LIGHT)

        with allure.step("Verify Add to Cart button is visible"):
            assert self.inventory_page.is_visible(
                self.inventory_page._add_to_cart_button(ProductData.BIKE_LIGHT)
            ), "Failed: 'Add to Cart' button is not visible"

        with allure.step("Verify cart badge count becomes zero"):
            assert self.header_page.cart_badge_count() == 0, \
                "Failed: Item is not removed from cart"

    @pytest.mark.regression
    def test_correct_product_details(self):

        with allure.step("Open Backpack product details"):
            self.inventory_page.open_product(ProductData.BACKPACK)
            details_page = ProductDetailsPage(self.driver)

        with allure.step("Verify product image"):
            assert details_page.is_product_image_displayed(
                ProductData.BACKPACK
            ), "Failed: Product image is not displayed"

        with allure.step("Verify product name"):
            assert details_page.product_name() == ProductData.BACKPACK, \
                "Failed: Product name is incorrect"

        with allure.step("Verify product price"):
            assert details_page.product_price() == ProductData.BACKPACK_PRICE, \
                "Failed: Product price is incorrect"

        with allure.step("Verify Add to Cart button"):
            assert self.inventory_page.is_visible(
                details_page.ADD_TO_CART_BUTTON
            ), "Failed: Add to Cart button is not visible"

    @pytest.mark.regression
    def test_sort_products_by_price_low_to_high(self):

        with allure.step("Sort products by Price Low to High"):
            self.inventory_page.sort_by("Price (low to high)")

        with allure.step("Fetch sorted prices"):
            sorted_prices = self.inventory_page.product_prices()

        with allure.step("Verify products are sorted correctly"):
            assert sorted_prices == sorted(sorted_prices), \
                "Failed: Products are not sorted in ascending order"

    @pytest.mark.regression
    def test_open_product_detail_from_inventory(self):

        with allure.step("Open Backpack details page"):
            self.inventory_page.open_product(ProductData.BACKPACK)
            details_page = ProductDetailsPage(self.driver)

        with allure.step("Verify product name"):
            assert details_page.product_name() == ProductData.BACKPACK

        with allure.step("Verify product price"):
            assert details_page.product_price() == ProductData.BACKPACK_PRICE

    @pytest.mark.regression
    def test_footer_social_links_are_available(self):

        with allure.step("Verify Footer is loaded"):
            assert self.footer_page.is_loaded()

        with allure.step("Verify Twitter link"):
            assert "saucelabs" in self.footer_page.social_link("twitter")

        with allure.step("Verify Facebook link"):
            assert "saucelabs" in self.footer_page.social_link("facebook")

        with allure.step("Verify LinkedIn link"):
            assert "sauce-labs" in self.footer_page.social_link("linkedin")