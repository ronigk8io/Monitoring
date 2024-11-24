import requests

# Define the node URL
node_url = "https://cosmos-rest.publicnode.com"

# Function to fetch the latest block number from a node
def get_latest_block(node_url):
    endpoint = "/cosmos/base/tendermint/v1beta1/blocks/latest"  # Updated endpoint
    try:
        # Attempt to get data from the node with a 3-second timeout
        response = requests.get(node_url + endpoint, timeout=5)
        if response.status_code == 200:
            data = response.json()
            block_height = data["block"]["header"]["height"]
            return block_height
        else:
            print(f"Failed to fetch block number from {node_url}. Status code: {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        print(f"Timeout occurred when fetching from {node_url}")
        return None
    except Exception as e:
        print(f"An error occurred while fetching block number from {node_url}: {str(e)}")
        return None

# Fetch and print the latest block number
latest_block_number = get_latest_block(node_url)
if latest_block_number is not None:
    print(f"{latest_block_number}")
else:
    print("Could not retrieve the latest block number.")
