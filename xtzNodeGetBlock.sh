#!/bin/bash

api_token=$(cat Tokens/TezosExternalApiToken)

# Function to get current block height from a given node
get_xtz_online () {
  local node_address="$1"
  json=$(timeout 4 curl --silent -H "Content-Type: application/json" -H "X-API-Key: $api_token" \
        "$node_address:11625/explorer/tip" 2>/dev/null)
  result=$(echo $json | jq '.height')
}

# Check if the script was called with an IP address
if [[ -z "$1" ]]; then
  echo "Usage: $0 <node IP address>"
  exit 1
fi

# Initial call to get block height
get_xtz_online "$1"

# Check the block height multiple times with condition to avoid loop issues
for i in {1..10} ; do
  if [[ $result == "2797174" ]]; then
    get_xtz_online "$1"
  else
    break
  fi
done

# Fetch the latest block number from tzkt.io for comparison
second_check_xtz_block_number=$(curl --silent "https://api.tzkt.io/v1/blocks/count")

# Compare and print the higher block number
if [[ -n $result && -n $second_check_xtz_block_number ]]; then
  echo $(( result > second_check_xtz_block_number ? result : second_check_xtz_block_number ))
else
  echo "Error: Could not retrieve block numbers."
fi
