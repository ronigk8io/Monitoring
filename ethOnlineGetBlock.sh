#!/bin/bash

ApiToken=$(cat Tokens/EthereumApiToken)

get_eth_online () {
  ETH_JSON=$(timeout 5 curl -H "Content-Type: application/json" --data "{'Content-type': 'application/json',         'Accept': 'application/json'}" \
       "https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey="$ApiToken 2>/dev/null)
  ETH_BASE_16=$(echo $ETH_JSON | jq '.result')
  ETH_BASE_16_STRIP=$(echo $ETH_BASE_16 | grep "[a-f0-9][a-f0-9][a-f0-9]*" -o)
}

get_eth_online

# Retries
if [[ -z $ETH_BASE_16_STRIP ]] ; then
  for i in {1..10} ; do
    get_eth_online
    [[ $ETH_BASE_16_STRIP ]] && break
  done
fi

#second_check_eth_block_number=`curl --silent https://api.blockchair.com/ethereum/stats | jq '.data.best_block_height'`
#echo $(( 16#$ETH_BASE_16_STRIP > $second_check_eth_block_number ? 16#$ETH_BASE_16_STRIP : $second_check_eth_block_number ))


second_check_eth_block_number=$(curl --silent https://api.blockchair.com/ethereum/stats | jq '.data.best_block_height')
echo $(( 16#$ETH_BASE_16_STRIP > $second_check_eth_block_number ? 16#$ETH_BASE_16_STRIP : $second_check_eth_block_number ))

rm -f $second_check_eth_block_number
