import calendar
import json
import shutil
from datetime import date, datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_chromedriver_path() -> str:
    return shutil.which("chromedriver")


def get_webdriver_service() -> Service:
    service = Service(
        executable_path=get_chromedriver_path(),
    )
    return service


def generate_12_months_list(start_date=datetime.now().date()):
    months_list = []
    year = start_date.year
    month = start_date.month
    day = start_date.day

    for _ in range(12):
        last_day = calendar.monthrange(year, month)[1]
        valid_day = min(day, last_day)

        months_list.append(date(year, month, valid_day).strftime("%Y-%m-%d"))

        month += 1
        if month > 12:
            month = 1
            year += 1

    return months_list


def save_json(filename: str, data: dict):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)  # indent=4 is optional but makes it readable


def read_json(filename):
    with open(filename, "r") as f:
        info = json.loads(f.read())
        return info


def get_driver():

    options = webdriver.ChromeOptions()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument('--ignore-certificate-errors')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # options = get_webdriver_options()
    service = get_webdriver_service()
    return webdriver.Chrome(options=options, service=service)


def render_html(url, tag_to_wait=None, timeout=10):
    driver = get_driver()
    driver.get(url)
    if tag_to_wait:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, tag_to_wait))
        )
    return driver.page_source
