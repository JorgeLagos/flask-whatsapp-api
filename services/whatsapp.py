import requests
import json
import os

WSP_API_TOKEN = os.getenv('WSP_API_TOKEN')
WSP_API_URL = os.getenv('WSP_API_URL')
WSP_API_VERSION = os.getenv('WSP_API_VERSION')
WSP_API_PHONE_ID = os.getenv('WSP_API_PHONE_ID')

def send_message(data: dict):
    try:
        response = requests.post(
            url = f'{WSP_API_URL}/{WSP_API_VERSION}/{WSP_API_PHONE_ID}/messages',
            data = json.dumps(data),
            headers = {
                'Content-Type': 'application/json', 
                'Authorization': f'Bearer {WSP_API_TOKEN}'
            }
        )

        print('send_message', response)
        if response.status_code == 200:
            return True
        
        return False
    except Exception as exception:
        print(exception)
        return False
    
def get_file(fileId: int):
    try:
        response = requests.get(
            url = f'{WSP_API_URL}/{WSP_API_VERSION}/{fileId}',
            headers = {
                'Content-Type': 'application/json', 
                'Authorization': f'Bearer {WSP_API_TOKEN}'
            }
        )

        if response.status_code == 200:
            return True, response.text
        
        return False, {}
    except Exception as exception:
        print(exception)
        return False, {}