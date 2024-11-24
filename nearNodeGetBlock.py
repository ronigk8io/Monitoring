#!/usr/bin/env python2.7
import json
import sys
import requests
import re

if len(sys.argv) < 2:
    print("Usage:", sys.argv[0], "<node_ip>")
    sys.exit(1)

node_ip = sys.argv[1]
ip_regex = r"[0-9.][0-9.]*"
if len(re.findall(ip_regex, node_ip))>0 and re.findall(ip_regex, node_ip)[0] == node_ip:
    pass
else:
    response = requests.post(
        ""+node_ip,
        headers={"Content-Type": "application/json",
                "Connection": "Keep-Alive"},
        data=json.dumps({
            "jsonrpc": "2.0",
            "id": 67,
            "method": "block",
            "params": {
            "finality": "final"
            }
        }),
        timeout=5
    )
    print(response.json()['result']['header']['height'])
