
Steps:

- Get code
- Update nodes lists in nodes.txt
- run install_monitoring.sh
- run install_nodes_monitoring_crontab.txt and install_certs_renewal_sudo_crontab.txt
- test crontab commands
- aws configure - supply credentials for aws ses user with send email permissions
  - also see you set the user's correct region from the user's aws IAM
  - DOC: https://stackoverflow.com/questions/37528301/email-address-is-not-verified-aws-ses

Flow:

- Add coin and allowed block diff - to Node.py in "max_block_diff_name"
- Add url/ip, coin ticker, description - to nodes.txt
- Add coinOnlineGetBlock.py and coinNodeGetBlock.py scripts

Tests:
- use email for tests only for your email
- use notifications:
  - while testing: use the nodes-monitoring-tests slack channel
  - in production: use the healthcenter slack channel

BlockJinn checks (app-level -- separate from node MonitorManager; live under `blockjinn/`):
- `blockjinn/check_blockjinn_scanners.py` -- all mainnet `/v1/health` milestone ages
- `blockjinn/check_polymesh_faces.py` -- Polymesh Hot-like + node face probes
- Safe test: `python3 blockjinn/check_blockjinn_scanners.py --dry-run`
- Test Slack: `python3 blockjinn/check_blockjinn_scanners.py --channel-test --max-age-sec 1 --chains ethereum --force-notify`
- Prod cron (Monitoring host `ubuntu@3.222.94.21`, log `~/logs/blockjinn_scanners.log`):
  `*/5 * * * * cd /home/ubuntu/Monitoring && /usr/bin/python3 blockjinn/check_blockjinn_scanners.py >> ~/logs/blockjinn_scanners.log 2>&1`
- Default Slack = `#healthcenter` (`C04LPKAGV6U`). Silent when all OK; re-alert dedup 60 min.
- Thresholds: 30 min default; bitcoin/bitcoincash 60 min.

====================

Work status and info from 2024-05


Notifications status:
- currently the configured notifications are:
  - slack notifications to nodes-monitoring -- in the meanwhiel for Mark
  - slack notifications to healthcenter -- after adding all the nodes, remove nodes-monitoring channel posts, and use only healthcenter without the current influx nodes checks
  - emails to roni for test reasons

TO DO:
V - Add more nodes to the list
V - Add the last added nodes to the nodes.txt file
V - Last field of comments is missing for the nodes. Not urgent but should be fixed.
- fix this: self.owner = "BD" if "127.0.0.1" in ip else "GK8"   to get owner from the 3rd part of line in nodes.txt

Nodes list:
- There are still nodes to add to the monitoring list: cosmos (roni), cardano (dima), avalanche, arbitrum (evm), tron (shahar), near (celsius)
  - Ready:
    - cosmos - online + node (our url)
    - cardano - online (cardanoscan.io - have registered to free api service) + node (https://cardano-mainnet.blockfrost.io)
    - arbitrum (evm, nginx) - online + (https://api.tatum.io/v3/blockchain/node/arb-one-mainnet)
    - tron (native) - online (https://tron-rpc.publicnode.com) + node (https://api.trongrid.io)
    - near (public) - online () + node (https://rpc.mainnet.near.org)
    - celo (public) - online + node
    - avalanche (evm, nginx, tatum) - online (list) + node (https://api.tatum.io/v3/blockchain/node/avax-mainnet/ext/bc/C/rpc)
    - base (evm, nginx, tatum) - online (list) + node (https://api.tatum.io/v3/blockchain/node/base-mainnet)
    - xlm - online + node (BD, nginx)
    - 

done:
added nginx conf for more coins. from wallets.
fixed a few lines in few files monitor manager, node.py, nodes.txt, install_monitoring.sh, crontab

info:
evm list: chainlink
getblocks.io are nice evnthough their near service took too much time from me and did not work

other:
- erc20token: in cold, coin management, create, load, and you get a list of 100+
- evm - each has its on node, it's an Eth Virtual Machine


Testnet:
- Holesky - (https://ethereum-holesky-rpc.publicnode.com) + (https://svc.blockdaemon.com/ethereum/holesky/native)
- tron - (https://api.shasta.trongrid.io)
