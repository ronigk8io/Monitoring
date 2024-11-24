#!/bin/bash

# Read API token
api_token=$(cat Tokens/TezosExternalApiToken)

# Function to get current block height from tzstats API
get_xtz_online () {
  json=$(timeout 5 curl --silent -H "Content-Type: application/json" -H "X-API-Key: $api_token" \
       "https://api.tzstats.com/explorer/tip" 2>/dev/null)
  result=$(echo $json | jq '.height')
}

# Initial call to get block height
get_xtz_online

# Check the block height multiple times with some condition to avoid infinite loop
for i in {1..10}; do
  if [[ $result == "2797174" ]]; then
    get_xtz_online
    # Break if the result changes
    [[ $result != "2797174" ]] && break
  else
    break
  fi
done

# Fetch the latest block number from another API for comparison
second_check_xtz_block_number=$(curl --silent "https://api.tzkt.io/v1/blocks/count")

# Print the higher of the two block numbers
echo $(( result > second_check_xtz_block_number ? result : second_check_xtz_block_number ))
