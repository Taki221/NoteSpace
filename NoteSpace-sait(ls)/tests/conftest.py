from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

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


# Запускает временный локальный HTTP-сервер для проверки HTTP-статусов файлов.
@pytest.fixture
def http_server():
    handler = partial(
        SimpleHTTPRequestHandler,
        directory=str(PROJECT_ROOT),
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()

    yield f"http://127.0.0.1:{server.server_port}"

    server.shutdown()
    server.server_close()
    server_thread.join()


#для запуск
# python -m pytest tests -v