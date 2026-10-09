import pytest

from playwright.sync_api import sync_playwright



@pytest.fixture()
def page():
    """
    Открывает главную страницу приложения в Firefox.

    Yields:
        Страница Playwright с загруженным http://localhost:5000.
    """
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        context = browser.new_context()
        curr_page = context.new_page()
        curr_page.goto("http://localhost:5000")
        yield curr_page

@pytest.fixture()
def filled_form(page):
    """
    Заполняет форму маршрута и отправляет её.

    Вводит города Курган и Москва, габариты 1.8 x 1.5, тип транспорта
    "Легковое авто" и нажимает кнопку "Оптимизировать маршрут".

    Returns:
        Страница Playwright после отправки формы.
    """
    page.locator('input[name="start"]').fill("Курган")
    page.locator('input[name="end"]').fill("Москва")
    page.locator('input[name="width"]').fill("1.8")
    page.locator('input[name="height"]').fill("1.5")
    page.locator('select[name="vehicle_type"]').select_option("Легковое авто")
    page.get_by_role("button", name="Оптимизировать маршрут").click()
    return page

@pytest.fixture()
def results(filled_form):
    """
    Собирает локаторы элементов страницы с результатами расчёта.

    Returns:
        Словарь локаторов: расстояние, рекомендуемая скорость, расход топлива,
        цена топлива и кнопка возврата.
    """
    page = filled_form

    page.wait_for_load_state("networkidle")
    return {
        "distance": page.locator("p.stat-label:has-text('Расстояние')").locator("..").locator("p.stat-value"),
        "speed": page.locator("p.stat-label:has-text('Рекомендуемая скорость')").locator("..").locator("p.stat-value"),
        "fuel_spend": page.locator("p.stat-label:has-text('Расход топлива')").locator("..").locator("p.stat-value"),
        "fuel_price": page.locator("p.stat-label:has-text('Цена топлива')").locator("..").locator("p.stat-value"),
        "back_btn": page.locator("a.btn-back"),
    }


def test_ui(results):
    """
    Проверяет, что после отправки формы на странице видны все элементы результата.

    Args:
        results: словарь локаторов элементов страницы с результатами.
    """
    for elem in results.values():
        assert elem.is_visible()