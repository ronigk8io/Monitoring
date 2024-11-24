#!/bin/bash


[[ ! $1 ]] && echo "Usage: "$0" <node_ip>" && exit

CELO=`timeout 4 curl -H "Content-Type: application/json" --data "{\"jsonrpc\":\"2.0\",\"method\":\"eth_blockNumber\",\"params\":[],\"id\":67}" \
     http://$1:8555 2>/dev/null`
CELO_HEX=`echo $CELO | jq '.result'`
CELO_BLOCK_NUMBER=`echo $CELO_HEX | tr -d '"'`
echo $(($CELO_BLOCK_NUMBER))
