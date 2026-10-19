import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait


# Максимальное время ожидания элементов и обновления страницы.
WAIT_SECONDS = 5

# Страница, CSS-селектор, свойство стиля и его ожидаемое значение в тёмной теме.
THEME_PAGES = [
    ("index.html", ".hero", "color", "rgb(245, 247, 251)"),
    ("login.html", ".login-card", "backgroundColor", "rgb(22, 28, 37)"),
    ("Notes.html", ".sidebar", "backgroundColor", "rgb(17, 22, 30)"),
]


# Открывает страницу тёмной версии и сбрасывает тему в светлую перед проверкой.
def open_page_with_light_theme(driver, open_page, page_name):
    open_page(f"hex/{page_name}")
    driver.execute_script("localStorage.removeItem('zametki-theme')")
    driver.refresh()
    WebDriverWait(driver, WAIT_SECONDS).until(
        conditions.presence_of_element_located((By.CSS_SELECTOR, ".theme"))
    )


# Проверяет переключение тем, оформление страницы и подписи кнопки на каждой странице.
@pytest.mark.parametrize(
    ("page_name", "styled_selector", "style_property", "dark_value"),
    THEME_PAGES,
)
def test_dark_theme_can_be_enabled_on_each_page(
    driver, open_page, page_name, styled_selector, style_property, dark_value
):
    open_page_with_light_theme(driver, open_page, page_name)

    # Проверяет, что страница открылась в светлой теме и кнопка предлагает включить тёмную.
    theme_button = driver.find_element(By.CSS_SELECTOR, ".theme")
    assert "dark-mode" not in driver.find_element(By.TAG_NAME, "body").get_attribute(
        "class"
    )
    assert theme_button.get_attribute("aria-pressed") == "false"
    assert theme_button.get_attribute("aria-label") == "Включить тёмную тему"

    # Включает тёмную тему и проверяет класс, доступные подписи, иконку и цвет элемента.
    theme_button.click()

    body_classes = driver.find_element(By.TAG_NAME, "body").get_attribute("class")
    assert "dark-mode" in body_classes.split()
    assert theme_button.get_attribute("aria-pressed") == "true"
    assert theme_button.get_attribute("aria-label") == "Включить светлую тему"
    assert driver.find_element(By.CSS_SELECTOR, ".theme img").get_attribute(
        "src"
    ).endswith("/img/icon/sun.svg")
    assert driver.execute_script(
        "return getComputedStyle(document.querySelector(arguments[0]))"
        "[arguments[1]]",
        styled_selector,
        style_property,
    ) == dark_value

    # Возвращает светлую тему и проверяет состояние кнопки и исходную иконку.
    theme_button.click()

    body_classes = driver.find_element(By.TAG_NAME, "body").get_attribute("class")
    assert "dark-mode" not in body_classes.split()
    assert theme_button.get_attribute("aria-pressed") == "false"
    assert theme_button.get_attribute("aria-label") == "Включить тёмную тему"
    assert driver.find_element(By.CSS_SELECTOR, ".theme img").get_attribute(
        "src"
    ).endswith("/img/moon.svg")


# Проверяет, что выбор тёмной или светлой темы сохраняется после перезагрузки.
def test_selected_theme_persists_after_reload(driver, open_page):
    open_page_with_light_theme(driver, open_page, "Notes.html")

    # Включает тёмную тему и проверяет её сохранение и применение после перезагрузки.
    driver.find_element(By.CSS_SELECTOR, ".theme").click()
    driver.refresh()

    theme_button = driver.find_element(By.CSS_SELECTOR, ".theme")
    assert "dark-mode" in driver.find_element(
        By.TAG_NAME, "body"
    ).get_attribute("class").split()
    assert theme_button.get_attribute("aria-pressed") == "true"
    assert driver.execute_script(
        "return localStorage.getItem('zametki-theme')"
    ) == "dark"

    # Выбирает светлую тему и проверяет, что это значение также сохраняется после перезагрузки.
    theme_button.click()
    driver.refresh()

    theme_button = driver.find_element(By.CSS_SELECTOR, ".theme")
    assert "dark-mode" not in driver.find_element(
        By.TAG_NAME, "body"
    ).get_attribute("class").split()
    assert theme_button.get_attribute("aria-pressed") == "false"
    assert driver.execute_script(
        "return localStorage.getItem('zametki-theme')"
    ) == "light"


