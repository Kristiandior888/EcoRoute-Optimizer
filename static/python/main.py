import requests  # Для запросов к API карт (используем OpenStreetMap Nominatim для геокодирования)
import math  # Для простых расчётов

from bs4 import BeautifulSoup


# Функция для геокодирования (преобразование адреса в координаты)
def geocode(location):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    response = requests.get(url, headers={'User-Agent': 'EcoRouteOptimizer/1.0'})
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    return None, None


# Простая функция для расчёта расстояния (Haversine formula)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Радиус Земли в км
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# Простая оптимизация: Рекомендуемая скорость для минимизации топлива (гипотетическая формула)
def recommend_speed(distance, vehicle_type):
    # Для грузовика: оптимальная скорость ~80 км/ч
    if vehicle_type == 'truck':
        return 80, distance / 80 * 10  # Время в часах, расход 10 л/100км
    elif vehicle_type == 'bus':
        return 60, distance / 60 * 8
    else:
        return 90, distance / 90 * 7


# Функция для получения и парсинга цены
def get_fuel_price(fuel_class, soup: BeautifulSoup):
    fuel_card = soup.find('div', class_=fuel_class)
    if fuel_card:
        price_span = fuel_card.find('span', itemprop='price')
        if price_span:
            return float(price_span.get_text(strip=True).replace('₽', ''))
    return None  # Если цена не найдена


# Основная функция
def get_gas_prices(vehicle_type):

    url = "https://fuelprices.ru/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    price = None

    if vehicle_type == "Легковой":

        # Получаем цены для АИ-92, АИ-95, АИ-98
        gas_92_price = get_fuel_price('fuel-card border-ai80', soup)
        gas_95_price = get_fuel_price('fuel-card border-ai92', soup)
        gas_98_price = get_fuel_price('fuel-card border-ai95', soup)

        if None not in [gas_92_price, gas_95_price, gas_98_price]:
            # Вычисляем среднюю цену
            price = (gas_92_price + gas_95_price + gas_98_price) / 3

        else:
            price = None

    else:
        # Получаем цену дизельного топлива
        price = get_fuel_price('fuel-card border-diesel', soup)

    return price

