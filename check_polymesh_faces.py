#!/usr/bin/env python3
"""Polymesh face probes + Slack (Monitoring-server style).

Probe A: Hot-like GET {BJ}/polymesh/v1/health (last_milestone age).
Probe B: BJ-like node block age via sidecar /blocks/head (or :9934 /health peers).

Default notify: Slack #healthcenter (same token as MonitorManager).
CW SNS email stays on the host cron metrics -- this script is the easy Slack path.

Usage (Monitoring Server):
  python3 check_polymesh_faces.py
Cron example:
  */5 * * * * cd /home/ubuntu/Monitoring && python3 check_polymesh_faces.py >> logs/polymesh_faces.log 2>&1
"""
from __future__ import annotations

import json
import os
import time
import urllib.request

BJ_HEALTH_URL = os.environ.get(
    "BJ_HEALTH_URL", "https://blockjinn.gk8.network/polymesh/v1/health"
)
# Public DNS -- SG must allow this host
NODE_RPC_HEALTH = os.environ.get(
    "NODE_RPC_HEALTH", "http://polymesh-mainnet.gk8.network:9934/health"
)
SIDECAR_HEAD = os.environ.get(
    "SIDECAR_HEAD", "http://polymesh-mainnet.gk8.network:8080/blocks/head"
)
MAX_AGE_SEC = int(os.environ.get("MAX_AGE_SEC", "300"))
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "C04LPKAGV6U")  # healthcenter
SLACK_TOKEN_PATH = os.environ.get(
    "SLACK_TOKEN_PATH", "Tokens/slack_token_for_nodes_monitoring_app"
)


def http_get(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def probe_a() -> tuple[bool, str]:
    try:
        raw = http_get(BJ_HEALTH_URL)
        d = json.loads(raw)
        secs = d["last_milestone"]["BlockBased"]["timestamp"]["timestamp"]["secs"]
        age = time.time() - float(secs)
        ok = age <= MAX_AGE_SEC
        return ok, f"bj age_s={int(age)} block={d['last_milestone']['BlockBased'].get('number')}"
    except Exception as e:
        return False, f"bj error={e}"


def probe_b() -> tuple[bool, str]:
    try:
        health = json.loads(http_get(NODE_RPC_HEALTH, timeout=8))
        peers_ok = (not health.get("isSyncing", True)) and int(health.get("peers") or 0) >= 1
        head = json.loads(http_get(SIDECAR_HEAD, timeout=10))
        ts_ms = None
        for ex in head.get("extrinsics") or []:
            m = ex.get("method") or {}
            if m.get("pallet") == "timestamp" and m.get("method") == "set":
                ts_ms = int((ex.get("args") or {}).get("now"))
                break
        if ts_ms is None:
            return False, "node missing timestamp extrinsic"
        age = time.time() - (ts_ms / 1000.0)
        ok = peers_ok and age <= MAX_AGE_SEC
        return ok, f"node age_s={int(age)} peers_ok={peers_ok} block={head.get('number')}"
    except Exception as e:
        return False, f"node error={e}"


def notify_slack(subject: str, text: str) -> None:
    token = open(SLACK_TOKEN_PATH, encoding="utf-8").read().strip()
    body = json.dumps({"channel": SLACK_CHANNEL, "text": f"*{subject}*\n{text}"}).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        out = json.loads(resp.read().decode())
    if not out.get("ok"):
        raise RuntimeError(f"slack failed: {out}")


def main() -> int:
    a_ok, a_msg = probe_a()
    b_ok, b_msg = probe_b()
    line = f"polymesh faces A={'OK' if a_ok else 'FAIL'} ({a_msg}) B={'OK' if b_ok else 'FAIL'} ({b_msg})"
    print(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), line)
    if a_ok and b_ok:
        return 0
    subject = "Polymesh face probe FAIL"
    detail = (
        f"A Hot->BJ /v1/health: {'OK' if a_ok else 'FAIL'} -- {a_msg}\n"
        f"B BJ->node block age: {'OK' if b_ok else 'FAIL'} -- {b_msg}\n"
        f"Ticket GK8-45835"
    )
    try:
        notify_slack(subject, detail)
        print("slack_ok")
    except Exception as e:
        print(f"slack_skip {e}")
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