# Открывает страницу тёмной версии и включает тёмную тему перед функциональным тестом.
def open_dark_page(driver, open_page, page_name):
    open_page(f"hex/{page_name}")
    driver.execute_script("localStorage.setItem('zametki-theme', 'dark')")
    driver.refresh()
    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda browser: "dark-mode"
        in browser.find_element(By.TAG_NAME, "body").get_attribute("class").split()
    )


# Ищет элемент на странице и ждёт, пока он появится в DOM.
def find(driver, selector):
    return WebDriverWait(driver, WAIT_SECONDS).until(
        conditions.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


# Ждёт доступности элемента для нажатия и нажимает его.
def click(driver, selector):
    element = WebDriverWait(driver, WAIT_SECONDS).until(
        conditions.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )
    element.click()
    return element


# Ждёт, пока элемент с указанным селектором не будет содержать ожидаемый текст.
def wait_for_text(driver, selector, expected_text):
    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda browser: any(
            element.text == expected_text
            for element in browser.find_elements(By.CSS_SELECTOR, selector)
        )
    )


# Создаёт заметку через тёмный интерфейс так же, как это сделал бы пользователь.
def create_dark_note(driver, title, content=""):
    click(driver, ".new-note")
    find(driver, ".note-title").send_keys(title)
    if content:
        find(driver, ".note-text").send_keys(content)
    click(driver, ".save-note")
    wait_for_text(driver, ".note-card", title)


# Проверяет главную страницу тёмной версии и переход оттуда к форме входа.
def test_dark_landing_page_links_to_login(driver, open_page):
    open_dark_page(driver, open_page, "index.html")

    assert driver.title == "ZAMETKI SUN"
    assert "Ваши заметки" in find(driver, "h1").text
    assert "dark-mode" in find(driver, "body").get_attribute("class").split()

    click(driver, ".brdn")
    WebDriverWait(driver, WAIT_SECONDS).until(
        conditions.url_contains("login.html")
    )
    assert find(driver, ".login-heading h1").text == "Вход в аккаунт"
    assert "dark-mode" in find(driver, "body").get_attribute("class").split()


# Проверяет наличие обязательных полей формы входа в тёмной версии.
def test_dark_login_form_has_required_fields(driver, open_page):
    open_dark_page(driver, open_page, "login.html")

    assert find(driver, "#username").get_attribute("required") == "true"
    assert find(driver, "#password").get_attribute("required") == "true"
    assert driver.execute_script(
        "return document.querySelector('.login-form').checkValidity()"
    ) is False
    assert "dark-mode" in find(driver, "body").get_attribute("class").split()


# Проверяет тексты пустых списков заметок, избранного и корзины в тёмной версии.
def test_dark_empty_notes_sections_show_messages(driver, open_page):
    open_dark_page(driver, open_page, "Notes.html")
    wait_for_text(driver, ".empty-title", "У вас пока нет заметок")

    click(driver, ".favorites-nav")
    wait_for_text(driver, ".empty-title", "В избранном пока нет заметок")

    click(driver, ".trash-nav")
    wait_for_text(driver, ".empty-title", "Корзина пуста")
    assert "dark-mode" in find(driver, "body").get_attribute("class").split()


# Проверяет создание, редактирование и добавление заметки в избранное в тёмной версии.
def test_dark_note_can_be_created_edited_and_favorited(driver, open_page):
    open_dark_page(driver, open_page, "Notes.html")
    create_dark_note(driver, "План на день", "Купить продукты")

    assert driver.execute_script(
        "return document.querySelector('.note-text').value"
    ) == "Купить продукты"

    title = find(driver, ".note-title")
    title.clear()
    title.send_keys("План на неделю")
    click(driver, ".save-note")
    wait_for_text(driver, ".note-card", "План на неделю")

    click(driver, ".favorite-note")
    assert find(driver, ".favorite-note").get_attribute("aria-pressed") == "true"
    click(driver, ".favorites-nav")
    wait_for_text(driver, ".note-card", "План на неделю")


