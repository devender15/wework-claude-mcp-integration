from appium import webdriver
from appium.options.android import UiAutomator2Options

UDID = "UORCQC6HEAZHRCN7"
APP_PACKAGE = "in.co.wework.spacecraft"
APP_ACTIVITY = "in.co.wework.spacecraft.SpacecraftActivity"

opts = UiAutomator2Options()
opts.platform_name = "Android"
opts.automation_name = "UiAutomator2"
opts.udid = UDID
opts.no_reset = True
opts.new_command_timeout = 180
opts.app_package = APP_PACKAGE
opts.app_activity = APP_ACTIVITY

driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", options=opts)
print("✅ Session started. Current package:", driver.current_package)
driver.quit()
print("✅ Done")

