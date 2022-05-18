from bs4 import BeautifulSoup
import requests
import json
import os

def getBusTimingsA():
    url = 'https://www.sbstransit.com.sg/service/sbs-transit-app?BusStopNo=67201&ServiceNo='
    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html.parser')
    app = soup.find('div', {'class': 'sbs-mobile-app'})
    busStops = app.find_all('tr')[1:]

    headings = [
        'Service Number', 'Next Bus', 'Subsequent Bus'
    ]

    def getTimings(row):
        info = row.find_all('td')
        return {
            heading: (_.find('span').text if _.find('span') else _.text)
            for heading, _ in zip(headings,info)
        }

    for busStop in busStops:    
        print(getTimings(busStop))

def getBusTimingsB():
    url = 'https://www.nextbuses.sg/api.php?stop=67201'
    data = requests.get(url).json()
    return data

# _ = getBusTimingsA()
# _ = getBusTimingsB()

def extractAllBusStops():
    url = 'https://www.sbstransit.com.sg/service/sbs-transit-app?BusStopNo=67201&ServiceNo='
    keys = ['busStopNo', 'busStopName']
    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html.parser')
    _ = soup.find('select', {'id': 'BusStopNo'})
    busStopsStr = [i.text for i in _.find_all('option') if i.get('value')]
    busStopsStr = [dict(zip(keys, i.split(' - '))) for i in busStopsStr]
    return busStopsStr

def oneMapApi(busStopNo):
    url = f'https://developers.onemap.sg/commonapi/elastic/omsearch?searchVal={busStopNo}%20(&returnGeom=Y&getAddrDetails=Y'
    response = requests.get(url)
    if response.ok:
        results = response.json()['results']
        for result in results:
            if 'BUS STOP' in result['SEARCHVAL']:
                return result['LATITUDE'], result['LONGITUDE']
        return 'Not found.'
    else:
        raise Exception('Failed to use OneMap API...')

def saveJson(JSON):
    with open('busStops.json', 'w') as file:
        json.dump(JSON, file, indent=4)
    print('Saved to busStops.json..')

if os.path.exists('busStops.json'):
    with open('busStops.json') as file:
        data = json.load(file)
else:
    data = extractAllBusStops()

for busStop in data:
    if 'latitude' in busStop.keys():
        # print(f'Value exists for {busStop["busStopNo"]}')
        continue
    try:
        latitude, longitude = oneMapApi(busStop["busStopNo"])
    except:
        print(f'Skipping for {busStop["busStopNo"]}')
        continue
    print(f'Bus stop no. {busStop["busStopNo"]}: {latitude}, {longitude}')
    busStop['latitude'] = latitude
    busStop['longitude'] = longitude

saveJson(data)