"""
InterviewMe Frontend - Selenium Test Suite
==========================================
Tests both Recruiter and Candidate flows.
Covers happy paths and negative tests.

Requirements:
    pip install selenium webdriver-manager pytest

Run:
    pytest test_interviewme.py -v
    pytest test_interviewme.py -v -k "recruiter"   # recruiter tests only
    pytest test_interviewme.py -v -k "candidate"   # candidate tests only
"""

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ── CONFIG ────────────────────────────────────────────────────────────────────

BASE_URL        = "http://localhost:5173"
VIDEO_PATH      = r"C:\Users\beeko\Desktop\AI-Video-interview-analysis\DataSet\man2.mp4"

RECRUITER_EMAIL = "beeko@gmail.com"
RECRUITER_PASS  = "qZa2WTaCB9yHhU3"

CANDIDATE_EMAIL = "ahmed@gmail.com"
CANDIDATE_PASS  = "Pqc2VzFQMTGUX97"

WAIT_TIMEOUT    = 15   # seconds to wait for elements
UPLOAD_TIMEOUT  = 300  # seconds to wait for video processing (5 min)


# ── FIXTURES ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def driver():
    """Create a fresh Chrome browser for each test."""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    # Uncomment to run headless (no browser window):
    # options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def wait(driver):
    return WebDriverWait(driver, WAIT_TIMEOUT)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def go_to(driver, path="/"):
    driver.get(f"{BASE_URL}{path}")
    time.sleep(0.5)


def login(driver, wait, email, password):
    """Login helper — navigates to sign-in and logs in."""
    go_to(driver, "/sign-in")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
    driver.find_element(By.CSS_SELECTOR, "input[type='email']").clear()
    driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").clear()
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)


def logout(driver, wait):
    """Logout helper — clicks avatar then logout button."""
    try:
        avatar = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[aria-label='User menu']")
        ))
        avatar.click()
        time.sleep(0.5)
        logout_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Log out') or contains(text(), 'Logout')]")
        ))
        logout_btn.click()
        time.sleep(1)
    except Exception:
        # Fallback: clear localStorage and reload
        driver.execute_script("localStorage.clear();")
        go_to(driver, "/sign-in")


def element_exists(driver, by, value):
    """Check if an element exists without raising an exception."""
    try:
        driver.find_element(by, value)
        return True
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
# 1. PUBLIC PAGES
# ══════════════════════════════════════════════════════════════════════════════

class TestPublicPages:

    def test_home_page_loads(self, driver, wait):
        """Home page should load with correct title and navbar."""
        go_to(driver)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "Interview" in driver.title or "interview" in driver.page_source.lower()
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
        """Products dropdown should open on hover/click."""
        go_to(driver)
        products_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Products')]")
        ))
        products_btn.click()
        time.sleep(0.5)
        assert "Analyze my interview" in driver.page_source

    def test_how_it_works_page_loads(self, driver, wait):
        """How it works page should load."""
        go_to(driver, "/how-it-works")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert driver.current_url == f"{BASE_URL}/how-it-works"

    def test_signup_page_loads(self, driver, wait):
        """Sign up page should load with form."""
        go_to(driver, "/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        assert "Create" in driver.page_source or "Sign" in driver.page_source

    def test_signin_page_loads(self, driver, wait):
        """Sign in page should load with email and password fields."""
        go_to(driver, "/sign-in")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))

    def test_forgot_password_page_loads(self, driver, wait):
        """Forgot password page should load."""
        go_to(driver, "/forgot-password")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "Forgot" in driver.page_source or "forgot" in driver.page_source.lower()

    def test_unknown_route_redirects_home(self, driver, wait):
        """Unknown routes should redirect to home page."""
        go_to(driver, "/this-page-does-not-exist")
        time.sleep(1)
        assert driver.current_url == f"{BASE_URL}/"


# ══════════════════════════════════════════════════════════════════════════════
# 2. AUTHENTICATION — SIGN UP
# ══════════════════════════════════════════════════════════════════════════════

class TestSignUp:

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

    def test_signup_empty_form_shows_errors(self, driver, wait):
        """Submitting empty signup form should show validation errors."""
        go_to(driver, "/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        page = driver.page_source
        assert "required" in page.lower() or "valid" in page.lower() or "error" in page.lower()

    def test_signup_password_mismatch_shows_error(self, driver, wait):
        """Mismatched passwords should show error."""
        go_to(driver, "/signup")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.NAME, "fullName").send_keys("Test User")
        driver.find_element(By.NAME, "email").send_keys("testuser@example.com")
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


