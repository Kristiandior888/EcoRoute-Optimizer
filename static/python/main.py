import requests  # Для запросов к API карт (используем OpenStreetMap Nominatim для геокодирования)
import math  # Для простых расчётов


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