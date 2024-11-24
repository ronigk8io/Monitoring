#!/bin/bash


BTC_JSON=`timeout 5 curl -H "Content-Type: application/json" \
     "https://blockchain.info/latestblock" 2>/dev/null`

BTC_BLOCK=`echo $BTC_JSON | jq '.height'`
BTC_BLOCK_STRIP=`echo $BTC_BLOCK | grep "[0-9]*" -o` 

echo $BTC_BLOCK_STRIP
