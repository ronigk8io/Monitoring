#!/usr/bin/env python2.7
import sys
import requests
import re

if len(sys.argv) < 2:
    print("Usage:", sys.argv[0], "<node_ip>")
    sys.exit(1)

node_ip = sys.argv[1]
ip_regex = r"[0-9\.][0-9\.]*"

if len(re.findall(ip_regex, node_ip))>0 and re.findall(ip_regex, node_ip)[0] == node_ip:
    response = requests.post(
        "http://"+node_ip+":6060/health",
        data={'net': 'mainnet',
              'node_id': "0.0.3"},
        timeout=5
    )
    print(response.status_code==200)

else:
    response = requests.get(
        node_ip+"/blocks",
        headers={"Content-Type": "application/json",
                "Connection": "Keep-Alive"},
        timeout=5
        )
    print(response.json()['blocks'][0]['number'])



