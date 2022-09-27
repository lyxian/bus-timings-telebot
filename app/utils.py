from cryptography.fernet import Fernet
import requests
import pendulum
import numpy
import json
import os

def retrieveKey():
    required = ['APP_NAME', 'APP_PASS', 'STORE_PASS', 'STORE_URL']
    if all(param in os.environ for param in required):
        payload = {
            'url': '{}/{}'.format(os.getenv('STORE_URL'), 'getPass'),
            'payload': {
                'password': int(os.getenv('STORE_PASS')),
                'app': os.getenv('APP_NAME'),
                'key': int(os.getenv('APP_PASS'))
            }
        }
        response = requests.post(payload['url'], json=payload['payload']).json()
        if response.get('status') == 'OK':
            key = response.get('KEY')
            os.environ['KEY'] = key
            return key
        else:
            raise Exception('Bad response from KEY_STORE, please try again ..')
    else:
        raise Exception('No key store found, please check config ..')

def postError(error):
    required = ['APP_NAME', 'APP_PASS', 'STORE_PASS', 'STORE_URL']
    if all(param in os.environ for param in required):
        payload = {
            'url': '{}/{}'.format(os.getenv('STORE_URL'), 'postError'),
            'payload': {
                'password': int(os.getenv('STORE_PASS')),
                'app': os.getenv('APP_NAME'),
                'key': int(os.getenv('APP_PASS')),
                'error': error,
            }
        }
        response = requests.post(payload['url'], json=payload['payload']).json()
        if response.get('status') == 'OK':
            return response
        else:
            raise Exception('Bad response from KEY_STORE, please try again ..')
    else:
        raise Exception('No key store found, please check config ..')

def getToken():
    key = bytes(retrieveKey(), 'utf-8')
    encrypted = bytes(os.getenv('SECRET_TELEGRAM'), 'utf-8')
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
    if not args and os.path.exists('secrets.yaml'):
        with open('secrets.yaml', 'r') as file:
            yamlData = yaml.safe_load(file)
        return yamlData['home1']['latitude'], yamlData['home1']['longitude']
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

def getFormattedMessage(busStops, radius):
    def formatNumber(num):
        if num is None:
            return 'No Bus'
        else:
            if num == 0:
                return 'Coming'
            elif num == 1:
                return f'{num} min'
            else:
                return f'{num} mins'

    s = f'<b>Bus Timings <i>({len(busStops)} nearby within {radius} km)</i>:</b>\n'
    for i, busInfo in enumerate(busStops):
        number, street, _, _, distance = busInfo.values()
        buses = getBusTimingsB(number)['buses']
        letter = chr(ord("A")+len(busStops)-i-1)
        s += f'{letter}: {street}\n({number}): {distance} km\n'
        if buses:
            for k,v in buses.items():
                s += f'{k:>3}: Now - {formatNumber(v[0]):>7}, Next - {formatNumber(v[1]):>7}\n'
        else:
            s += '<i>No available buses</i>\n'
        s += '\n'
    currentTime = ', '.join(pendulum.now('Asia/Singapore').to_day_datetime_string().split(', ')[1:])
    s += f'<i>Updated on: {currentTime}</i>'
    return s

import requests
REQUEST_TIMEOUT = 25
def generateMap(currLoc, busStops, urlOnly=False):
    latitude, longitude = currLoc

    pointsString = [f'[{latitude},{longitude},"255,255,255"]']
    for i in range(len(busStops)):
        letter = chr(ord("A")+len(busStops)-i-1)
        pointsString += [f'[{busStops[i]["latitude"]},{busStops[i]["longitude"]},"0,0,0","{letter}"]']
    pointsString = '|'.join(pointsString)

    url = 'https://developers.onemap.sg/commonapi/staticmap/getStaticImage'

    params = {
        'layerchosen': 'original',
        'lat': latitude,
        'lng': longitude,
        'zoom': '17',
        'width': '500',
        'height': '500',
        'points': pointsString
    }
    if urlOnly:
        return url + '?' + '&'.join([f'{k}={v}' for k,v in params.items()])
    else:
        print(url + '?' + '&'.join([f'{k}={v}' for k,v in params.items()]))
        try:
            response = requests.get(url=url, params=params, timeout=REQUEST_TIMEOUT)
        except:
            print('Using layer=default..')
            response = ''
        if response and response.ok:
            imagePath = 'map.png'
            if os.path.exists(imagePath):
                os.remove(imagePath)
                print(f'Removed {imagePath}')
            with open(imagePath, 'wb') as file:
                file.write(response.content)
            print(f'Map successfully saved as {imagePath}')
        else:
            # Change map layer
            params['layerchosen'] = 'default'
            response = requests.get(url=url, params=params, timeout=REQUEST_TIMEOUT)
            if response.ok:
                imagePath = 'map.png'
                if os.path.exists(imagePath):
                    os.remove(imagePath)
                    print(f'Removed {imagePath}')
                with open(imagePath, 'wb') as file:
                    file.write(response.content)
                print(f'Map successfully saved as {imagePath}')
            else:
                raise Exception('Bad request: Error in parameters')
        return imagePath

def removeMapFile(imagePath):
    if os.path.exists(imagePath):
        os.remove(imagePath)
        print(f'Removed {imagePath}')
    return

def loadConfig():
    if os.path.exists('secrets.yaml'):
        with open('secrets.yaml', 'r') as file:
            yamlData = yaml.safe_load(file)
        return yamlData
    else:
        return None

from extract import getBusTimingsA, getBusTimingsB
if __name__ == '__main__':
    # Constants
    setRadius = 0.3 # 0.8 # (km)
    busLimit = 100

    currLoc = getCurrLoc()
    busStops = sorted([i for i in loadBusStops(currLoc) if 'latitude' in i.keys() and getHaversineDistance(*currLoc, i['latitude'], i['longitude']) <= setRadius], key=lambda x: x['distance'])[:busLimit]
    
    if 0:
        print(getFormattedMessage(busStops[:busLimit], setRadius))
    else:
        imagePath = generateMap(currLoc, busStops)
        # imagePath = generateMap(currLoc, busStops, urlOnly=True)
        print(imagePath)