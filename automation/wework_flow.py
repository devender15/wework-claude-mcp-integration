from __future__ import annotations
import calendar
import datetime as dt
from typing import List

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder

from automation.driver import create_driver


# =========================
# CONFIG
# =========================

APPIUM_SERVER = "http://127.0.0.1:4723"

UDID = "UORCQC6HEAZHRCN7"

APP_PACKAGE = "in.co.wework.spacecraft"
APP_ACTIVITY = "in.co.wework.spacecraft.SpacecraftActivity"



# =========================
# HELPERS
# =========================

def wait_click(driver, by, value, timeout=20):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    el.click()
    return el

def swipe_left_to_right(driver, by, value, duration=1300, steps=6, end_hold_ms=300):
    # add wait to ensure element is interactable
    el = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((by, value))
    )

    rect = el.rect

    start_x = rect["x"] + int(rect["width"] * 0.05)

    # End slightly BEYOND the right edge (important)
    end_x = rect["x"] + rect["width"] + 5  # near right edge

    y = rect["y"] + rect["height"] // 2               # vertical center

    finger = PointerInput("touch", "finger")
    actions = ActionBuilder(driver, mouse=finger)

    actions.pointer_action.move_to_location(start_x, y)
    actions.pointer_action.pointer_down()

    step_pause = (duration / steps) / 1000  # ms → seconds
    delta = (end_x - start_x) / steps

    current_x = start_x
    for _ in range(steps):
        current_x += delta
        actions.pointer_action.pause(step_pause)
        actions.pointer_action.move_to_location(int(current_x), y)

    actions.pointer_action.pause(end_hold_ms / 1000)

    actions.pointer_action.pointer_up()
    actions.perform()



def month_diff(today: dt.date, target: dt.date) -> int:
    return (target.year - today.year) * 12 + (target.month - today.month)


def date_accessibility_label(date: dt.date) -> str:
    weekday = calendar.day_name[date.weekday()]
    month = calendar.month_name[date.month]
    return f"{date.day}, {weekday}, {month} {date.day}, {date.year}"


def launch_app(driver):
    driver.terminate_app(APP_PACKAGE)
    driver.activate_app(APP_PACKAGE)


def select_building(driver, building_name: str):
    # Preferred dynamic selector
    try:
        wait_click(
            driver,
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().descriptionContains("{building_name}")',
            timeout=30
        )
        return
    except TimeoutException:
        raise RuntimeError(f"Building '{building_name}' not found")


# =========================
# CORE FLOW
# =========================

def book_single_date(driver, target_date: dt.date, building_name: str):
    today = dt.date.today()

    # Desk
    wait_click(driver, AppiumBy.ACCESSIBILITY_ID, "Desk")

    # Open date picker (dynamic)
    wait_click(
        driver,
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("All day")'
    )

    # Navigate months
    diff = month_diff(today.replace(day=1), target_date.replace(day=1))
    for _ in range(max(0, diff)):
        wait_click(driver, AppiumBy.ACCESSIBILITY_ID, "Next month")

    # Select day
    day_label = date_accessibility_label(target_date)
    wait_click(driver, AppiumBy.ACCESSIBILITY_ID, day_label)

    # Confirm date
    wait_click(driver, AppiumBy.ACCESSIBILITY_ID, "Confirm and proceed")

    # Select building
    select_building(driver, building_name)

    # Final booking
    # wait_click(driver, AppiumBy.ACCESSIBILITY_ID, "Book a desk")
    swipe_left_to_right(driver, AppiumBy.ACCESSIBILITY_ID, "Book a desk")


# =========================
# PUBLIC API
# =========================

def book_desks(
    dates: List[str],
    building_name: str
):
    driver = create_driver()

    try:
        launch_app(driver)

        for d in dates:
            try:
                print(f"📅 Booking desk for {d}")
                target = dt.date.fromisoformat(d)
                book_single_date(driver, target, building_name)
                print(f"✅ Booked {d}")

                # going back to the homepage
                wait_click(driver, AppiumBy.ACCESSIBILITY_ID, "Scrim")
                wait_click(driver, AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().className(\"android.widget.Button\").instance(0)")

            except Exception as e:
                print(f"❌ Failed for {d}: {e}")
                launch_app(driver)

    finally:
        driver.quit()


# =========================
# RUN
# =========================

if __name__ == "__main__":
    book_desks(
        dates=[
            # "2026-02-11"
            "2026-02-25",
            # "2026-02-13"
        ],
        building_name="Two Horizon Center"
    )

