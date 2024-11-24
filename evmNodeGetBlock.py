import requests
import json

def getEVMBlock(node_ip):
    try:
        response = requests.post(
            "http://"+node_ip,
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 67
            }),
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            block_hex = data.get("result", "0x0")
            block_number = int(block_hex, 16)
            print(block_number)
        else:
            print("Error:", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print("Request error:", e)
    except ValueError as e:
        print("JSON decoding error:", e)
