import requests

def get_current_tron_block():
    # Base URL for the Tron API
    base_url = "https://tron-rpc.publicnode.com"
    # Specific endpoint for getting the current block
    endpoint = "/wallet/getnowblock"

    # Complete URL constructed
    url = base_url + endpoint

    # Making a POST request to the Tron API for the current block
    response = requests.post(url, json={}, timeout=5)  # No need for headers as requests defaults to JSON

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the current block number and print it
        current_block_number = data['block_header']['raw_data']['number']
        print(current_block_number)
    else:
        print("Failed to fetch the current block. Status code:", response.status_code)

# Call the function to execute
get_current_tron_block()
