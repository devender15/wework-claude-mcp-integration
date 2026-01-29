"""
WeWork India (Spacecraft) Desk Booking Automation - Appium + Android 11
- Uses accessibility-id selectors captured via Appium Inspector recording
- Adds explicit waits + retries to reduce flakiness
"""

from __future__ import annotations

import calendar
import datetime as dt
from typing import Optional

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# -------------------------
# CONFIG (EDIT THESE)
# -------------------------

APPIUM_SERVER_URL = "http://127.0.0.1:4723"  # you're using Appium v3 default base path (/)
UDID = "UORCQC6HEAZHRCN7"  # <-- from `adb devices`

APP_PACKAGE = "in.co.wework.spacecraft"
APP_ACTIVITY = "in.co.wework.spacecraft.SpacecraftActivity"

# Your recorded center selector (brittle). Kept as primary since you confirmed it works.
CENTER_ACCESSIBILITY_BLOB = '86\nTwo Horizon Center\n4.6\n5th Floor\n2.51 km'

# If the app occasionally shows a slightly different "All day" string, we handle it loosely.
DATE_PICKER_TEMPLATE_PREFIX = ""  # optional if you want to enforce "Fri, 30 Jan · All day"


# -------------------------
# HELPERS
# -------------------------

def _wait_clickable(driver, by, value, timeout=25):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )

def _wait_present(driver, by, value, timeout=25):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def _safe_click(driver, by, value, timeout=25, label=""):
    el = _wait_clickable(driver, by, value, timeout=timeout)
    el.click()
    return el

def _month_diff(from_date: dt.date, to_date: dt.date) -> int:
    """How many times to press 'Next month' from from_date's month to reach to_date's month."""
    return (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month)

def _a11y_day_label(target: dt.date) -> str:
    """
    Recreate the accessibility label you saw:
    '11, Wednesday, February 11, 2026'
    """
    weekday_name = calendar.day_name[target.weekday()]      # Wednesday
    month_name = calendar.month_name[target.month]          # February
    return f"{target.day}, {weekday_name}, {month_name} {target.day}, {target.year}"

def _find_center(driver) -> None:
    """
    Select the center. Primary: your recorded long accessibility string.
    Fallback: scroll and match partial text via UiSelector.
    """
    try:
        _safe_click(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().description("{CENTER_ACCESSIBILITY_BLOB}")',
                    timeout=25, label="Center (recorded blob)")
        return
    except TimeoutException:
        pass

    # Fallback: look for "Two Horizon Center" in content-desc and click it.
    # This is usually safer if the distance/rating changes.
    try:
        el = _wait_clickable(
            driver,
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().descriptionContains("Two Horizon Center")',
            timeout=25,
        )
        el.click()
        return
    except TimeoutException as e:
        raise RuntimeError("Could not find/select the center. The selector likely changed.") from e


# -------------------------
# MAIN FLOW
# -------------------------

def make_driver() -> webdriver.Remote:
    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.automation_name = "UiAutomator2"
    opts.udid = UDID
    opts.no_reset = True
    opts.new_command_timeout = 180

    # Workaround for Android 11 devices that block hidden_api_policy setting edits
    opts.set_capability("appium:ignoreHiddenApiPolicyError", True)

    # App under test
    opts.app_package = APP_PACKAGE
    opts.app_activity = APP_ACTIVITY

    return webdriver.Remote(APPIUM_SERVER_URL, options=opts)


def book_desk(
    target_date: str,
    confirm_booking: bool = False,
    advance_months_max: int = 24,
) -> None:
    """
    Automate WeWork desk booking for a given date.

    Args:
        target_date: "YYYY-MM-DD" e.g. "2026-02-11"
        confirm_booking: If False, stops right before final booking tap as a safety guard.
        advance_months_max: safety to avoid infinite loops when month nav breaks.
    """
    target = dt.date.fromisoformat(target_date)
    today = dt.date.today()

    driver = make_driver()
    wait = WebDriverWait(driver, 25)

    try:
        # 1) Open Desk flow
        _safe_click(driver, AppiumBy.ACCESSIBILITY_ID, "Desk", timeout=30, label="Desk")

        # 2) Open date picker
        # Your recording used a full string "Fri, 30 Jan · All day". This will change daily.
        # So we click the first element that looks like it contains "All day".
        try:
            # Prefer a robust selector instead of exact match:
            el_date = _wait_clickable(
                driver,
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().descriptionContains("All day")',
                timeout=25,
            )
            el_date.click()
        except TimeoutException:
            # fallback to your recorded exact label (works only if it matches current UI)
            _safe_click(driver, AppiumBy.ACCESSIBILITY_ID, "Fri, 30 Jan · All day", timeout=10, label="Date (exact)")

        # 3) Move months forward/backward as needed
        # Your flow pressed "Next month" once. We'll compute how many times needed.
        diff = _month_diff(today.replace(day=1), target.replace(day=1))

        if diff > 0:
            if diff > advance_months_max:
                raise RuntimeError(f"Refusing to press Next month {diff} times (safety limit {advance_months_max}).")
            for _ in range(diff):
                _safe_click(driver, AppiumBy.ACCESSIBILITY_ID, "Next month", timeout=15, label="Next month")
        elif diff < 0:
            # If your UI has "Previous month" available, we support it.
            # If not present, you can remove this block.
            for _ in range(abs(diff)):
                _safe_click(driver, AppiumBy.ACCESSIBILITY_ID, "Previous month", timeout=15, label="Previous month")

        # 4) Select specific day
        day_label = _a11y_day_label(target)
        _safe_click(driver, AppiumBy.ACCESSIBILITY_ID, day_label, timeout=25, label=f"Day {day_label}")

        # 5) Confirm & proceed
        _safe_click(driver, AppiumBy.ACCESSIBILITY_ID, "Confirm and proceed", timeout=25, label="Confirm and proceed")

        # 6) Select center
        _find_center(driver)

        # 7) "Book a desk" - final step (guarded)
        if not confirm_booking:
            print("🛑 Safety stop: reached 'Book a desk' step. Set confirm_booking=True to actually book.")
            return

        _safe_click(driver, AppiumBy.ACCESSIBILITY_ID, "Book a desk", timeout=25, label="Book a desk")
        print("✅ Booking flow completed.")

    finally:
        driver.quit()


if __name__ == "__main__":
    # Example run:
    # - First run with confirm_booking=False to verify navigation safely.
    book_desk(target_date="2026-02-11", confirm_booking=False)

