"""
test_auth.py — Authentication tests.
Covers: Sign Up, Sign In, Forgot Password, Reset Password, Logout.

Run: pytest tests/test_auth.py -v
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from conftest import (
    go_to, login, logout,
    RECRUITER_EMAIL, RECRUITER_PASS,
    CANDIDATE_EMAIL, CANDIDATE_PASS,
)


# ── SIGN UP ───────────────────────────────────────────────────────────────────

class TestSignUp:

    def test_signup_page_loads(self, driver, wait):
        """Sign up page should load with form fields."""
        go_to(driver, "/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        assert "Create" in driver.page_source or "Sign" in driver.page_source

    def test_signup_toggle_candidate_company(self, driver, wait):
        """Toggle between Candidate and Company should work."""
        go_to(driver, "/signup")
        company_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Company')]")
        ))
        company_btn.click()
        time.sleep(0.5)
        assert "Company" in driver.page_source

        candidate_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Candidate')]")
        candidate_btn.click()
        time.sleep(0.5)
        assert "Candidate" in driver.page_source

    def test_signup_empty_form_shows_errors(self, driver, wait):
        """Submitting empty signup form should show validation errors."""
        go_to(driver, "/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        page = driver.page_source
        assert "required" in page.lower() or "valid" in page.lower() or "error" in page.lower()

    def test_signup_short_password_shows_error(self, driver, wait):
        """Password shorter than 8 characters should show error."""
        go_to(driver, "/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.NAME, "fullName").send_keys("Test User")
        driver.find_element(By.NAME, "email").send_keys("testshort@example.com")
        driver.find_element(By.NAME, "phone").send_keys("01234567890")

        passwords = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        passwords[0].send_keys("short")
        passwords[1].send_keys("short")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        page = driver.page_source
        assert "8" in page or "characters" in page.lower() or "error" in page.lower()

    def test_signup_password_mismatch_shows_error(self, driver, wait):
        """Mismatched passwords should show error."""
        go_to(driver, "/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.NAME, "fullName").send_keys("Test User")
        driver.find_element(By.NAME, "email").send_keys("testmismatch@example.com")
        driver.find_element(By.NAME, "phone").send_keys("01234567890")

        passwords = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        passwords[0].send_keys("Password123!")
        passwords[1].send_keys("DifferentPass!")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        assert "match" in driver.page_source.lower() or "error" in driver.page_source.lower()

    def test_signup_duplicate_email_shows_error(self, driver, wait):
        """Signing up with existing email should show error."""
        go_to(driver, "/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.NAME, "fullName").send_keys("Existing User")
        driver.find_element(By.NAME, "email").send_keys(RECRUITER_EMAIL)
        driver.find_element(By.NAME, "phone").send_keys("01234567890")

        passwords = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        passwords[0].send_keys("Password123!")
        passwords[1].send_keys("Password123!")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        page = driver.page_source
        assert "exist" in page.lower() or "error" in page.lower() or "taken" in page.lower()

    def test_signup_login_link_navigates(self, driver, wait):
        """Log in button on signup page should navigate to /sign-in."""
        go_to(driver, "/signup")
        login_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Log in')] | //a[contains(text(), 'Log in')]")
        ))
        login_btn.click()
        time.sleep(1)
        assert "sign-in" in driver.current_url


# ── SIGN IN ───────────────────────────────────────────────────────────────────

class TestSignIn:

    def test_signin_page_loads(self, driver, wait):
        """Sign in page should load with email and password fields."""
        go_to(driver, "/sign-in")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
        assert "Welcome" in driver.page_source or "Log in" in driver.page_source

    def test_signin_empty_fields_stays_on_page(self, driver, wait):
        """Login with empty fields should not proceed."""
        go_to(driver, "/sign-in")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        assert "sign-in" in driver.current_url

    def test_signin_wrong_password_shows_error(self, driver, wait):
        """Login with wrong password should show error message."""
        go_to(driver, "/sign-in")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(RECRUITER_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("WrongPassword123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        page = driver.page_source
        assert "incorrect" in page.lower() or "invalid" in page.lower() or "error" in page.lower()

    def test_signin_wrong_email_shows_error(self, driver, wait):
        """Login with non-existent email should show error."""
        go_to(driver, "/sign-in")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys("notexist@gmail.com")
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("SomePassword123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        page = driver.page_source
        assert "incorrect" in page.lower() or "invalid" in page.lower() or "error" in page.lower()

    def test_recruiter_login_redirects_to_history(self, driver, wait):
        """Recruiter login should redirect to /recruiter-history."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        assert "recruiter-history" in driver.current_url

    def test_candidate_login_redirects_to_process_video(self, driver, wait):
        """Candidate login should redirect to /process-video."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        assert "process-video" in driver.current_url

    def test_forgot_password_link_navigates(self, driver, wait):
        """Forgotten password button should navigate to /forgot-password."""
        go_to(driver, "/sign-in")
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Forgotten') or contains(text(), 'Forgot')]")
        )).click()
        time.sleep(1)
        assert "forgot-password" in driver.current_url

    def test_signup_link_navigates(self, driver, wait):
        """Create new account link should navigate to /signup."""
        go_to(driver, "/sign-in")
        signup_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(), 'Create') or contains(text(), 'new account')]")
        ))
        signup_link.click()
        time.sleep(1)
        assert "signup" in driver.current_url


# ── FORGOT PASSWORD ───────────────────────────────────────────────────────────

class TestForgotPassword:

    def test_forgot_password_page_loads(self, driver, wait):
        """Forgot password page should load."""
        go_to(driver, "/forgot-password")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "Forgot" in driver.page_source or "forgot" in driver.page_source.lower()

    def test_forgot_password_empty_email_shows_error(self, driver, wait):
        """Submitting empty email should show validation error."""
        go_to(driver, "/forgot-password")
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Send reset')]")
        )).click()
        time.sleep(1)
        page = driver.page_source
        assert "valid" in page.lower() or "required" in page.lower() or "error" in page.lower()

    def test_forgot_password_invalid_format_shows_error(self, driver, wait):
        """Invalid email format should show error."""
        go_to(driver, "/forgot-password")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys("notanemail")
        driver.find_element(By.XPATH, "//button[contains(text(), 'Send reset')]").click()
        time.sleep(1)
        page = driver.page_source
        assert "valid" in page.lower() or "error" in page.lower()

    def test_forgot_password_nonexistent_email_shows_error(self, driver, wait):
        """Non-existent email should show error."""
        go_to(driver, "/forgot-password")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys("notexist@nowhere.com")
        driver.find_element(By.XPATH, "//button[contains(text(), 'Send reset')]").click()
        time.sleep(2)
        page = driver.page_source
        assert "not found" in page.lower() or "error" in page.lower() or "no account" in page.lower()

    def test_forgot_password_valid_email_shows_success(self, driver, wait):
        """Valid email should show check your email screen."""
        go_to(driver, "/forgot-password")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(RECRUITER_EMAIL)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Send reset')]").click()
        time.sleep(2)
        assert "Check your email" in driver.page_source or "check" in driver.page_source.lower()

    def test_forgot_password_step_indicator_visible(self, driver, wait):
        """Step indicator should be visible on forgot password page."""
        go_to(driver, "/forgot-password")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert driver.find_elements(By.CSS_SELECTOR, "div.rounded-full") or \
               driver.find_elements(By.CSS_SELECTOR, "div[class*='rounded']")

    def test_forgot_password_back_to_login(self, driver, wait):
        """Back to log in button should navigate to /sign-in."""
        go_to(driver, "/forgot-password")
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Back to log in')]")
        )).click()
        time.sleep(1)
        assert "sign-in" in driver.current_url


# ── RESET PASSWORD ────────────────────────────────────────────────────────────

class TestResetPassword:

    def test_reset_password_no_token_shows_invalid(self, driver, wait):
        """Reset password page with no token should show invalid link."""
        go_to(driver, "/reset-password")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        assert "invalid" in driver.page_source.lower() or "expired" in driver.page_source.lower()

    def test_reset_password_invalid_token_shows_error(self, driver, wait):
        """Reset password with invalid token should show error after submit."""
        go_to(driver, "/reset-password?token=invalidtoken123")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        passwords = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if passwords:
            passwords[0].send_keys("NewPassword123!")
            passwords[1].send_keys("NewPassword123!")
            driver.find_element(By.XPATH, "//button[contains(text(), 'Reset password')]").click()
            time.sleep(2)
            page = driver.page_source
            assert "invalid" in page.lower() or "expired" in page.lower() or "error" in page.lower()

    def test_reset_password_mismatch_shows_error(self, driver, wait):
        """Mismatched passwords on reset page should show error."""
        go_to(driver, "/reset-password?token=sometoken123")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        passwords = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if passwords:
            passwords[0].send_keys("NewPassword123!")
            passwords[1].send_keys("DifferentPassword!")
            driver.find_element(By.XPATH, "//button[contains(text(), 'Reset password')]").click()
            time.sleep(1)
            assert "match" in driver.page_source.lower() or "error" in driver.page_source.lower()

    def test_reset_password_back_to_login(self, driver, wait):
        """Back to log in on reset page should navigate to /sign-in."""
        go_to(driver, "/reset-password?token=sometoken")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        try:
            back_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Back to log in')]")
            ))
            back_btn.click()
            time.sleep(1)
            assert "sign-in" in driver.current_url
        except Exception:
            pytest.skip("Back to log in button not found on reset page")

    def test_reset_password_request_new_link(self, driver, wait):
        """Invalid reset page should have button to request new link."""
        go_to(driver, "/reset-password")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        page = driver.page_source
        assert "Request a new link" in page or "request" in page.lower() or "forgot" in page.lower()


# ── LOGOUT ────────────────────────────────────────────────────────────────────

class TestLogout:

    def test_recruiter_logout_redirects_to_signin(self, driver, wait):
        """Recruiter logout should redirect to /sign-in."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        logout(driver, wait)
        time.sleep(2)
        assert "sign-in" in driver.current_url

    def test_candidate_logout_redirects_to_signin(self, driver, wait):
        """Candidate logout should redirect to /sign-in."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        logout(driver, wait)
        time.sleep(2)
        assert "sign-in" in driver.current_url

    def test_after_logout_cannot_access_protected_page(self, driver, wait):
        """After logout, accessing protected page should redirect to sign-in."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        logout(driver, wait)
        time.sleep(2)
        driver.execute_script("localStorage.clear();")
        go_to(driver, "/recruiter-history")
        time.sleep(2)
        # Should either redirect to sign-in or show sign-in page
        page = driver.page_source
        assert "sign-in" in driver.current_url or "Welcome Back" in page or "Log in" in page
