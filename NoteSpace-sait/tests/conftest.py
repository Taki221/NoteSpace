from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Корень проекта нужен, чтобы находить HTML-страницы в папке hex.
PROJECT_ROOT = Path(__file__).resolve().parents[1]


# Фикстура запускает один браузер для тестов этого файла и закрывает его после.
@pytest.fixture(scope="module")
def driver():
    options = Options()
    # Запускает Chrome без окна и задаёт начальный размер рабочего окна.
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")

    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


# Фикстура открывает локальные страницы сайта по имени HTML-файла.
@pytest.fixture
def open_page(driver):
    def _open_page(file_name):
        page_path = PROJECT_ROOT / "hex" / file_name
        driver.get(page_path.as_uri())

    return _open_page


#для запуск
# python -m pytest tests -v