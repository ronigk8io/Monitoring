#!/usr/bin/env python2.7
import sys
import requests

if len(sys.argv) < 2:
    print("Usage: " + sys.argv[0] + " <node_ip>")
    sys.exit(1)

node_ip = sys.argv[1]

# Construct the URL
if node_ip.endswith('/'):
    node_url = node_ip + "api/core/v2/info"
else:
    node_url = node_ip + "/api/core/v2/info"

try:
    # Send a GET request to the node URL with a timeout of 5 seconds
    response = requests.get(node_url, timeout=5)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Access the value of latestMilestoneIndex and print it
        latest_milestone_index = data.get('status', {}).get('latestMilestone', {}).get('index')
        if latest_milestone_index is not None:
            print(latest_milestone_index)
        else:
            print("Latest Milestone Index not found in the JSON response.")
    else:
        print("Failed to fetch data. Status code:", response.status_code)
except requests.exceptions.RequestException as e:
    print("An error occurred:", e)

