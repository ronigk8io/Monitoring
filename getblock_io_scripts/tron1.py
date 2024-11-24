import requests
import json

def get_latest_block_number(token_path):
    # Read the API token from a file
    try:
        with open(token_path, 'r') as file:
            token = file.read().strip()
    except FileNotFoundError:
        raise Exception(f"Token file not found at {token_path}.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the token file: {str(e)}.")

    # Adjust the URL to the correct endpoint provided for your API access
    url = f"https://go.getblock.io/{token}/jsonrpc"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": "getblock.io"
    })

    # Send the POST request
    response = requests.post(url, headers=headers, data=payload)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if 'result' in data:
            # Convert hexadecimal block number to integer
            block_number = int(data['result'], 16)
            return block_number
        else:
            raise ValueError("No 'result' key in response, check API or payload.")
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

# Example usage
token_path = "Tokens/getblock_io_tron"
try:
    latest_block_number = get_latest_block_number(token_path)
    print(latest_block_number)
except Exception as e:
    print("Error:", e)
