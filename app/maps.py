import requests
import yaml
import os

from utils import getCurrLoc, loadBusStops, getHaversineDistance

if os.path.exists('secrets.yaml'):
    with open('secrets.yaml', 'r') as file:
        yamlData = yaml.safe_load(file)
    latitude, longitude = yamlData['home1'].values()

setRadius = 0.3 # 0.8 # (km)
busLimit = 100

currLoc = getCurrLoc()
busStops = [i for i in loadBusStops(currLoc) if 'latitude' in i.keys() and getHaversineDistance(*currLoc, i['latitude'], i['longitude']) <= setRadius]

pointsString = [f'[{latitude}, {longitude}, "255,255,255"]']
for i in range(len(busStops)):
    pointsString += [f'[{busStops[i]["latitude"]}, {busStops[i]["longitude"]}, "0,0,0", "{chr(ord("A")+i)}"]']
pointsString = '|'.join(pointsString)
# print(pointsString)

url = 'https://developers.onemap.sg/commonapi/staticmap/getStaticImage'

params = {
    'layerchosen': 'original',
    'lat': latitude,
    'lng': longitude,
    'zoom': '17',
    'width': '512',
    'height': '512',
    'points': pointsString
}

if 1:
    response = requests.get(url=url, params=params)

    if 1:
        if os.path.exists('map.png'):
            os.remove('map.png')
        with open('map.png', 'wb') as file:
            file.write(response.content)
    else:
        if os.path.exists('map.jpg'):
            os.remove('map.jpg')
        with open('map.jpg', 'wb') as file:
            file.write(response.content)

# &layerchosen={Map Layer}
# &lat={Latitude}
# &lng={Longtitude}
# &zoom={Zoom Level}
# &width={Image's Width}
# &height={Image's Height}
# &polygons={Polygons' Details}
# &lines={Lines' Details}
# &points={Points' Details}
# &color={All Lines' Color}
# &fillColor={All Polygons' Color}