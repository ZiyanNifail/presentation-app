import requests


presentation_id = 1
url = f'http://127.0.0.1:5000/api/analyze/{presentation_id}'

print(f"Requesting analysis for Presentation ID: {presentation_id}...")

try:
    
    response = requests.post(url)
    
    print("Status:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)