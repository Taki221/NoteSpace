from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait


# Максимальное время ожидания элемента или изменения страницы.
WAIT_SECONDS = 5


# Ищет элемент по CSS-селектору и ждёт, пока он появится в HTML.
def find(driver, selector):
    return WebDriverWait(driver, WAIT_SECONDS).until(
        conditions.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


# Ждёт, пока элемент станет доступен для нажатия, затем нажимает его.
def click(driver, selector):
    element = WebDriverWait(driver, WAIT_SECONDS).until(
        conditions.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )
    element.click()
    return element


# Ждёт, пока среди элементов появится текст, совпадающий с ожидаемым.
def wait_for_text(driver, selector, expected_text):
    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda browser: any(
            element.text == expected_text
            for element in browser.find_elements(By.CSS_SELECTOR, selector)
        )
    )


# Создаёт заметку через интерфейс так же, как это сделал бы пользователь.
def create_note(driver, title, content=""):
    click(driver, ".new-note")
    find(driver, ".note-title").send_keys(title)
    if content:
        find(driver, ".note-text").send_keys(content)
    click(driver, ".save-note")
    wait_for_text(driver, ".note-card", title)


def test_landing_page_links_to_login(driver, open_page):
    # Проверяет главную страницу и переход по кнопке «Войти».
    open_page("index.html")

    assert driver.title == "ZAMETKI SUN"
    assert "Ваши заметки" in find(driver, "h1").text

    click(driver, ".brdn")
    WebDriverWait(driver, WAIT_SECONDS).until(
        conditions.url_contains("login.html")
    )
    assert find(driver, ".login-heading h1").text == "Вход в аккаунт"


def test_login_form_has_required_fields(driver, open_page):
    # Проверяет наличие полей логина и пароля и их обязательность.
    open_page("login.html")

    assert find(driver, "#username").get_attribute("required") == "true"
    assert find(driver, "#password").get_attribute("required") == "true"
    assert driver.execute_script(
        "return document.querySelector('.login-form').checkValidity()"
    ) is False


def test_empty_notes_sections_show_messages(driver, open_page):
    # Проверяет пустые состояния списка заметок, избранного и корзины.
    open_page("Notes.html")
    wait_for_text(driver, ".empty-title", "У вас пока нет заметок")

    click(driver, ".favorites-nav")
    wait_for_text(driver, ".empty-title", "В избранном пока нет заметок")

    click(driver, ".trash-nav")
    wait_for_text(driver, ".empty-title", "Корзина пуста")


def test_note_can_be_created_edited_and_favorited(driver, open_page):
    # Проверяет создание, редактирование заметки и добавление в избранное.
    open_page("Notes.html")
    create_note(driver, "План на день", "Купить продукты")

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


def test_note_can_be_trashed_and_restored(driver, open_page):
    # Проверяет перенос заметки в корзину и её последующее восстановление.
    open_page("Notes.html")
    create_note(driver, "Черновик")
    click(driver, ".delete-note")
    click(driver, ".trash-nav")
    wait_for_text(driver, ".note-card", "Черновик")

    click(driver, ".note-card")
    assert find(driver, ".note-title").get_attribute("readonly") == "true"
    click(driver, ".restore-note")

    wait_for_text(driver, ".note-card", "Черновик")
    assert find(driver, ".notes-list-title").text == "Заметки"


def test_note_in_trash_can_be_deleted_permanently(driver, open_page):
    # Проверяет окончательное удаление заметки из корзины.
    open_page("Notes.html")
    create_note(driver, "Удалить навсегда")
    click(driver, ".delete-note")
    click(driver, ".trash-nav")
    wait_for_text(driver, ".note-card", "Удалить навсегда")
    click(driver, ".note-card")

    click(driver, ".delete-forever")
    WebDriverWait(driver, WAIT_SECONDS).until(conditions.alert_is_present())
    driver.switch_to.alert.accept()
    wait_for_text(driver, ".empty-title", "Корзина пуста")


def test_profile_menu_opens_and_closes_on_outside_click(driver, open_page):
    # Проверяет открытие меню профиля и закрытие кликом вне меню.
    open_page("Notes.html")
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


def test_sidebar_can_be_collapsed_and_expanded(driver, open_page):
    # Проверяет сворачивание и повторное раскрытие боковой панели.
    open_page("Notes.html")
    click(driver, ".sidebar-toggle")

    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda browser: "is-collapsed"
        in find(browser, ".notes-app").get_attribute("class")
    )
    assert find(driver, ".sidebar-toggle").get_attribute("aria-expanded") == "false"

    click(driver, ".sidebar-toggle")
    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda browser: "is-collapsed"
        not in find(browser, ".notes-app").get_attribute("class")
    )
    assert find(driver, ".sidebar-toggle").get_attribute("aria-expanded") == "true"


def test_theme_button_changes_page_background(driver, open_page):
    # Проверяет, что кнопка темы меняет цвет фона страницы.
    open_page("Notes.html")
    initial_background = driver.execute_script(
        "return getComputedStyle(document.body).backgroundColor"
    )

    click(driver, ".theme")
    changed_background = driver.execute_script(
        "return getComputedStyle(document.body).backgroundColor"
    )

    assert changed_background != initial_background


def test_notes_editor_does_not_overflow_mobile_viewport(driver, open_page):
    # Проверяет отсутствие горизонтальной прокрутки редактора на мобильном экране.
    open_page("Notes.html")
    # Включает мобильный размер экрана через Chrome DevTools Protocol.
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": 390,
            "height": 844,
            "deviceScaleFactor": 1,
            "mobile": True,
        },
    )
    create_note(driver, "Мобильная заметка")

    # Сравнивает ширину страницы с шириной экрана, чтобы поймать прокрутку вбок.
    widths = driver.execute_script(
        "return {page: document.documentElement.scrollWidth, "
        "viewport: document.documentElement.clientWidth}"
    )
    assert widths["page"] <= widths["viewport"], (
        f"Ширина страницы {widths['page']}px превышает экран "
        f"{widths['viewport']}px"
    )