# Проверяет перенос заметки в корзину и её восстановление в тёмной версии.
def test_dark_note_can_be_trashed_and_restored(driver, open_page):
    open_dark_page(driver, open_page, "Notes.html")
    create_dark_note(driver, "Черновик")
    click(driver, ".delete-note")
    click(driver, ".trash-nav")
    wait_for_text(driver, ".note-card", "Черновик")

    click(driver, ".note-card")
    assert find(driver, ".note-title").get_attribute("readonly") == "true"
    click(driver, ".restore-note")

    wait_for_text(driver, ".note-card", "Черновик")
    assert find(driver, ".notes-list-title").text == "Заметки"


# Проверяет окончательное удаление заметки из корзины в тёмной версии.
def test_dark_note_in_trash_can_be_deleted_permanently(driver, open_page):
    open_dark_page(driver, open_page, "Notes.html")
    create_dark_note(driver, "Удалить навсегда")
    click(driver, ".delete-note")
    click(driver, ".trash-nav")
    wait_for_text(driver, ".note-card", "Удалить навсегда")
    click(driver, ".note-card")

    click(driver, ".delete-forever")
    WebDriverWait(driver, WAIT_SECONDS).until(conditions.alert_is_present())
    driver.switch_to.alert.accept()
    wait_for_text(driver, ".empty-title", "Корзина пуста")


# Проверяет, что меню профиля открывается и закрывается кликом снаружи в тёмной версии.
def test_dark_profile_menu_opens_and_closes_on_outside_click(driver, open_page):
    open_dark_page(driver, open_page, "Notes.html")
    wait_for_text(driver, ".empty-title", "У вас пока нет заметок")

    click(driver, ".profile-more")
    assert find(driver, ".profile-menu").is_displayed()
    assert find(driver, ".profile-more").get_attribute("aria-expanded") == "true"

    click(driver, ".empty-title")
    WebDriverWait(driver, WAIT_SECONDS).until(
        conditions.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".profile-menu")
        )
    )
    assert find(driver, ".profile-more").get_attribute("aria-expanded") == "false"


# Проверяет сворачивание и повторное раскрытие боковой панели в тёмной версии.
def test_dark_sidebar_can_be_collapsed_and_expanded(driver, open_page):
    open_dark_page(driver, open_page, "Notes.html")
    click(driver, ".sidebar-toggle")

    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda browser: "is-collapsed"
        in find(browser, ".notes-app").get_attribute("class").split()
    )
    assert find(driver, ".sidebar-toggle").get_attribute("aria-expanded") == "false"

    click(driver, ".sidebar-toggle")
    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda browser: "is-collapsed"
        not in find(browser, ".notes-app").get_attribute("class").split()
    )
    assert find(driver, ".sidebar-toggle").get_attribute("aria-expanded") == "true"


# Проверяет открытие редактора заметки и отсутствие горизонтальной прокрутки на телефоне.
def test_dark_notes_editor_fits_mobile_viewport(driver, open_page):
    open_dark_page(driver, open_page, "Notes.html")
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": 390,
            "height": 844,
            "deviceScaleFactor": 1,
            "mobile": True,
        },
    )
    click(driver, ".empty-state .new-note")
    find(driver, ".note-title").send_keys("Мобильная заметка")
    find(driver, ".note-text").send_keys("Проверка редактора")

    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda browser: "mobile-editor-open"
        in find(browser, ".notes-app").get_attribute("class").split()
    )
    assert find(driver, ".note-editor").is_displayed()

    widths = driver.execute_script(
        "return {page: document.documentElement.scrollWidth, "
        "viewport: document.documentElement.clientWidth}"
    )
    assert widths["page"] <= widths["viewport"], (
        f"Ширина страницы {widths['page']}px превышает экран "
        f"{widths['viewport']}px"
    )
    driver.execute_cdp_cmd(
        "Emulation.clearDeviceMetricsOverride",
        {},
    )
