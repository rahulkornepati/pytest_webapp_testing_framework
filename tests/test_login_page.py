from selenium import webdriver
import pytest
from pages.base_page import BasePage
from pages.header_page import HeaderPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


class TestLoginPage:

    @pytest.mark.smoke
    def test_login_with_correct_credentials(self, driver, base_url, users):
        login_page = LoginPage(driver)
        login_page.load(base_url)
        login_page.login(users["standard_user"]["username"], users["standard_user"]["password"])

        assert InventoryPage(driver).is_loaded()
        assert HeaderPage(driver).page_title() == "Products"

    @pytest.mark.regression
    def test_login_with_wrong_credentials_shows_error(self, driver, base_url, users):
        login_page = LoginPage(driver)
        login_page.load(base_url)
        login_page.login(users["invalid_user"]["username"], users["invalid_user"]["password"])

        assert "Username and password do not match" in login_page.error_message()

    @pytest.mark.regression
    def test_locked_out_user_cannot_login(self, driver, base_url, users):
        login_page = LoginPage(driver)
        login_page.load(base_url)
        login_page.login(users["locked_out_user"]["username"], users["locked_out_user"]["password"])

        assert "locked out" in login_page.error_message()