from bs4 import BeautifulSoup
import requests
import json
import os

# Bus Stop Format :
# - title : <str>
# - buses : 
#    - <bus_1> : <timing_1> , <timing_2>
#    - <bus_2> : <timing_1> , <timing_2>

import time
def trackTime(func):
    def wrapper(*args):
        t1 = time.time()
        rtnVal = func(*args)
        print(f'Time Taken: {time.time() - t1} s')
        return rtnVal
    return wrapper

@trackTime
def getBusTimingsA(busStopNo):
    url = f'https://www.sbstransit.com.sg/service/sbs-transit-app?BusStopNo={busStopNo}&ServiceNo='
    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html.parser')
    app = soup.find('div', {'class': 'sbs-mobile-app'})
    busStops = app.find_all('tr')[1:]

    def getInfo(rows):
        d = {}
        for row in rows:
            busNo, nextBus, subsequentBus = map(lambda x: x.text.split()[0], row.find_all('td'))
            d[busNo] = list(map(lambda x: 0 if x == 'Arriving' else int(x), [nextBus, subsequentBus]))
        return d

    def getInfoB(rows):
        busNos = [row.find_all('td')[0].text.split()[0] for row in rows]
        busTimes = [[int(i.text.split()[0]) if i.text.split()[0] != 'Arriving' else 0 for i in row.find_all('td')[1:]] for row in rows]
        return busNos, busTimes

    title = app.find('h3').text
    return {
        'title': title.upper(),
        'buses': getInfo(busStops)
        # 'buses': dict(zip(*getInfoB(busStops)))
    }

# @trackTime
def getBusTimingsB(busStopNo):
    titleUrl = f'https://www.nextbuses.sg/api.php?title={busStopNo}'
    title = requests.get(titleUrl).json()['title']
    busUrl = f'https://www.nextbuses.sg/api.php?stop={busStopNo}'
    data = requests.get(busUrl).json()['data']

    return {
        'title': title,
        'buses': {
            k: v['eta'] for k,v in sorted(data.items(), key=lambda x: int(x[0]))
        }
    }

def extractAllBusStops():
    url = 'https://www.sbstransit.com.sg/service/sbs-transit-app?BusStop`No=67201&ServiceNo='
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

def compileBusStopInfo():
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
            print(f'Dropping {busStop["busStopNo"]}')
            # data.pop('busStopNo')
            continue
        print(f'Bus stop no. {busStop["busStopNo"]}: {latitude}, {longitude}')
        busStop['latitude'] = float(latitude)
        busStop['longitude'] = float(longitude)
    saveJson(data)

if __name__ == '__main__':
    no = 65021 # 67759
    # print(getBusTimingsA(no))
    print('===========================')
    print(getBusTimingsB(no))