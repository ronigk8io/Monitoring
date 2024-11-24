#!/bin/bash


[[ ! $1 ]] && echo "Usage: "$0" <node_ip>"  && exit

BTC=`timeout 4 curl --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getblockcount", "params": [] }' \
     -H 'content-type: text/plain;'  http://518095d92ceecf87:085d478af18a9082@$1:8335 2>/dev/null`
BTC_BLOCK_NUMBER=`grep -oP '(?<=\{\"result\"\:).*?(?=,)' <<< $BTC`
echo $BTC_BLOCK_NUMBER

