import requests
import math
from bs4 import BeautifulSoup

# Функция для геокодирования (общая)
def geocode(location):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    response = requests.get(url, headers={'User-Agent': 'EcoRouteOptimizer/1.0'})
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    return None, None

# Функция для расчета расстояния (резервная)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Объединенная функция рекомендации скорости
def recommend_speed(distance, vehicle_type):
    # Используем улучшенную версию (расход на 100 км)
    if vehicle_type == 'truck':
        return 80, distance / 100 * 10  # 10 л/100км
    elif vehicle_type == 'bus':
        return 60, distance / 100 * 8   # 8 л/100км
    else:
        return 90, distance / 100 * 7   # 7 л/100км

# Функция для получения цен на топливо (от Дани)
def get_fuel_price(fuel_class, soup: BeautifulSoup):
    fuel_card = soup.find('div', class_=fuel_class)
    if fuel_card:
        price_span = fuel_card.find('span', itemprop='price')
        if price_span:
            return float(price_span.get_text(strip=True).replace('₽', ''))
    return None

def get_gas_prices(vehicle_type, gas_amount):
    url = "https://fuelprices.ru/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    price = None

    if vehicle_type == "car":
        gas_92_price = get_fuel_price('fuel-card border-ai80', soup)
        gas_95_price = get_fuel_price('fuel-card border-ai92', soup)
        gas_98_price = get_fuel_price('fuel-card border-ai95', soup)

        if None not in [gas_92_price, gas_95_price, gas_98_price]:
            price = (gas_92_price + gas_95_price + gas_98_price) / 3
        else:
            price = 50  # Резервная цена
    else:
        price = get_fuel_price('fuel-card border-diesel', soup)
        if price is None:
            price = 55  # Резервная цена для дизеля

    return round(price * gas_amount)