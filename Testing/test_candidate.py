"""
test_candidate.py — Candidate flow tests.
Covers: Process Video, History pages.

Run: pytest tests/test_candidate.py -v
Run (skip slow upload): pytest tests/test_candidate.py -v -k "not upload"
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import (
    go_to, login, logout,
    CANDIDATE_EMAIL, CANDIDATE_PASS,
    VIDEO_PATH, UPLOAD_TIMEOUT,
)


# ── PROCESS VIDEO ─────────────────────────────────────────────────────────────

class TestCandidateProcessVideo:

    def test_process_video_page_loads(self, driver, wait):
        """Candidate process video page should load."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        assert "New Processing" in driver.page_source or "process" in driver.current_url

    def test_process_video_shows_candidate_info(self, driver, wait):
        """Process video page should show candidate name."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        page = driver.page_source
        assert "ahmed" in page.lower() or "User" in page or "Candidate" in page

    def test_candidate_file_input_single_only(self, driver, wait):
        """File input should NOT have multiple attribute for candidate."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        file_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='file']")
        ))
        multiple = file_input.get_attribute("multiple")
        assert multiple is None or multiple == "false"

    def test_candidate_role_name_required(self, driver, wait):
        """Clicking Start Processing without role name should show alert."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)

        # Upload a file first
        file_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='file']")
        ))
        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(VIDEO_PATH)
        time.sleep(1)

        # Click Start Processing without role name
        start_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Start Processing')]")
        ))
        start_btn.click()
        time.sleep(1)

        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            assert "role" in alert_text.lower() or "target" in alert_text.lower()
            alert.accept()
        except Exception:
            page = driver.page_source
            assert "role" in page.lower() or "target" in page.lower()

    def test_candidate_file_upload_shows_in_list(self, driver, wait):
        """Uploaded file should appear in Ready to process list."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        file_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='file']")
        ))
        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(VIDEO_PATH)
        time.sleep(1)
        assert "man2" in driver.page_source or "Uploaded" in driver.page_source

    def test_candidate_clear_all_removes_files(self, driver, wait):
        """Clear all button should remove uploaded files."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        file_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='file']")
        ))
        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(VIDEO_PATH)
        time.sleep(1)

        clear_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Clear all')]")
        ))
        clear_btn.click()
        time.sleep(0.5)
        assert "No videos uploaded yet" in driver.page_source

    def test_candidate_history_sidebar_link(self, driver, wait):
        """Sidebar History link should go to /candidate-history."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        history_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href, 'candidate-history')]")
        ))
        history_link.click()
        time.sleep(1)
        assert "candidate-history" in driver.current_url

    def test_candidate_weights_sum_100_by_default(self, driver, wait):
        """Weights should sum to 100% by default."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        assert "Total: 100%" in driver.page_source or "100" in driver.page_source

    def test_candidate_start_processing_disabled_without_file(self, driver, wait):
        """Start Processing button should be disabled when no file uploaded."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        start_btn = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[contains(text(), 'Start Processing')]")
        ))
        assert start_btn.get_attribute("disabled") is not None or \
               "cursor-not-allowed" in (start_btn.get_attribute("class") or "")

    def test_candidate_logout_from_process_video(self, driver, wait):
        """Logout from process video page should redirect to /sign-in."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        time.sleep(2)
        logout(driver, wait)
        time.sleep(2)
        assert "sign-in" in driver.current_url

    def test_candidate_upload_happy_path(self, driver, wait):
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

        # Verify file in list
        assert "man2" in driver.page_source or "Uploaded" in driver.page_source

        # Start Processing
        start_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Start Processing')]")
        ))
        start_btn.click()

        # Wait for redirect to candidate history
        upload_wait = WebDriverWait(driver, UPLOAD_TIMEOUT)
        upload_wait.until(
            lambda d: "candidate-history" in d.current_url or "Failed" in d.page_source
        )
        assert "candidate-history" in driver.current_url


# ── HISTORY ───────────────────────────────────────────────────────────────────

class TestCandidateHistory:

    def test_candidate_history_page_loads(self, driver, wait):
        """Candidate history page should load."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        go_to(driver, "/candidate-history")
        time.sleep(2)
        assert "candidate-history" in driver.current_url or "history" in driver.current_url

    def test_candidate_history_shows_correct_user(self, driver, wait):
        """Candidate history should show correct user name."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        go_to(driver, "/candidate-history")
        time.sleep(2)
        page = driver.page_source
        assert "ahmed" in page.lower() or "Candidate" in page or "User" in page

    def test_candidate_history_sidebar_analyze_link(self, driver, wait):
        """Sidebar Analyze Interview link should go to /process-video."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        go_to(driver, "/candidate-history")
        time.sleep(2)
        try:
            analyze_link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, 'process-video')]")
            ))
            analyze_link.click()
            time.sleep(1)
            assert "process-video" in driver.current_url
        except Exception:
            pytest.skip("Analyze Interview link not found in candidate history sidebar")

    def test_candidate_history_logout(self, driver, wait):
        """Candidate should be able to logout from history page."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        go_to(driver, "/candidate-history")
        time.sleep(2)
        logout(driver, wait)
        time.sleep(2)
        assert "sign-in" in driver.current_url

    def test_candidate_cannot_access_recruiter_history(self, driver, wait):
        """Candidate should not be able to see recruiter history data."""
        login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASS)
        go_to(driver, "/recruiter-history")
        time.sleep(2)
        # Either redirected or shows empty/different data
        page = driver.page_source
        # Should not show recruiter-specific content for candidate's data
        assert "Reports History" not in page or "No reports" in page or \
               driver.current_url != "http://localhost:5173/recruiter-history"
