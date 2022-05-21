from cryptography.fernet import Fernet
import numpy
import json
import os

def getToken():
    key = bytes(os.getenv("KEY"), "utf-8")
    encrypted = bytes(os.getenv("SECRET_TELEGRAM"), "utf-8")
    return Fernet(key).decrypt(encrypted).decode()

def getHaversineDistance(latitude_1, longitude_1, latitude_2, longitude_2):
    latitude_1, longitude_1, latitude_2, longitude_2 = map(numpy.radians, [latitude_1, longitude_1, latitude_2, longitude_2])
    earthDiameter = 2 * 6371.0088 # 6372.8
    return earthDiameter * numpy.arcsin( numpy.sqrt( numpy.sin((latitude_2 - latitude_1) / 2) ** 2 + \
        numpy.cos(latitude_1) * numpy.cos(latitude_2) * numpy.sin((longitude_2 - longitude_1) / 2) ** 2 ) )

def loadBusStops():
    with open('busStops.json') as file:
        data = json.load(file)
    return data

from typing import List
import yaml
def getCurrLoc(*args):
    if os.path.exists('secrets.yaml'):
        with open('secrets.yaml', 'r') as file:
            yamlData = yaml.safe_load(file)
        return yamlData['home']['latitude'], yamlData['home']['longitude']
    else:
        if len(args) == 1 and isinstance(args[0], List) and len(args[0]) == 2:
            return tuple(args[0])
        elif len(args) == 2:
            return args
        else:
            try:
                latitude, longitude = map(float, input('Enter latitude and longitude, separated by comma: ').split(','))
                return latitude, longitude
            except:
                print('Input error...')
                return

if __name__ == '__main__':
    setRadius = 0.8 # (km)
    currLoc = getCurrLoc()
    busStops = [i for i in loadBusStops() if 'latitude' in i.keys() and getHaversineDistance(*currLoc, i['latitude'], i['longitude']) <= setRadius]
    for busStop in busStops:
        number = busStop['busStopNo']
        street = busStop['busStopName']
        busLoc = map(float, (busStop['latitude'], busStop['longitude']))
        distance = getHaversineDistance(*currLoc, *busLoc)
        print(f'{street} ({number}): {distance} km')
        # break
