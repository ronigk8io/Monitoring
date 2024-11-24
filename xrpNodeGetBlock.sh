#!/bin/bash


[[ ! $1 ]] && echo "Usage: "$0" <node_ip>" && exit

XRP=`timeout 4 curl --data-binary '{"method": "account_info", "params": [{ "account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59", \
     "strict": true, "ledger_index": "validated" } ]}' \
     -H "content-type: text/plain;" $1:5005 2>/dev/null`
XRP_BLOCK_NUMBER_A=`grep -oP '(?<=_index\"\:).*?(?=,)' <<< $XRP`
# Alternative command, with method ledger and jq to parse json:

#if [[ $1 == "127.0.0.1" ]] ; then
  timeout 4 curl --data-binary '{"method": "ledger", "params": [{"ledger_index": "validated"}]}' -H "content-type: text/plain;" http://$1:5005 > jsonFile 2>/dev/null
#else
#  timeout 4 curl --data-binary '{"method": "ledger", "params": [{"ledger_index": "validated"}]}' -H "content-type: text/plain;" http://$1:5005 > jsonFile 2>/dev/null
#fi
JSON=`cat jsonFile`
XRP_BLOCK_NUMBER_B=`echo $JSON | jq -r '.result.ledger.ledger_index'`
echo $(( XRP_BLOCK_NUMBER_B > XRP_BLOCK_NUMBER_A ? XRP_BLOCK_NUMBER_A : XRP_BLOCK_NUMBER_B ))
rm jsonFile
