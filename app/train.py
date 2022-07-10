from bs4 import BeautifulSoup
import requests
import os

from utils import loadConfig

FILES = ['train.html', 'train-1.html', 'train-2.html', 'train.png']

def getCookieStr(url):
    session = requests.Session()
    response = session.get(url)
    with open('train.html', 'w') as file:
        file.write(response.text)
    if response.ok:
        cookies = session.cookies.get_dict()
        if len(cookies) == 1:
            _, imageUrl, _ = getPayload()
            response = session.get(f'{url.split("/default")[0]}/{imageUrl}')
            with open('train.png', 'wb') as file:
                file.write(response.content)
            return '='.join([j for i in cookies.items() for j in i])
        else:
            return ''
    else:
        return ''

def getPayload():
    with open('train.html', 'r') as file:
        content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    imageUrl = soup.find('img', {'id': 'imgCaptcha'}).attrs['src']
    d = {
        'ScriptManager1': 'UP1|ibtnSubmit',
        '__EVENTTARGET': 'ibtnSubmit'
    }
    for ___ in soup.find_all('input'):
        if ___.attrs['name'] != '__EVENTTARGET':
            if 'value' in ___.attrs.keys():
                d[___.attrs['name']] = ___.attrs['value']
            else:
                d[___.attrs['name']] = ''
    return soup, imageUrl, d

for file in FILES:
    if os.path.exists(file):
        os.remove(file)
        print(f'{file} removed..')

url = 'https://trainarrivalweb.smrt.com.sg/default.aspx'

cookie = getCookieStr(url) if True else loadConfig()['train']['set-cookie']

headers = {
    'Cookie': cookie,    # IMPT
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'X-MicrosoftAjax': 'Delta=true'    # include to get non-html format
}

payload = {
    'ScriptManager1': 'UP1|ibtnSubmit',
    '__EVENTTARGET': 'ibtnSubmit',
    'txtCodeNumber': 740,
    # 'ScriptManager1': 'UP1|ddlStation',
    # '__EVENTTARGET': 'ddlStation',
    # 'ddlStation': 'BNL',
}

_, imageUrl, payload = getPayload()

# payload['txtCodeNumber'] = input(f'Cookie = {cookie.split("=")[1]}\nVerify @ {url.split("/default")[0]}/{imageUrl} , CODE=')
payload['txtCodeNumber'] = input('Verify train.png , CODE=')

response_1 = requests.post(url=url, headers=headers, data=payload)

with open('train.html', 'w') as file:
    file.write(response_1.text)

payload = {
    'ScriptManager1': 'UP1|ddlStation',
    '__EVENTTARGET': 'ddlStation',
    'ddlStation': 'BNL',
    **{k:v for k,v in payload.items() if k not in ['ScriptManager1', '__EVENTTARGET', 'txtCodeNumber']}
}

if 0:
    response_2 = requests.post(url=url, headers=headers, data=payload)

    with open('train.html', 'w') as file:
        file.write(response_2.text)