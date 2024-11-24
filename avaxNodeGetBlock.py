import requests
import json
import sys

def get_avalanche_block_number():
    if len(sys.argv) < 2:
        print("Usage: python script.py <node_ip>")
        return

    node_ip = sys.argv[1]
    node_port = "34569"  # Adjust this if the port may vary
    node_url = f"http://{node_ip}:{node_port}"

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1
    }
    try:
        response = requests.post(node_url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            block_number = int(data["result"], 16)
            print(block_number)
        else:
            print("Failed to fetch Avalanche block number. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)

# Usage
get_avalanche_block_number()
