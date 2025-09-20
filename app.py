from flask import Flask, render_template, request
import folium
from static.python.main import geocode, recommend_speed
from static.python.osrm import get_route_osrm
from static.python.driver_schedule import plan_driver_schedule
import requests

app = Flask(__name__)

def get_fuel_stations(lat_min, lon_min, lat_max, lon_max, limit=20):
    """Получаем АЗС через Overpass API"""
    query = f"""
    [out:json];
    node["amenity"="fuel"]({lat_min},{lon_min},{lat_max},{lon_max});
    out;
    """
    url = "http://overpass-api.de/api/interpreter"
    response = requests.post(url, data=query)
    stations = []
    if response.status_code == 200:
        data = response.json()
        for element in data.get("elements", [])[:limit]:
            stations.append((
                element["lat"], 
                element["lon"], 
                element.get("tags", {}).get("name", "АЗС")
            ))
    return stations

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start = request.form['start']
        end = request.form['end']
        width = float(request.form['width'])
        height = float(request.form['height'])
        vehicle_type = request.form['vehicle_type']

        start_lat, start_lon = geocode(start)
        end_lat, end_lon = geocode(end)
        if start_lat is None or end_lat is None:
            return render_template('index.html', error="Не удалось найти адреса")

        # Маршрут OSRM
        distance, duration, geometry = get_route_osrm(start_lat, start_lon, end_lat, end_lon)
        if distance is None:
            return render_template('index.html', error="Не удалось построить маршрут")

        # Проверка габаритов
        size_warning = ""
        if width > 3 or height > 4:
            size_warning = "Внимание: Габариты могут не пройти под мостами или в туннелях!"

        # Скорость и расход
        speed, fuel = recommend_speed(distance, vehicle_type)

        # Планируем перерывы и ночёвки
        schedule = plan_driver_schedule(distance, speed)

        # Карта
        m = folium.Map(location=[start_lat, start_lon], zoom_start=6)
        folium.Marker([start_lat, start_lon], popup=start).add_to(m)
        folium.Marker([end_lat, end_lon], popup=end).add_to(m)
        folium.GeoJson(geometry, name="Маршрут").add_to(m)

        coords = geometry["coordinates"]
        segment_count = len(schedule)
        step = max(1, len(coords)//segment_count)

        # Добавляем перерывы и ночёвки по маршруту
        for i, item in enumerate(schedule):
            if item["action"] in ["break", "overnight_rest"]:
                idx = min(i*step, len(coords)-1)
                lon, lat = coords[idx]
                folium.Marker(
                    [lat, lon],
                    tooltip=f"{item['action'].replace('_',' ').title()} ({item['duration']})",
                    icon=folium.Icon(color="red" if item["action"]=="break" else "green")
                ).add_to(m)

        # Получаем границы маршрута для поиска АЗС
        lats = [lat for lon, lat in coords]
        lons = [lon for lon, lat in coords]
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)

        # Получаем и отображаем АЗС
        fuel_stations = get_fuel_stations(lat_min, lon_min, lat_max, lon_max)
        for lat, lon, name in fuel_stations:
            folium.Marker(
                [lat, lon],
                tooltip=name,
                icon=folium.Icon(color="blue", icon="tint", prefix="fa")
            ).add_to(m)

        map_html = m._repr_html_()

        return render_template(
            'result.html',
            distance=round(distance,2),
            speed=speed,
            fuel=round(fuel,2),
            size_warning=size_warning,
            map_html=map_html,
            schedule=schedule
        )

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
