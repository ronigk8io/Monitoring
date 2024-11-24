#!/usr/bin/env python2.7
import requests

url = "https://mainnet-public.mirrornode.hedera.com/api/v1/blocks"

try:
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        block_number = response.json()['blocks'][0]['number']
        print(block_number)
    else:
        print("Failed to fetch block number. Status code:", response.status_code)
except requests.exceptions.RequestException as e:
    print("An error occurred:", e)

