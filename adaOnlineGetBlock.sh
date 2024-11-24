#!/bin/bash

# Path to the file containing the API key
API_KEY_FILE="Tokens/CardanoApiToken_cardanoscan"

# Check if the API key file exists and is readable
if [ ! -f "${API_KEY_FILE}" ] || [ ! -r "${API_KEY_FILE}" ]; then
    echo "API key file does not exist or is not readable."
    exit 1
fi

# Read the API key from the file and trim any whitespace
API_KEY=$(cat "${API_KEY_FILE}" | tr -d '[:space:]')

# Ensure the API key is not empty
if [ -z "${API_KEY}" ]; then
    echo "API key is empty."
    exit 1
fi

# Make the API call
json=$(timeout 4 curl -s -X GET "https://api.cardanoscan.io/api/v1/block/latest" -H "apiKey: ${API_KEY}")
if [ $? -ne 0 ]; then
    echo "Curl command failed."
    echo 0
    exit 1
fi

#echo "JSON Response: $json"  # Debugging line to print the raw JSON response

# Parse the height from the JSON response
result=$(echo $json | jq '.blockHeight')
if [ $? -ne 0 ]; then
    echo "jq command failed."
    echo 0
    exit 1
fi

# Check if the result is non-empty and not null
if [ -n "$result" ] && [ "$result" != "null" ]; then
    echo $result
else
    echo 0
fi
