#!/bin/bash


XRP=`timeout 4 curl --data-binary '{"method": "account_info", "params": [{ "account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59", \
     "strict": true, "ledger_index": "validated" } ]}' \
     -H "content-type: text/plain;" http://s1.ripple.com:51234 2>/dev/null`
XRP_BLOCK_NUMBER_A=`grep -oP '(?<=_index\"\:).*?(?=,)' <<< $XRP`
# Alternative command, with method ledger and jq to parse json:

timeout 5 curl --data-binary '{"method": "ledger", "params": [{"ledger_index": "validated"}]}' -H "content-type: text/plain;" http://s1.ripple.com:51234 > jsonFile 2>/dev/null
JSON=`cat jsonFile`
XRP_BLOCK_NUMBER_B=`echo $JSON | jq -r '.result.ledger.ledger_index'`

echo $(( XRP_BLOCK_NUMBER_B > XRP_BLOCK_NUMBER_A ? XRP_BLOCK_NUMBER_B : XRP_BLOCK_NUMBER_A ))
rm jsonFile
