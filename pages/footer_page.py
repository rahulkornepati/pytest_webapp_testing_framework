from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class FooterPage(BasePage):
    FOOTER = (By.CLASS_NAME, "footer")
    TWITTER_LINK = (By.CSS_SELECTOR, "li.social_twitter a")
    FACEBOOK_LINK = (By.CSS_SELECTOR, "li.social_facebook a")
    LINKEDIN_LINK = (By.CSS_SELECTOR, "li.social_linkedin a")
    COPYRIGHT_TEXT = (By.CLASS_NAME, "footer_copy")

    def is_loaded(self) -> bool:
        return self.is_visible(self.FOOTER)

    def copyright_text(self) -> str:
        self.scroll_to(self.COPYRIGHT_TEXT)
        return self.get_text(self.COPYRIGHT_TEXT)

    def social_link(self, network: str) -> str | None:
        locators = {
            "twitter": self.TWITTER_LINK,
            "facebook": self.FACEBOOK_LINK,
            "linkedin": self.LINKEDIN_LINK,
        }
        return self.get_attribute(locators[network], "href")
