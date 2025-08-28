import requests
import json
import os

WSP_API_URL = os.getenv('WSP_API_URL')
WSP_API_TOKEN = os.getenv('WSP_API_TOKEN')

print(os.getenv('WSP_API_TOKEN'))

def send_message(data: dict):
    try:
        response = requests.post(
            url = WSP_API_URL,
            data = json.dumps(data),
            headers = {
                'Content-Type': 'application/json', 
                'Authorization': f'Bearer {WSP_API_TOKEN}'
            }
        )

        print(response)
        if response.status_code == 200:
            return True
        
        return False
    except Exception as exception:
        print(exception)
        return False