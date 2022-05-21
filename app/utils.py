from cryptography.fernet import Fernet
from datetime import datetime
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
    return round(earthDiameter * numpy.arcsin( numpy.sqrt( numpy.sin((latitude_2 - latitude_1) / 2) ** 2 + \
        numpy.cos(latitude_1) * numpy.cos(latitude_2) * numpy.sin((longitude_2 - longitude_1) / 2) ** 2 ) ), 3)

def loadBusStops(currLoc=None):
    with open('busStops.json') as file:
        data = json.load(file)
    if currLoc:
        for busStop in data:
            if 'latitude' in busStop.keys():
                busLoc = map(float, (busStop['latitude'], busStop['longitude']))
                busStop['distance'] = getHaversineDistance(*busLoc, *currLoc)
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

def getFormattedMessage(busStops):
    def formatNumber(num):
        if num == 0:
            return 'Arriving'
        elif num == 1:
            return f'{num} min'
        else:
            return f'{num} mins'

    s = '<b>Bus Timings:</b>\n'
    for busInfo in busStops:
        number, street, _, _, distance = busInfo.values()
        buses = getBusTimingsB(number)['buses']
        s += f'{street}\n({number}): {distance} km\n'
        for k,v in buses.items():
            s += f'{k:>3}: Now - {formatNumber(v[0]):>8}, Next - {formatNumber(v[1])}\n'
        s += '\n'
    s += f'<i>Updated on: {datetime.now().strftime("%b %d, %Y %-I:%M %p")}</i>'
    return s

from extract import getBusTimingsA, getBusTimingsB
if __name__ == '__main__':
    # Constants
    setRadius = 0.4 # 0.8 # (km)
    busLimit = 5

    currLoc = getCurrLoc()
    busStops = [i for i in loadBusStops(currLoc) if 'latitude' in i.keys() and getHaversineDistance(*currLoc, i['latitude'], i['longitude']) <= setRadius]
    
    print(getFormattedMessage(sorted(busStops, key=lambda x: x['distance'])[:busLimit]))