#!/usr/bin/env python2.7
import requests
import sys

def get_latest_block(node_url):
    endpoint = "/cosmos/base/tendermint/v1beta1/blocks/latest"
    try:
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

# Check if node URL is provided as a command-line argument
if len(sys.argv) < 2:
    print("Usage: {} <node_url>".format(sys.argv[0]))
    sys.exit(1)

node_url = sys.argv[1]

# Fetch and print the latest block number
latest_block_number = get_latest_block(node_url)
if latest_block_number is not None:
    print(f"{latest_block_number}")
else:
    print("Could not retrieve the latest block number.")
