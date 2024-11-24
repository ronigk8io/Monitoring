#!/bin/bash

# Define the URL and output file
url="https://api.fullstack.cash/v5/blockchain/getBlockCount"
output_file="output.log"

# Perform the request with a timeout
timeout 5 wget -qO- "$url" --no-check-certificate 2>/dev/null > "$output_file"

# Check the exit status of the last command
status=$?

# Handle different cases
case $status in
    0)
        echo "$(cat $output_file)"
        rm "$output_file" ;;
    124)
        echo "Error: The request timed out." ;;
    4)
        echo "Error: Network failure. Unable to connect to the server." ;;
    *)
        echo "Error: An unexpected error occurred with status code: $status" ;;
esac

# Output the result to a log file
echo "$(date): Completed with status $status" >> log.txt
