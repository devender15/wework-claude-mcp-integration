import subprocess
import re
from appium import webdriver
from appium.options.android import UiAutomator2Options

APPIUM_SERVER = "http://127.0.0.1:4723"
APP_PACKAGE = "in.co.wework.spacecraft"
APP_ACTIVITY = "in.co.wework.spacecraft.SpacecraftActivity"


def get_udid() -> str:
    """
    Auto-detects the first connected Android device via adb.
    Works for:
    - USB
    - Wi-Fi (IP:5555)
    - Wi-Fi (mDNS adb-xxxx._adb-tls-connect._tcp)
    """
    out = subprocess.check_output(["adb", "devices"], text=True)

    for line in out.splitlines():
        if "\tdevice" in line and not line.startswith("List"):
            return line.split("\t")[0]

    raise RuntimeError("No connected Android device found via adb")


def create_driver() -> webdriver.Remote:
    udid = get_udid()

    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.automation_name = "UiAutomator2"
    opts.udid = udid
    opts.no_reset = True
    opts.new_command_timeout = 300
    opts.app_package = APP_PACKAGE
    opts.app_activity = APP_ACTIVITY

    # Stability flags (you already learned why these matter)
    opts.set_capability("appium:ignoreHiddenApiPolicyError", True)
    opts.set_capability("appium:disableWindowAnimation", True)
    opts.set_capability("appium:adbExecTimeout", 120000)

    return webdriver.Remote(APPIUM_SERVER, options=opts)
