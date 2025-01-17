import requests
import json

url = 'http://localhost:8000/check-user/'

data = {
    'telegram_user_id': '123456789'
}

response = requests.post(url, json=data)

if response.status_code == 200:

    print(response.json())
    parsed_data = response.json()
    print(parsed_data['exists'])
else:
    print(f"Error: {response.status_code}")
    print(response.text)
