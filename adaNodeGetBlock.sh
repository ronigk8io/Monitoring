#!/bin/bash

ADA_API_TOKEN=$(cat Tokens/CardanoApiToken)

[[ ! $1 ]] && echo "Usage: "$0" <node_url like https://cardano-mainnet.blockfrost.io> " &&	exit

json=`timeout 4 curl -H "project_id:$ADA_API_TOKEN" \
     "$1/api/v0/blocks/latest/" 2>/dev/null`
result=`echo $json| jq '.height' 2>/dev/null`
if [ ! -z "${result}"  ] && [ "${result}" != "null" ]
then
    echo $result
else
    echo 0
fi


