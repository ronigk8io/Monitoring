import requests
import json
import sys

def get_stellar_block_number():
    if len(sys.argv) < 2:
        print("Usage: python script.py <node_ip>")
        return

    node_ip = sys.argv[1]
    node_port = "11625"  # Adjust this if the port may vary
    node_url = f"http://{node_ip}:{node_port}"

    try:
        response = requests.get(node_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(data["core_latest_ledger"])
        else:
            print("Failed to fetch block number. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)

# Usage
get_stellar_block_number()
