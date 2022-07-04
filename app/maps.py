import requests
import yaml
import os

if os.path.exists('secrets.yaml'):
    with open('secrets.yaml', 'r') as file:
        yamlData = yaml.safe_load(file)
    latitude, longitude = yamlData['home1'].values()

url = 'https://developers.onemap.sg/commonapi/staticmap/getStaticImage'
params = {
    'layerchosen': 'original',
    'lat': latitude,
    'lng': longitude,
    'zoom': '17',
    'width': '512',
    'height': '512'
}

response = requests.get(url=url, params=params)

if 1:
    with open('map.png', 'wb') as file:
        file.write(response.content)
else:
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