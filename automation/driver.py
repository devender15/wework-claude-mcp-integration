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
    try:
        out = subprocess.check_output(
            ["adb", "devices"],
            text=True,
            timeout=10,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        # Negative returncode often means process died from a signal (e.g. -5 = SIGTRAP)
        msg = (
            "adb failed or crashed (e.g. when running inside Docker on macOS the container cannot see your device). "
            "Fix: run the MCP server on the host: in Claude Desktop config use command 'python', args ['-m', 'app_mcp.server'], "
            "cwd set to this project; run Appium on the host (e.g. 'appium --use-plugins=inspector') so adb and Appium both see the device."
        )
        if getattr(e, "returncode", None) is not None and e.returncode < 0:
            raise RuntimeError(msg) from e
        raise RuntimeError(f"{msg} Details: {e}") from e
    except Exception as e:
        raise RuntimeError(
            "adb failed (if in Docker on macOS, run MCP server and Appium on the host instead). "
            f"Details: {e}"
        ) from e

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
    # Give UiAutomator2 instrumentation more time to start (helps "instrumentation process cannot be initialized")
    opts.set_capability("appium:uiautomator2ServerLaunchTimeout", 120000)

    return webdriver.Remote(APPIUM_SERVER, options=opts)