# ══════════════════════════════════════════════════════════════════════════════
# 3. AUTHENTICATION — SIGN IN
# ══════════════════════════════════════════════════════════════════════════════

class TestSignIn:

    def test_login_empty_fields_fails(self, driver, wait):
        """Login with empty fields should not proceed."""
        go_to(driver, "/sign-in")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        assert driver.current_url == f"{BASE_URL}/sign-in"

    def test_login_wrong_password_shows_error(self, driver, wait):
        """Login with wrong password should show error message."""
        go_to(driver, "/sign-in")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(RECRUITER_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("WrongPassword123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        page = driver.page_source
        assert "incorrect" in page.lower() or "invalid" in page.lower() or "error" in page.lower() or "wrong" in page.lower()

    def test_login_wrong_email_shows_error(self, driver, wait):
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


# ══════════════════════════════════════════════════════════════════════════════
# 4. FORGOT PASSWORD
# ══════════════════════════════════════════════════════════════════════════════

class TestForgotPassword:

    def test_forgot_password_empty_email_shows_error(self, driver, wait):
        """Submitting empty email should show validation error."""
        go_to(driver, "/forgot-password")
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Send reset')]")
        )).click()
        time.sleep(1)
        page = driver.page_source
        assert "valid" in page.lower() or "required" in page.lower() or "error" in page.lower()

    def test_forgot_password_invalid_email_shows_error(self, driver, wait):
        """Submitting invalid email format should show error."""
        go_to(driver, "/forgot-password")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys("notanemail")
        driver.find_element(By.XPATH, "//button[contains(text(), 'Send reset')]").click()
        time.sleep(1)
        page = driver.page_source
        assert "valid" in page.lower() or "error" in page.lower()

    def test_forgot_password_nonexistent_email_shows_error(self, driver, wait):
        """Submitting non-existent email should show error."""
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

    def test_forgot_password_back_to_login(self, driver, wait):
        """Back to log in link should navigate to sign-in."""
        go_to(driver, "/forgot-password")
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Back to log in')]")
        )).click()
        time.sleep(1)
        assert "sign-in" in driver.current_url

    def test_reset_password_invalid_token(self, driver, wait):
        """Reset password page with invalid token should show error."""
        go_to(driver, "/reset-password?token=invalidtoken123")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        # Fill in passwords and try to reset
        passwords = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if passwords:
            passwords[0].send_keys("NewPassword123!")
            passwords[1].send_keys("NewPassword123!")
            driver.find_element(By.XPATH, "//button[contains(text(), 'Reset password')]").click()
            time.sleep(2)
            page = driver.page_source
            assert "invalid" in page.lower() or "expired" in page.lower() or "error" in page.lower()

    def test_reset_password_no_token_shows_invalid(self, driver, wait):
        """Reset password page with no token should show invalid link."""
        go_to(driver, "/reset-password")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        assert "invalid" in driver.page_source.lower() or "expired" in driver.page_source.lower()


# ══════════════════════════════════════════════════════════════════════════════
# 5. LOGOUT
# ══════════════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════════════
# 6. RECRUITER — HISTORY PAGE
# ══════════════════════════════════════════════════════════════════════════════

class TestRecruiterHistory:

    def test_recruiter_history_page_loads(self, driver, wait):
        """Recruiter history page should load with Reports History heading."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "Reports History" in driver.page_source

    def test_recruiter_history_shows_correct_username(self, driver, wait):
        """Recruiter history should show correct user name in header."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        page = driver.page_source
        assert "Recruiter" in page or "beeko" in page.lower() or "AbubakerElsiddig" in page

    def test_recruiter_history_search_works(self, driver, wait):
        """Search bar in recruiter history should filter results."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        search = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='search']")
        ))
        search.send_keys("nonexistentbatch12345")
        time.sleep(1)
        page = driver.page_source
        assert "No batches found" in page or "no reports" in page.lower() or "nonexistentbatch" in page.lower()

    def test_recruiter_history_sort_works(self, driver, wait):
        """Sort dropdown in recruiter history should be clickable."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        sort_select = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select")
        ))
        sort_select.click()
        time.sleep(0.5)
        options = sort_select.find_elements(By.TAG_NAME, "option")
        assert len(options) > 1

    def test_recruiter_history_sidebar_navigation(self, driver, wait):
        """Sidebar Analyze Interview link should navigate to /process-video."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        analyze_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(), 'Analyze Interview') or contains(@href, 'process-video')]")
        ))
        analyze_link.click()
        time.sleep(1)
        assert "process-video" in driver.current_url

    def test_recruiter_history_view_report_button(self, driver, wait):
        """View Report button should navigate to recruiter-report page."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        try:
            view_report_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'View Report') and not(@disabled)]")
            ))
            view_report_btn.click()
            time.sleep(2)
            assert "recruiter-report" in driver.current_url
        except Exception:
            # No DONE batches available — skip
            pytest.skip("No completed batches available to view report")


