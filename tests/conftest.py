import pytest
from selene import browser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tests.config import USE_SELENOID, DEFAULT_BROWSER_NAME, DEFAULT_BROWSER_VERSION, DEFAULT_SELENOID_URL
from utils import attach
from dotenv import load_dotenv
import os


def pytest_addoption(parser):
    parser.addoption(
        "--browser_name",
        action="store",
        default="chrome",
        help="Укажите браузер: chrome или firefox"
    )
    parser.addoption(
        "--browser_version",
        action="store",
        default="128.0",
        help="Укажите версию браузера"  # chrome 128.0, 127.0, firefox 124.0, 125.0
    )
    parser.addoption(
        "--selenoid_url",
        action="store",
        default="selenoid.autotests.cloud",
        help="URL Selenoid"
    )


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(scope="function")
def setup_browser(request):
    options = Options()
    options.page_load_strategy = 'eager'
    options.add_argument("--window-size=1280,1080")
    # Определяем, используется ли Selenoid
    print(f" Selenoid: {USE_SELENOID}")
    video_url = ""

    if USE_SELENOID:
        browser_name = request.config.getoption('--browser_name')
        browser_name = browser_name if browser_name != "" else DEFAULT_BROWSER_NAME
        browser_version = request.config.getoption('--browser_version')
        browser_version = browser_version if browser_version != "" else DEFAULT_BROWSER_VERSION
        selenoid_url = request.config.getoption('--selenoid_url')
        selenoid_url = selenoid_url if selenoid_url != "" else DEFAULT_SELENOID_URL

        # Конфигурация для Selenoid
        selenoid_capabilities = {
            "browserName": browser_name,
            "browserVersion": browser_version,
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

        driver = webdriver.Remote(
            command_executor=f"https://{selenoid_login}:{selenoid_pass}@{selenoid_url}/wd/hub",
            options=options
        )
        print(f"Браузер в SELENOID: {browser_name}:{browser_version}")
        video_url = selenoid_url
    else:
        driver = webdriver.Chrome(options=options)

    browser.config.driver = driver
    browser.config.base_url = 'https://demoqa.com'
    print(f"Установленный размер окна: {driver.get_window_size()}")
    yield browser
    attach.add_screenshot(browser)
    attach.add_logs(browser)
    attach.add_html(browser)
    attach.add_video(browser, video_url)
    driver.quit()
