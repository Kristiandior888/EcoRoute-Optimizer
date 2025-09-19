# EcoRoute Optimizer - Простой веб-сайт на Flask для оптимизации маршрутов
# Требования: Установите Flask (pip install flask), requests для API, folium для карт (pip install folium)
# Запуск: python app.py, затем откройте http://127.0.0.1:5000/
import folium  # Для генерации интерактивных карт

from flask import Flask, render_template, request, jsonify
from static.python.main import haversine, geocode, recommend_speed, get_gas_prices

app = Flask(__name__)


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

        # Цена за топливо
        gas_price = get_gas_prices(vehicle_type, fuel)

        # Генерация карты с маршрутом (простая линия)
        m = folium.Map(location=[start_lat, start_lon], zoom_start=6)
        folium.Marker([start_lat, start_lon], popup=start).add_to(m)
        folium.Marker([end_lat, end_lon], popup=end).add_to(m)
        folium.PolyLine([[start_lat, start_lon], [end_lat, end_lon]], color="blue").add_to(m)

        map_html = m._repr_html_()

        return render_template('result.html', distance=round(distance, 2), speed=speed, fuel=round(fuel, 2),
                               size_warning=size_warning, map_html=map_html, gas_price = gas_price)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)