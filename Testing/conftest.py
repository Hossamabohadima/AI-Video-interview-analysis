"""
conftest.py — Shared fixtures and helpers for all test files.
Pytest automatically loads this file before running any tests.
"""

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
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

WAIT_TIMEOUT    = 15    # seconds
UPLOAD_TIMEOUT  = 300   # seconds (5 min for video processing)


# ── DRIVER FIXTURE ────────────────────────────────────────────────────────────

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
    """WebDriverWait instance for each test."""
    return WebDriverWait(driver, WAIT_TIMEOUT)


# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def go_to(driver, path="/"):
    """Navigate to a page."""
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
        driver.execute_script("localStorage.clear();")
        go_to(driver, "/sign-in")


def element_exists(driver, by, value):
    """Check if an element exists without raising an exception."""
    try:
        driver.find_element(by, value)
        return True
    except Exception:
        return False
