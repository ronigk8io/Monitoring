# BlockJinn monitoring checks

App-level probes for BlockJinn (not GK8 chain nodes -- those stay in repo root via `MonitorManager.py`).

| Script | Purpose |
|---|---|
| `check_blockjinn_scanners.py` | All mainnet scanner `/v1/health` milestone ages --> Slack `#healthcenter` |
| `check_polymesh_faces.py` | Polymesh Hot-like BJ health + node/sidecar face |

Run from Monitoring repo root so relative docs match cron:

```bash
cd /home/ubuntu/Monitoring
python3 blockjinn/check_blockjinn_scanners.py --dry-run
```

Token path resolves to `../Tokens/slack_token_for_nodes_monitoring_app` automatically.
