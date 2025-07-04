import pytest
from selene import browser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from demoga_tests.model.browser_settings import is_selenoid_enabled
from utils import attach
from dotenv import load_dotenv
import os


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(scope="function")
def setup_browser():
    options = Options()
    options.page_load_strategy = 'eager'
    options.add_argument("--window-size=1280,1080")
    # Определяем, используется ли Selenoid
    use_selenoid = is_selenoid_enabled()
    print(f" Selenoid: {use_selenoid}")
    if use_selenoid:
        # Конфигурация для Selenoid
        selenoid_capabilities = {
            "browserName": "chrome",
            "browserVersion": "128.0",
            "selenoid:options": {
                "enableLog": True,
                "enableVNC": True,
                "enableVideo": True
            },
            "goog:loggingPrefs": {"browser": "ALL"}
        }
        options.capabilities.update(selenoid_capabilities)

        selenoid_login = os.getenv("SELENOID_LOGIN")
        selenoid_pass = os.getenv("SELENOID_PASS")
        selenoid_url = os.getenv("SELENOID_URL")
        driver = webdriver.Remote(
            command_executor=f"https://{selenoid_login}:{selenoid_pass}@{selenoid_url}/wd/hub",
            options=options
        )
    else:
        driver = webdriver.Chrome(options=options)

    browser.config.driver = driver
    browser.config.base_url = 'https://demoqa.com'
    print(f"Установленный размер окна: {driver.get_window_size()}")

    yield browser
    attach.add_screenshot(browser)
    attach.add_logs(browser)
    attach.add_html(browser)
    if use_selenoid:
        attach.add_video(browser, selenoid_url)
    driver.quit()