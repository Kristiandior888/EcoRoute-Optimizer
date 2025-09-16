# EcoRoute Optimizer - Простой веб-сайт на Flask для оптимизации маршрутов
# Требования: Установите Flask (pip install flask), requests для API, folium для карт (pip install folium)
# Запуск: python app.py, затем откройте http://127.0.0.1:5000/

from flask import Flask, render_template, request, jsonify
import folium  # Для генерации интерактивных карт
import requests  # Для запросов к API карт (используем OpenStreetMap Nominatim для геокодирования)
import math  # Для простых расчётов

app = Flask(__name__)


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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start = request.form['start']
        end = request.form['end']
        width = float(request.form['width'])
        height = float(request.form['height'])
        vehicle_type = request.form['vehicle_type']

        # Геокодирование
        start_lat, start_lon = geocode(start)
        end_lat, end_lon = geocode(end)

        if start_lat is None or end_lat is None:
            return render_template('index.html', error="Не удалось найти場所")

        # Расчёт расстояния
        distance = haversine(start_lat, start_lon, end_lat, end_lon)

        # Проверка габаритов (упрощённо: если ширина > 3м или высота > 4м, предупредить)
        size_warning = ""
        if width > 3 or height > 4:
            size_warning = "Внимание: Габариты могут не пройти под мостами или в туннелях!"

        # Рекомендация скорости и расхода
        speed, fuel = recommend_speed(distance, vehicle_type)

        # Генерация карты с маршрутом (простая линия)
        m = folium.Map(location=[start_lat, start_lon], zoom_start=6)
        folium.Marker([start_lat, start_lon], popup=start).add_to(m)
        folium.Marker([end_lat, end_lon], popup=end).add_to(m)
        folium.PolyLine([[start_lat, start_lon], [end_lat, end_lon]], color="blue").add_to(m)

        map_html = m._repr_html_()

        return render_template('result.html', distance=round(distance, 2), speed=speed, fuel=round(fuel, 2),
                               size_warning=size_warning, map_html=map_html)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)