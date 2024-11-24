import requests

url = 'https://api.blockchair.com/polkadot/stats'

try:
    r = requests.get(url, timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(data['data']['blocks'])
    else:
        print("Failed to fetch block number. Status code:", r.status_code)
except Exception as e:
    print("An error occurred:", e)