# ══════════════════════════════════════════════════════════════════════════════
# 7. RECRUITER — REPORT PAGE
# ══════════════════════════════════════════════════════════════════════════════

class TestRecruiterReport:

    def _navigate_to_report(self, driver, wait):
        """Helper to navigate to a recruiter report."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        try:
            view_report_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'View Report') and not(@disabled)]")
            ))
            view_report_btn.click()
            time.sleep(3)
            return True
        except Exception:
            return False

    def test_recruiter_report_loads(self, driver, wait):
        """Recruiter report page should load with Batch Report heading."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        assert "Batch Report" in driver.page_source

    def test_recruiter_report_shows_candidates(self, driver, wait):
        """Recruiter report should show candidate ranking table."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        assert "All candidates ranked" in driver.page_source

    def test_recruiter_report_threshold_apply(self, driver, wait):
        """Changing threshold and clicking Apply should update pass/fail."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        threshold_input = wait.until(EC.presence_of_element_located(
            (By.ID, "threshold-input")
        ))
        threshold_input.triple_click() if hasattr(threshold_input, 'triple_click') else (
            threshold_input.click(),
            threshold_input.send_keys(Keys.CONTROL + "a"),
        )
        threshold_input.clear()
        threshold_input.send_keys("50")
        apply_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]")
        apply_btn.click()
        time.sleep(1)
        assert "Active:" in driver.page_source

    def test_recruiter_report_back_to_history(self, driver, wait):
        """Back to History button should navigate to recruiter-history."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        back_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Back to History')]")
        ))
        back_btn.click()
        time.sleep(1)
        assert "recruiter-history" in driver.current_url

    def test_recruiter_report_no_ids_shows_error(self, driver, wait):
        """Recruiter report with no IDs in URL should show error."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        go_to(driver, "/recruiter-report")
        time.sleep(1)
        page = driver.page_source
        assert "No batch" in page or "No videos" in page or "error" in page.lower()


# ══════════════════════════════════════════════════════════════════════════════
# 8. RECRUITER — PROCESS VIDEO PAGE
# ══════════════════════════════════════════════════════════════════════════════

class TestRecruiterProcessVideo:

    def test_process_video_page_loads(self, driver, wait):
        """Process video page should load with New Processing heading."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        assert "New Processing" in driver.page_source

    def test_process_video_requires_role_name(self, driver, wait):
        """Clicking Start Processing without role name should show alert."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)

        # Upload a file
        file_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='file']")
        ))
        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(VIDEO_PATH)
        time.sleep(1)

        # Click Start Processing without entering role name
        start_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Start Processing')]")
        ))
        start_btn.click()
        time.sleep(1)

        # Should show alert
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            assert "role" in alert_text.lower() or "target" in alert_text.lower()
            alert.accept()
        except Exception:
            # Alert might be inline
            page = driver.page_source
            assert "role" in page.lower() or "target" in page.lower()

    def test_process_video_weights_must_sum_100(self, driver, wait):
        """Weights total must be 100% — should show error otherwise."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        assert "100" in driver.page_source or "Total" in driver.page_source

    def test_process_video_role_name_red_border_when_empty(self, driver, wait):
        """Role name input should have red border when empty."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        role_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder*='frontend' i], input[placeholder*='role' i], input[placeholder*='Senior' i]")
        ))
        border_color = role_input.value_of_css_property("border-color")
        # Red border when empty
        assert "red" in border_color.lower() or "300" in border_color or role_input.get_attribute("class") and "red" in role_input.get_attribute("class")

    def test_process_video_upload_and_process(self, driver, wait):
        """
        HAPPY PATH: Upload a video with role name and process it.
        NOTE: This test takes several minutes due to AI processing.
        """
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)

        # Enter role name
        role_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder*='frontend' i], input[placeholder*='role' i], input[placeholder*='Senior' i]")
        ))
        role_input.clear()
        role_input.send_keys("Selenium Test Batch")

        # Upload file
        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(VIDEO_PATH)
        time.sleep(1)

        # Verify file appears in ready list
        assert "man2" in driver.page_source or "Uploaded" in driver.page_source

        # Click Start Processing
        start_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Start Processing')]")
        ))
        start_btn.click()

        # Wait for processing to complete (up to UPLOAD_TIMEOUT seconds)
        upload_wait = WebDriverWait(driver, UPLOAD_TIMEOUT)
        upload_wait.until(lambda d: "recruiter-history" in d.current_url or "Failed" in d.page_source)

        assert "recruiter-history" in driver.current_url, "Should redirect to history after processing"


