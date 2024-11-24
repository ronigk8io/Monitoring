import requests

# Other RPC providers: https://docs.near.org/api/rpc/providers

# Define the NEAR Protocol RPC endpoint
rpc_endpoint = 'https://1rpc.io/near'

# Define the request payload to get the latest block
payload = {
    "jsonrpc": "2.0",
    "method": "status",
    "params": [],
    "id": "1"
}

try:
    # Send the POST request to the NEAR Protocol RPC endpoint
    response = requests.post(rpc_endpoint, json=payload, timeout=5)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the response JSON data
        response_json = response.json()

        # Check if the 'result' key exists in the response
        if 'result' in response_json:
            # Extract the latest block information
            latest_block = response_json['result']['sync_info']['latest_block_height']

            # Print the latest block information
            print(latest_block)
        else:
            print("Error: Invalid response format or missing 'result' key.")
    else:
        print("Error: Request failed with status code:", response.status_code)
except Exception as e:
    print("Error:", e)
