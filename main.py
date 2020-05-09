import os
import pygame
import requests
import argparse
from io import BytesIO
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('path', type=str)
parser.add_argument('--spn', type=str, default='0.002')
arguments = parser.parse_args().__dict__
map_types = ['sat', 'map', 'sat,skl']
index = 0

toponym_to_find = arguments['path']
delta = arguments['spn']
map_api_server = "http://static-maps.yandex.ru/1.x/"
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    raise Exception

json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
toponym_coodrinates = toponym["Point"]["pos"]
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

map_params = {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "spn": ",".join([delta, delta]),
    "l": "map",
    'scale': '1.0'
}

response = requests.get(map_api_server, params=map_params)
map_file = "map.png"
with open(map_file, "wb") as file:

    file.write(response.content)

pygame.init()
screen = pygame.display.set_mode((600, 450))
screen.blit(pygame.image.load(map_file), (0, 0))
pygame.display.flip()
FPS = 5
clock = pygame.time.Clock()


def update_screen(params):
    global response, screen, map_file
    os.remove(map_file)
    if float(params['scale']) < 1.0:
        params['scale'] = '1.0'
    elif float(params['scale']) >= 4.0:
        params['scale'] = '4.0'
    response = requests.get(map_api_server, params=params)


    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)

    screen.blit(pygame.image.load(map_file), (0, 0))
    pygame.display.flip()


while pygame.event.wait().type != pygame.QUIT:
    try:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_PAGEUP]:
            screen.fill((0, 0, 0))
            delta = map_params['spn'].split(',')[0]
            map_params['scale'] = str(float(map_params['scale']) + 0.1)
            update_screen(map_params)
        elif keys[pygame.K_PAGEDOWN]:
            delta = map_params['spn'].split(',')[0]
            map_params['scale'] = str(float(map_params['scale']) - 0.1)
            update_screen(map_params)
        if keys[pygame.K_LEFT]:
            long = float(map_params['ll'].split(',')[0])
            long -= 0.0001
            map_params['ll'] = f'{long},{map_params["ll"].split(",")[1]}'
            update_screen(map_params)
        elif keys[pygame.K_RIGHT]:
            long = float(map_params['ll'].split(',')[0])
            long += 0.0001
            map_params['ll'] = f'{long},{map_params["ll"].split(",")[1]}'
            update_screen(map_params)
        if keys[pygame.K_UP]:
            lat = float(map_params['ll'].split(',')[1])
            lat += 0.0001
            map_params['ll'] = f'{map_params["ll"].split(",")[0]},{lat}'
            update_screen(map_params)
        elif keys[pygame.K_DOWN]:
            lat = float(map_params['ll'].split(',')[1])
            lat -= 0.0001
            map_params['ll'] = f'{map_params["ll"].split(",")[0]},{lat}'
            update_screen(map_params)

        elif keys[pygame.K_HOME]:
            index += 1
            map_params['l'] = map_types[index % 3]
            update_screen(map_params)

    except pygame.error as exc:
        print(exc)
        break

pygame.quit()
os.remove(map_file)
