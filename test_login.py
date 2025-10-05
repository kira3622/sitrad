import requests

url = "http://127.0.0.1:8000/api/v1/auth/token/"
payload = {"username": "demo", "password": "demo1234"}

try:
    resp = requests.post(url, json=payload, timeout=10)
    print("STATUS:", resp.status_code)
    print("BODY:", resp.text)
except Exception as e:
    print("ERROR:", e)