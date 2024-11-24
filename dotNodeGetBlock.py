#!/usr/bin/env python2.7
import sys
import requests
import json

if len(sys.argv) < 2:
    print("Usage:", sys.argv[0], "<node_ip>")
    sys.exit(1)

node_ip = sys.argv[1]

try:
    response = requests.post(
        "http://"+node_ip+":45678",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "jsonrpc": "2.0",
            "method": "chain_getBlock",
            "params": [],
            "id": 67
        }),
        timeout=5
    )

    if response.status_code == 200:
        data = response.json()
        dot_hex = (data['result']['block']['header']['number'])
        dot_block_number = int(dot_hex, 16)
        print(dot_block_number)
    else:
        print("Error:", response.status_code, response.text)
except requests.exceptions.RequestException as e:
    print("Request error:", e)
except ValueError as e:
    print("JSON decoding error:", e)
