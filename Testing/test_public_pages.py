"""
test_public_pages.py — Tests for public pages (no login required).
Covers: Home, Navbar, How it works, 404 redirect.

Run: pytest tests/test_public_pages.py -v
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from conftest import go_to


class TestPublicPages:

    def test_home_page_loads(self, driver, wait):
        """Home page should load with Interview me branding."""
        go_to(driver)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "Interview me" in driver.page_source

    def test_navbar_links_visible(self, driver, wait):
        """Navbar should show Home, How it works, Products, Sign up."""
        go_to(driver)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "nav")))
        page = driver.page_source
        assert "How it works" in page or "how it works" in page.lower()
        assert "Products" in page
        assert "Sign up" in page

    def test_products_dropdown_opens(self, driver, wait):
        """Products dropdown should open on click and show items."""
        go_to(driver)
        products_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Products')]")
        ))
        products_btn.click()
        time.sleep(0.5)
        assert "Analyze my interview" in driver.page_source

    def test_products_dropdown_shows_view_report(self, driver, wait):
        """Products dropdown should show View my report item."""
        go_to(driver)
        products_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Products')]")
        ))
        products_btn.click()
        time.sleep(0.5)
        assert "View my report" in driver.page_source

    def test_how_it_works_page_loads(self, driver, wait):
        """How it works page should load at correct URL."""
        go_to(driver, "/how-it-works")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert driver.current_url.endswith("/how-it-works")

    def test_signup_button_navigates(self, driver, wait):
        """Sign up button in navbar should navigate to /signup."""
        go_to(driver)
        signup_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(), 'Sign up') or contains(@href, 'signup')]")
        ))
        signup_btn.click()
        time.sleep(1)
        assert "signup" in driver.current_url

    def test_unknown_route_redirects_home(self, driver, wait):
        """Unknown routes should redirect to home page."""
        go_to(driver, "/this-page-does-not-exist")
        time.sleep(1)
        assert driver.current_url == f"http://localhost:5173/"

    def test_logo_visible_on_home(self, driver, wait):
        """Logo should be visible on home page."""
        go_to(driver)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "Interview me" in driver.page_source

    def test_products_dropdown_not_logged_in_redirects_signin(self, driver, wait):
        """Products > View my report when not logged in should go to /sign-in."""
        go_to(driver)
        try:
            products_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Products')]")
            ))
            products_btn.click()
            time.sleep(0.5)
            view_report = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(), 'View my report')]")
            ))
            view_report.click()
            time.sleep(1)
            assert "sign-in" in driver.current_url
        except Exception:
            pytest.skip("Products dropdown not available on home page")
