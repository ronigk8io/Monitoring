import requests
import json

# Define the URLs of Arbitrum nodes
nodes = [
    "https://arbitrum.llamarpc.com",
    "https://arb-pokt.nodies.app",
    "https://arbitrum-one-rpc.publicnode.com",
    "https://api.stateless.solutions/arbitrum-one/v1/demo",
    "https://arb-mainnet.g.alchemy.com/v2/demo"
]

# Define the JSON-RPC payload
payload = {
    "jsonrpc": "2.0",
    "method": "eth_blockNumber",
    "params": [],
    "id": 1
}

# Function to fetch block number from a node
def get_block_number(node_url):
    try:
        # Send the POST request
        response = requests.post(node_url, json=payload, timeout=5)

        # Parse the response
        if response.status_code == 200:
            data = response.json()
            block_number = int(data["result"], 16)  # Convert hexadecimal to decimal
            return block_number
        else:
            ##print("Failed to fetch block number from", node_url, ". Status code:", response.status_code)
            return None
    except Exception as e:
        ##print("An error occurred while fetching block number from", node_url, ":", str(e))
        return None

# Iterate through nodes and fetch block number
for node_url in nodes:
    block_number = get_block_number(node_url)
    if block_number is not None:
        ##print("Block number from", node_url, ":", block_number)
        print(block_number)
        break

