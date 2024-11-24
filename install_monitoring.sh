#!/bin/bash
sudo apt update
sudo apt install python2 -y
sudo apt install jq -y
sudo apt install awscli -y
sudo apt install nginx -y
pip install beautifulsoup4
pip3 install beautifulsoup4
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
python2.7 get-pip.py
sudo apt install python-pip
sudo python2.7 -m pip install requests
echo '
## Mainnet
# blockdaemon: stellar + tezos + ripple + ethereum
server { listen 11625; location / { proxy_set_header Authorization "Bearer <<BEARER_TOKEN>>"; proxy_pass https://svc.blockdaemon.com/stellar/mainnet/native; proxy_ssl_server_name on; } }
server { listen 8732;  location / { proxy_set_header Authorization "Bearer <<BEARER_TOKEN>>"; proxy_pass https://svc.blockdaemon.com/tezos/mainnet/native; proxy_ssl_server_name on; } }
server { listen 5005;  location / { proxy_set_header Authorization "Bearer <<BEARER_TOKEN>>"; proxy_pass https://svc.blockdaemon.com/xrp/mainnet/native; proxy_ssl_server_name on; } }
server { listen 8545;  location / { proxy_set_header Authorization "Bearer <<BEARER_TOKEN>>"; proxy_pass https://svc.blockdaemon.com/ethereum/mainnet/native; proxy_ssl_server_name on; } }
# blockdaemon: optimism + polygon + polkadot
server { listen 34567;  location / { proxy_set_header Authorization "Bearer <<BEARER_TOKEN>>"; proxy_pass https://svc.blockdaemon.com/polygon/mainnet/native/http-rpc; proxy_ssl_server_name on; } }
server { listen 23456;  location / { proxy_set_header Authorization "Bearer <<BEARER_TOKEN>>"; proxy_pass https://svc.blockdaemon.com/optimism/mainnet/native/http-rpc; proxy_ssl_server_name on; } }
server { listen 45678;  location / { proxy_set_header Authorization "Bearer <<BEARER_TOKEN>>"; proxy_pass https://svc.blockdaemon.com/polkadot/mainnet/native/http-rpc; proxy_ssl_server_name on; } }
# tatum: Arbitrum + Avalanche + Base
server { listen 34568;  location / { proxy_set_header Authorization "<<TATUM_TOKEN>>"; proxy_pass https://api.tatum.io/v3/blockchain/node/arb-one-mainnet; proxy_ssl_server_name on; proxy_ssl_verify_depth 2; proxy_ssl_session_reuse on; } }
server { listen 34569;  location / { proxy_set_header Authorization "<<TATUM_TOKEN>>"; proxy_pass https://api.tatum.io/v3/blockchain/node/avax-mainnet/ext/bc/C/rpc; proxy_ssl_server_name on; proxy_ssl_verify_depth 2; proxy_ssl_session_reuse on; } }
server { listen 34570;  location / { proxy_set_header Authorization "<<TATUM_TOKEN>>"; proxy_pass https://api.tatum.io/v3/blockchain/node/base-mainnet; proxy_ssl_server_name on; proxy_ssl_verify_depth 2; proxy_ssl_session_reuse on; } }
' | sudo tee -a /etc/nginx/conf.d/gk8.conf
sudo systemctl restart nginx
echo "Insert aws ses user creds:"
aws configure
echo "Installing crontab."
bash install_crontab.sh
mkdir -p /home/ubuntu/Monitoring/Tokens
touch CardanoApiToken  CardanoApiToken_cardanoscan  EthereumApiToken  TezosExternalApiToken  apiTokens.json getblock_io_near  getblock_io_tron  slack_token_for_nodes_monitoring_app
echo "PLEASE PUT TOKENS IN PLACE."
[[ ! -d /home/ubuntu/Monitoring/ ]] && echo "Monitoring directory is missing." || echo "Monitoring directory is in place."