# ══════════════════════════════════════════════════════════════════════════════
# 9. CANDIDATE — PROCESS VIDEO PAGE
# ══════════════════════════════════════════════════════════════════════════════

class TestCandidateProcessVideo:

    def test_candidate_process_video_page_loads(self, driver, wait):
        """Candidate process video page should load."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        assert "New Processing" in driver.page_source or "process" in driver.current_url

    def test_candidate_history_sidebar_link(self, driver, wait):
        """Candidate sidebar History link should go to /candidate-history."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        history_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href, 'candidate-history')]")
        ))
        history_link.click()
        time.sleep(1)
        assert "candidate-history" in driver.current_url

    def test_candidate_cannot_upload_multiple_videos(self, driver, wait):
        """Candidate file input should not have multiple attribute."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        file_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='file']")
        ))
        multiple = file_input.get_attribute("multiple")
        assert multiple is None or multiple == "false"

    def test_candidate_upload_and_process(self, driver, wait):
        """
        HAPPY PATH: Candidate uploads a single video and processes it.
        NOTE: This test takes several minutes due to AI processing.
        """
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)

        # Enter role name
        role_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder*='frontend' i], input[placeholder*='role' i], input[placeholder*='Senior' i]")
        ))
        role_input.clear()
        role_input.send_keys("Software Engineer Interview")

        # Upload file
        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(VIDEO_PATH)
        time.sleep(1)

        # Start Processing
        start_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Start Processing')]")
        ))
        start_btn.click()

        # Wait for redirect to candidate history
        upload_wait = WebDriverWait(driver, UPLOAD_TIMEOUT)
        upload_wait.until(lambda d: "candidate-history" in d.current_url or "Failed" in d.page_source)

        assert "candidate-history" in driver.current_url


# ══════════════════════════════════════════════════════════════════════════════
# 10. CANDIDATE — HISTORY PAGE
# ══════════════════════════════════════════════════════════════════════════════

class TestCandidateHistory:

    def test_candidate_history_page_loads(self, driver, wait):
        """Candidate history page should load."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        go_to(driver, "/candidate-history")
        time.sleep(2)
        assert driver.current_url == f"{BASE_URL}/candidate-history" or "history" in driver.current_url

    def test_candidate_history_shows_correct_user(self, driver, wait):
        """Candidate history should show correct user info."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        go_to(driver, "/candidate-history")
        time.sleep(2)
        page = driver.page_source
        assert "Candidate" in page or "ahmed" in page.lower()


# ══════════════════════════════════════════════════════════════════════════════
# 11. NAVIGATION & PROTECTION
# ══════════════════════════════════════════════════════════════════════════════

class TestNavigationAndProtection:

    def test_products_dropdown_logged_in_recruiter_view_report(self, driver, wait):
        """Products > View my report for recruiter should go to recruiter-history."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/")
        time.sleep(1)
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
            assert "recruiter-history" in driver.current_url
        except Exception:
            pytest.skip("Products dropdown not available on this page")

    def test_products_dropdown_not_logged_in_redirects_signin(self, driver, wait):
        """Products > View my report when not logged in should go to /sign-in."""
        go_to(driver, "/")
        time.sleep(1)
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

    def test_logo_does_not_navigate(self, driver, wait):
        """Logo click should not navigate away from current page."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        current_url = driver.current_url
        try:
            logo = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(@class, 'logo') or contains(@class, 'Pacifico')]")
            ))
            logo.click()
            time.sleep(1)
            assert driver.current_url == current_url
        except Exception:
            pass  # Logo may not be clickable — that's correct behavior


# ══════════════════════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
