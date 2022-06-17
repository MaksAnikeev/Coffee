import json
import os

import folium
import requests
from dotenv import load_dotenv
from flask import Flask
from geopy import distance


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_cafe_distance(cafe):
    return cafe['distance']


def create_nearest_cafes(place, file_name='cafes_map'):
    with open('coffee.json', 'r', encoding='CP1251') as file:
        file_contents = file.read()
    cafes_file = json.loads(file_contents)
    load_dotenv()
    apikey = os.environ['MAPS_YANDEX_APIKEY']
    place_cords = fetch_coordinates(apikey, place)
    place_cords_for_geo = (place_cords[1], place_cords[0])
    cafes = []
    for i in range(len(cafes_file)):
        cafe_cords = (cafes_file[i]['geoData']['coordinates'][1], cafes_file[i]['geoData']['coordinates'][0])
        cafe = {}
        cafe['title'] = cafes_file[i]['Name']
        cafe['distance'] = distance.distance(place_cords_for_geo, cafe_cords).km
        cafe['latitude'] = cafes_file[i]['geoData']['coordinates'][1]
        cafe['longitude'] = cafes_file[i]['geoData']['coordinates'][0]
        cafes.append(cafe)

    sorted_cafes = sorted(cafes, key=get_cafe_distance)
    nearest_cafes = sorted_cafes[0:5]
    cafes_map = folium.Map(location=[place_cords[1], place_cords[0]], zoom_start=12, tiles="Stamen Terrain")

    for i in range(len(nearest_cafes)):
        folium.Marker([nearest_cafes[i]['latitude'], nearest_cafes[i]['longitude']],
                      popup="<i>Mt. Hood Meadows</i>", tooltip=nearest_cafes[i]['title']).add_to(cafes_map)
    folium.Marker(
        location=[place_cords[1], place_cords[0]],
        popup='Я здесь!',
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(cafes_map)

    cafes_map.save(f"{file_name}.html")


def show_cafes():
    with open('cafes_map.html') as file:
        return file.read()


if __name__ == '__main__':
    place = input('Где вы находитесь: ')
    create_nearest_cafes(place)
    cafe_app = Flask(__name__)
    cafe_app.add_url_rule('/', 'Caffee', show_cafes)
    cafe_app.run('0.0.0.0')
