# RUN
# - python -m pytest -p no:cacheprovider tests -sv
# - python -m pytest -p no:cacheprovider tests -svk 'not success' --print
# - pytest .. (if __init__.py exists in tests dir)

from copy import deepcopy
import requests
import pytest
import os

@pytest.fixture
def payload():
    '''Returns valid payload for /postError'''
    return {
        'url': '{}/{}'.format(os.getenv('STORE_URL'), 'postError'),
        'payload': {
            'password': int(os.getenv('STORE_PASS')),
            'app': os.getenv('APP_NAME'),
            'key': int(os.getenv('APP_PASS')),
            'error': '<u>TEST</u> - VALID PAYLOAD'
        }
    }

@pytest.fixture
def verbose():
    '''Returns default verbose setting'''
    return False

def test_bot_postError_success(payload):
    assert requests.post(payload['url'], json=payload['payload']).json().get('status') == 'OK'

def test_bot_postError_failure(payload, verbose):

    # App not found
    tmp = deepcopy(payload)
    tmp['payload']['app'] = 'NO'
    response = requests.post(tmp['url'], json=tmp['payload']).json()
    if verbose:
        print(f'\nApp not found: {payload}')
    assert response.get('status') == 'NOT_OK' and response.get('ERROR') == 'App not found in list!'
    
    # Missing parameters
    tmp = deepcopy(payload)
    tmp['payload'].pop('app')
    response = requests.post(tmp['url'], json=tmp['payload']).json()
    if verbose:
        print(f'Missing parameters: {payload}')
    assert response.get('status') == 'NOT_OK' and response.get('ERROR') == 'Wrong password and parameters!'
    tmp = deepcopy(payload)
    tmp['payload'].pop('password')
    response = requests.post(tmp['url'], json=tmp['payload']).json()
    if verbose:
        print(f'Missing parameters: {payload}')
    assert response.get('status') == 'NOT_OK' and response.get('ERROR') == 'Wrong password and parameters!'
    tmp = deepcopy(payload)
    tmp['payload'].pop('key')
    response = requests.post(tmp['url'], json=tmp['payload']).json()
    if verbose:
        print(f'Missing parameters: {payload}')
    assert response.get('status') == 'NOT_OK' and response.get('ERROR') == 'Wrong password and parameters!'
    
    # Wrong password
    tmp = deepcopy(payload)
    tmp['payload']['key'] = 1234
    response = requests.post(tmp['url'], json=tmp['payload']).json()
    if verbose:
        print(f'Wrong password: {payload}')
    assert response.get('status') == 'NOT_OK' and response.get('ERROR') == 'Wrong password and parameters!'
    
    # Wrong method
    response = requests.get(payload['url']).json()
    if verbose:
        print(f'Wrong method: {payload}')
    assert response.get('status') == 'NOT_OK' and response.get('ERROR') == 'Nothing here!'