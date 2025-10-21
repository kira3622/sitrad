import ssl, urllib.request
ctx = ssl.create_default_context()
url = 'http://127.0.0.1:8001/cost-calculation/api/commandes/'
with urllib.request.urlopen(url, context=ctx) as resp:
    print('status', resp.status)
    print(resp.read().decode('utf-8')[:800])