import requests
import json

# Define the JSON-RPC payload
payload = {
    "jsonrpc": "2.0",
    "method": "eth_blockNumber",
    "params": [],
    "id": 1
}

# Define the URLs of Ethereum nodes
urls = [
    "https://optimism.drpc.org",
    "https://optimism.llamarpc.com",
    "https://optimism-rpc.publicnode.com"
]

for url in urls:
    try:
        # Send the POST request
        response = requests.post(url, json=payload, timeout=5)

        # Parse the response
        if response.status_code == 200:
            data = response.json()
            block_number = int(data["result"], 16)  # Convert hexadecimal to decimal
            print(block_number)
            break  # If successful, exit the loop
    except:
        pass  # Ignore exceptions and continue to the next URL
