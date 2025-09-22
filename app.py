# EcoRoute Optimizer - Объединенная версия (исправленная)
import folium
from flask import Flask, render_template, request
from static.python.main import geocode, recommend_speed, get_gas_prices
from static.python.osrm import get_route_osrm
from static.python.driver_schedule import plan_driver_schedule
import requests
from datetime import timedelta
import math

app = Flask(__name__)


def get_fuel_stations(lat_min, lon_min, lat_max, lon_max, limit=20):
    """Получаем АЗС через Overpass API"""
    query = f"""
    [out:json];
    node["amenity"="fuel"]({lat_min},{lon_min},{lat_max},{lon_max});
    out;
    """
    url = "http://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data=query, timeout=10)
        if response.status_code == 200:
            data = response.json()
            stations = []
            for element in data.get("elements", [])[:limit]:
                stations.append((
                    element["lat"],
                    element["lon"],
                    element.get("tags", {}).get("name", "АЗС")
                ))
            return stations
    except:
        pass
    return []


def format_timedelta(td):
    """Форматируем timedelta в читаемый вид"""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if hours > 0:
        return f"{hours}ч {minutes}м"
    return f"{minutes}м"


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
            return render_template('index.html', error="Не удалось найти адреса")

        # Маршрут OSRM (от Сережи)
        distance, duration, geometry = get_route_osrm(start_lat, start_lon, end_lat, end_lon)

        # Если OSRM не работает, используем расчет по прямой
        if distance is None:
            distance = math.sqrt((end_lat - start_lat) ** 2 + (end_lon - start_lon) ** 2) * 111  # Примерное расстояние
            geometry = {
                "type": "LineString",
                "coordinates": [[start_lon, start_lat], [end_lon, end_lat]]
            }

        # Проверка габаритов (от вас и Дани)
        size_warning = ""
        if width > 3 or height > 4:
            size_warning = "Внимание: Габариты могут не пройти под мостами или в туннелях!"

        # Рекомендация скорости и расхода
        speed, fuel_consumption = recommend_speed(distance, vehicle_type)

        # Расчет цены топлива (от Дани)
        gas_price = get_gas_prices(vehicle_type, fuel_consumption)

        # Планирование графика водителя (от Сережи)
        schedule = plan_driver_schedule(distance, speed)

        # Создание карты
        m = folium.Map(location=[start_lat, start_lon], zoom_start=6)
        folium.Marker([start_lat, start_lon], popup=f"Старт: {start}", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker([end_lat, end_lon], popup=f"Финиш: {end}", icon=folium.Icon(color='red')).add_to(m)

        # Отображение маршрута
        if geometry and "coordinates" in geometry:
            folium.GeoJson(
                geometry,
                name="Маршрут",
                style_function=lambda x: {'color': 'blue', 'weight': 4}
            ).add_to(m)

            coords = geometry["coordinates"]

            # Добавляем АЗС вдоль маршрута
            if coords:
                lats = [lat for lon, lat in coords]
                lons = [lon for lon, lat in coords]
                lat_min, lat_max = min(lats), max(lats)
                lon_min, lon_max = min(lons), max(lons)

                fuel_stations = get_fuel_stations(lat_min - 0.1, lon_min - 0.1, lat_max + 0.1, lon_max + 0.1)
                for lat, lon, name in fuel_stations:
                    folium.Marker(
                        [lat, lon],
                        tooltip=f"АЗС: {name}",
                        popup=f"Заправка: {name}",
                        icon=folium.Icon(color="blue", icon="tint", prefix="fa")
                    ).add_to(m)

            # Добавляем маркеры перерывов и ночевок (исправленная логика)
            breaks_schedule = [item for item in schedule if item["action"] in ["break", "overnight_rest"]]

            if breaks_schedule and coords:
                # Равномерно распределяем маркеры по маршруту
                segment_count = len(breaks_schedule)
                step = max(1, len(coords) // (segment_count + 1))

                for i, item in enumerate(breaks_schedule):
                    # Распределяем маркеры равномерно по маршруту
                    idx = min((i + 1) * step, len(coords) - 1)
                    lon, lat = coords[idx]

                    # Настройки маркера в зависимости от типа
                    if item["action"] == "break":
                        icon_color = "orange"
                        icon_type = "coffee"
                        title = "Перерыв для отдыха"
                    else:
                        icon_color = "darkred"
                        icon_type = "bed"
                        title = "Ночёвка"

                    duration_text = format_timedelta(item["duration"])

                    folium.Marker(
                        [lat, lon],
                        tooltip=f"{title} ({duration_text})",
                        popup=f"{title}\nПродолжительность: {duration_text}",
                        icon=folium.Icon(color=icon_color, icon=icon_type, prefix="fa")
                    ).add_to(m)

        map_html = m._repr_html_()

        # Форматируем расписание для отображения
        formatted_schedule = []
        total_drive_time = timedelta()

        for item in schedule:
            if item["action"] == "drive":
                total_drive_time += item["duration"]
            else:
                formatted_schedule.append({
                    "action": item["action"],
                    "duration": format_timedelta(item["duration"]),
                    "after_driving": format_timedelta(total_drive_time)
                })
                total_drive_time = timedelta()

        return render_template(
            'result.html',
            distance=round(distance, 2),
            speed=round(speed, 1),
            fuel=round(fuel_consumption, 2),
            gas_price=gas_price if gas_price else "Не удалось рассчитать",
            size_warning=size_warning,
            map_html=map_html,
            schedule=formatted_schedule,
            travel_time=round(distance / speed, 1) if speed > 0 else 0
        )

    return render_template('index.html')


@app.route('/health')
def health_check():
    """Проверка работоспособности API"""
    return jsonify({"status": "ok", "message": "EcoRoute Optimizer работает корректно"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)