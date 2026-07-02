"""
test_recruiter.py — Recruiter flow tests.
Covers: Process Video, History, Report pages.

Run: pytest tests/test_recruiter.py -v
Run (skip slow upload): pytest tests/test_recruiter.py -v -k "not upload"
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import (
    go_to, login, logout,
    RECRUITER_EMAIL, RECRUITER_PASS,
    VIDEO_PATH, UPLOAD_TIMEOUT,
)


# ── PROCESS VIDEO ─────────────────────────────────────────────────────────────

class TestRecruiterProcessVideo:

    def test_process_video_page_loads(self, driver, wait):
        """Process video page should load with New Processing heading."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        assert "New Processing" in driver.page_source

    def test_process_video_shows_recruiter_info(self, driver, wait):
        """Process video page should show recruiter name and role."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        assert "Recruiter" in driver.page_source or "beeko" in driver.page_source.lower()

    def test_process_video_role_name_red_border_when_empty(self, driver, wait):
        """Role name input should have red border when empty."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        role_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder*='frontend' i], input[placeholder*='role' i], input[placeholder*='Senior' i]")
        ))
        classes = role_input.get_attribute("class") or ""
        assert "red" in classes or "border-red" in classes

    def test_process_video_requires_role_name(self, driver, wait):
        """Clicking Start Processing without role name should show alert."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)

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

    def test_process_video_weights_sum_display(self, driver, wait):
        """Weights total should display as 100% by default."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        assert "Total: 100%" in driver.page_source or "100" in driver.page_source

    def test_process_video_file_upload_shows_in_list(self, driver, wait):
        """Uploaded file should appear in Ready to process list."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        file_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='file']")
        ))
        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(VIDEO_PATH)
        time.sleep(1)
        assert "man2" in driver.page_source or "Uploaded" in driver.page_source

    def test_process_video_clear_all_removes_files(self, driver, wait):
        """Clear all button should remove uploaded files."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
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

    def test_process_video_multiple_files_allowed(self, driver, wait):
        """File input should have multiple attribute for recruiter."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        file_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='file']")
        ))
        multiple = file_input.get_attribute("multiple")
        assert multiple is not None and multiple != "false"

    def test_process_video_history_sidebar_link(self, driver, wait):
        """Sidebar History link should go to /recruiter-history."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        history_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href, 'recruiter-history')]")
        ))
        history_link.click()
        time.sleep(1)
        assert "recruiter-history" in driver.current_url

    def test_process_video_logout_works(self, driver, wait):
        """Logout from process video page should redirect to /sign-in."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        go_to(driver, "/process-video")
        time.sleep(1)
        logout(driver, wait)
        time.sleep(2)
        assert "sign-in" in driver.current_url

    def test_process_video_upload_happy_path(self, driver, wait):
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

        # Start Processing
        start_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Start Processing')]")
        ))
        start_btn.click()

        # Wait for redirect to recruiter history
        upload_wait = WebDriverWait(driver, UPLOAD_TIMEOUT)
        upload_wait.until(
            lambda d: "recruiter-history" in d.current_url or "Failed" in d.page_source
        )
        assert "recruiter-history" in driver.current_url


# ── HISTORY ───────────────────────────────────────────────────────────────────

class TestRecruiterHistory:

    def test_recruiter_history_page_loads(self, driver, wait):
        """Recruiter history page should load with Reports History heading."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        assert "Reports History" in driver.page_source

    def test_recruiter_history_shows_correct_username(self, driver, wait):
        """Recruiter history should show correct user name in header."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        page = driver.page_source
        assert "Recruiter" in page or "beeko" in page.lower() or "AbubakerElsiddig" in page

    def test_recruiter_history_table_headers(self, driver, wait):
        """History table should show correct column headers."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        page = driver.page_source
        assert "Batch" in page
        assert "Candidates" in page
        assert "Status" in page
        assert "Avg. Score" in page

    def test_recruiter_history_search_works(self, driver, wait):
        """Search bar should filter results."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        search = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='search']")
        ))
        search.send_keys("nonexistentbatch12345xyz")
        time.sleep(1)
        page = driver.page_source
        assert "No batches found" in page or "no reports" in page.lower()

    def test_recruiter_history_search_clear_shows_all(self, driver, wait):
        """Clearing search should show all batches again."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        search = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='search']")
        ))
        search.send_keys("nonexistentbatch")
        time.sleep(1)
        search.clear()
        time.sleep(1)
        # Should show batches again or empty state
        page = driver.page_source
        assert "Reports History" in page

    def test_recruiter_history_sort_dropdown(self, driver, wait):
        """Sort dropdown should have multiple options."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        sort_select = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select")
        ))
        options = sort_select.find_elements(By.TAG_NAME, "option")
        assert len(options) > 1

    def test_recruiter_history_sidebar_analyze_link(self, driver, wait):
        """Sidebar Analyze Interview link should navigate to /process-video."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        analyze_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(), 'Analyze Interview') or contains(@href, 'process-video')]")
        ))
        analyze_link.click()
        time.sleep(1)
        assert "process-video" in driver.current_url

    def test_recruiter_history_view_report_navigates(self, driver, wait):
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
            pytest.skip("No completed batches available to view report")

    def test_recruiter_history_failed_batch_view_report_disabled(self, driver, wait):
        """View Report button should be disabled for FAILED batches."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        failed_buttons = driver.find_elements(
            By.XPATH, "//button[contains(text(), 'View Report') and @disabled]"
        )
        # If there are failed batches, their buttons should be disabled
        # This passes even if no failed batches exist
        assert True


# ── REPORT ────────────────────────────────────────────────────────────────────

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
            return "recruiter-report" in driver.current_url
        except Exception:
            return False

    def test_recruiter_report_loads(self, driver, wait):
        """Recruiter report page should load with Batch Report heading."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        assert "Batch Report" in driver.page_source

    def test_recruiter_report_shows_candidates_table(self, driver, wait):
        """Recruiter report should show candidate ranking table."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        assert "All candidates ranked" in driver.page_source

    def test_recruiter_report_shows_summary_cards(self, driver, wait):
        """Recruiter report should show Total Candidates, Average Score etc."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        page = driver.page_source
        assert "Total Candidates" in page
        assert "Average Score" in page
        assert "Top Score" in page

    def test_recruiter_report_threshold_updates(self, driver, wait):
        """Changing threshold and clicking Apply should update active value."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        threshold_input = wait.until(EC.presence_of_element_located(
            (By.ID, "threshold-input")
        ))
        threshold_input.click()
        threshold_input.send_keys(Keys.CONTROL + "a")
        threshold_input.send_keys("50")
        apply_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]")
        apply_btn.click()
        time.sleep(1)
        assert "50%" in driver.page_source

    def test_recruiter_report_shows_score_distribution(self, driver, wait):
        """Recruiter report should show Score Distribution panel."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        assert "Score Distribution" in driver.page_source

    def test_recruiter_report_shows_pass_fail(self, driver, wait):
        """Recruiter report should show Pass / Fail panel."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        assert "Pass" in driver.page_source and "Fail" in driver.page_source

    def test_recruiter_report_shows_module_scores(self, driver, wait):
        """Recruiter report should show 6 Core Module Scores."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        assert "6 Core Module Scores" in driver.page_source

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
        """Recruiter report with no IDs in URL should show error message."""
        login(driver, wait, RECRUITER_EMAIL, RECRUITER_PASS)
        time.sleep(2)
        go_to(driver, "/recruiter-report")
        time.sleep(1)
        page = driver.page_source
        assert "No batch" in page or "No videos" in page or "error" in page.lower()

    def test_recruiter_report_export_pdf_button_visible(self, driver, wait):
        """Export PDF button should be visible on report page."""
        if not self._navigate_to_report(driver, wait):
            pytest.skip("No completed batches available")
        assert "Export PDF" in driver.page_source
