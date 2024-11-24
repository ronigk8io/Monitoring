#!/bin/bash


[[ ! $1 ]] && echo "Usage: "$0" <node_ip>" && exit

BCH=`timeout 4 curl --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getblockcount", "params": [] }' \
     -H 'content-type: text/plain;'  http://518095d92ceecf87:f45k8qac9p2bd4k5@$1:8337 2>/dev/null`				&>/dev/null ### not printing output ###

BCH_BLOCK_NUMBER=`grep -oP '(?<=\{\"result\"\:).*?(?=,)' <<< $BCH`

echo $BCH_BLOCK_NUMBER

