from urllib.error import HTTPError
from urllib.request import urlopen

import pytest


# Список HTML-страниц светлой и тёмной версий, которые должны отвечать кодом 200.
SITE_PAGES = [
    "hex/index.html",
    "hex/login.html",
    "hex/Notes.html",
    "hex/hex/index.html",
    "hex/hex/login.html",
    "hex/hex/Notes.html",
]


# Проверяет, что локальный сервер возвращает успешный HTTP-статус для страницы.
@pytest.mark.parametrize("page_path", SITE_PAGES)
def test_site_pages_return_success_status(http_server, page_path):
    with urlopen(f"{http_server}/{page_path}") as response:
        assert response.status == 200


# Проверяет, что для отсутствующего файла сервер возвращает HTTP-статус 404.
def test_missing_page_returns_not_found_status(http_server):
    with pytest.raises(HTTPError) as error:
        urlopen(f"{http_server}/hex/page-that-does-not-exist.html")

    assert error.value.code == 404
