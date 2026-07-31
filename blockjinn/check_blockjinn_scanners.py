#!/usr/bin/env python3
"""BlockJinn mainnet scanner lag check (Monitoring-server style).

For each chain face, GET https://blockjinn.gk8.network/<chain>/v1/health and
alert Slack if last_milestone age exceeds the chain threshold.

Learned from: MonitorManager.py (node tip lag) + check_polymesh_faces.py (BJ health).

Usage (Monitoring Server):
  cd /home/ubuntu/Monitoring && python3 blockjinn/check_blockjinn_scanners.py --dry-run
  python3 blockjinn/check_blockjinn_scanners.py --channel-test
  python3 blockjinn/check_blockjinn_scanners.py

Cron example:
  */5 * * * * cd /home/ubuntu/Monitoring && /usr/bin/python3 blockjinn/check_blockjinn_scanners.py >> ~/logs/blockjinn_scanners.log 2>&1

Safety:
  - Default Slack is #healthcenter. Use --channel-test or --dry-run first.
  - Dedup state avoids spam (re-alert on new fail set or every 60 min).
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

BJ_BASE = os.environ.get("BJ_BASE", "https://blockjinn.gk8.network").rstrip("/")
DEFAULT_MAX_AGE_SEC = int(os.environ.get("MAX_AGE_SEC", "1800"))  # 30 min
# Slow block-time chains: allow longer quiet periods before alert
SLOW_MAX_AGE_SEC = {
    "bitcoin": 3600,
    "bitcoincash": 3600,
}
# Mainnet scanner faces with a public /v1/health (from ECS *-scn + health probe)
CHAINS = [
    "arbitrum",
    "assethub",
    "avalanche",
    "base",
    "binance",
    "bitcoin",
    "bitcoincash",
    "cardano",
    "cosmos",
    "ethereum",
    "fantom",
    "hedera",
    "near",
    "optimism",
    "polygon",
    "polymesh",
    "ripple",
    "solana",
    "starknet",
    "stellar",
    "tezos",
    "tron",
]

# Repo root = parent of this package dir (Tokens/ lives there)
REPO_ROOT = Path(__file__).resolve().parent.parent
SLACK_HEALTHCENTER = "C04LPKAGV6U"
SLACK_TEST = "C06V5E6PEFJ"  # nodes-monitoring-tests
SLACK_TOKEN_PATH = os.environ.get(
    "SLACK_TOKEN_PATH",
    str(REPO_ROOT / "Tokens" / "slack_token_for_nodes_monitoring_app"),
)
STATE_PATH = Path(
    os.environ.get(
        "BJ_SCANNER_STATE",
        str(Path(__file__).resolve().parent / "blockjinn_scanners_state.json"),
    )
)
DEDUP_SEC = int(os.environ.get("BJ_SCANNER_DEDUP_SEC", "3600"))


def http_get(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


_AGE_OVERRIDE: int | None = None


def max_age_for(chain: str) -> int:
    if _AGE_OVERRIDE is not None:
        return _AGE_OVERRIDE
    return int(SLOW_MAX_AGE_SEC.get(chain, DEFAULT_MAX_AGE_SEC))


def parse_milestone(data: dict[str, Any]) -> tuple[float | None, str, str]:
    """Return (epoch_secs, kind, number_str)."""
    lm = data.get("last_milestone")
    if not isinstance(lm, dict) or not lm:
        return None, "missing", "?"

    # BlockBased: timestamp.timestamp.secs + number
    if "BlockBased" in lm and isinstance(lm["BlockBased"], dict):
        bb = lm["BlockBased"]
        num = str(bb.get("number", "?"))
        try:
            secs = float(bb["timestamp"]["timestamp"]["secs"])
            return secs, "BlockBased", num
        except (KeyError, TypeError, ValueError):
            return None, "BlockBased", num

    # DagBased (hedera): timestamp.secs at top of DagBased
    if "DagBased" in lm and isinstance(lm["DagBased"], dict):
        db = lm["DagBased"]
        try:
            secs = float(db["timestamp"]["secs"])
            return secs, "DagBased", "?"
        except (KeyError, TypeError, ValueError):
            return None, "DagBased", "?"

    kind = next(iter(lm.keys()))
    return None, str(kind), "?"


def check_chain(chain: str) -> dict[str, Any]:
    url = f"{BJ_BASE}/{chain}/v1/health"
    limit = max_age_for(chain)
    try:
        raw = http_get(url)
        data = json.loads(raw)
        secs, kind, num = parse_milestone(data)
        if secs is None:
            return {
                "chain": chain,
                "ok": False,
                "reason": f"unparsed milestone kind={kind}",
                "age_s": None,
                "number": num,
                "limit_s": limit,
                "url": url,
            }
        age = time.time() - secs
        ok = age <= limit
        return {
            "chain": chain,
            "ok": ok,
            "reason": "ok" if ok else f"stale age_s={int(age)}>{limit}",
            "age_s": int(age),
            "number": num,
            "limit_s": limit,
            "kind": kind,
            "url": url,
        }
    except urllib.error.HTTPError as e:
        return {
            "chain": chain,
            "ok": False,
            "reason": f"http {e.code}",
            "age_s": None,
            "number": "?",
            "limit_s": limit,
            "url": url,
        }
    except Exception as e:
        return {
            "chain": chain,
            "ok": False,
            "reason": f"error={type(e).__name__}: {e}",
            "age_s": None,
            "number": "?",
            "limit_s": limit,
            "url": url,
        }


def load_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def should_notify(fails: list[dict[str, Any]], state: dict[str, Any], now: float) -> bool:
    fail_keys = sorted(f"{r['chain']}:{r.get('number')}:{r.get('reason')}" for r in fails)
    last_keys = state.get("last_fail_keys") or []
    last_ts = float(state.get("last_notify_ts") or 0)
    if fail_keys != last_keys:
        return True
    if now - last_ts >= DEDUP_SEC:
        return True
    return False


def notify_slack(channel: str, subject: str, text: str) -> None:
    token = open(SLACK_TOKEN_PATH, encoding="utf-8").read().strip()
    body = json.dumps({"channel": channel, "text": f"*{subject}*\n{text}"}).encode()
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


def format_fail_table(fails: list[dict[str, Any]]) -> str:
    lines = ["chain | age_s | limit_s | number | reason"]
    for r in fails:
        age = r["age_s"] if r["age_s"] is not None else "?"
        lines.append(
            f"{r['chain']} | {age} | {r['limit_s']} | {r['number']} | {r['reason']}"
        )
    return "```\n" + "\n".join(lines) + "\n```"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check all BlockJinn scanner milestone ages")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check only; never post Slack; never write notify state",
    )
    parser.add_argument(
        "--channel-test",
        action="store_true",
        help="Post to nodes-monitoring-tests instead of healthcenter",
    )
    parser.add_argument(
        "--force-notify",
        action="store_true",
        help="Ignore dedup (still respects --dry-run)",
    )
    parser.add_argument(
        "--chains",
        default=",".join(CHAINS),
        help="Comma-separated chain list (default: all mainnet faces)",
    )
    parser.add_argument(
        "--max-age-sec",
        type=int,
        default=None,
        help="Override default max age for all chains (slow-chain map still applies unless set)",
    )
    args = parser.parse_args()

    global _AGE_OVERRIDE
    if args.max_age_sec is not None:
        _AGE_OVERRIDE = args.max_age_sec

    chains = [c.strip() for c in args.chains.split(",") if c.strip()]
    channel = SLACK_TEST if args.channel_test else SLACK_HEALTHCENTER
    now = time.time()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))

    # Parallel probes -- 22 serial HTTPS calls are slow on the Monitoring host
    by_chain: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(chains)))) as pool:
        futs = {pool.submit(check_chain, c): c for c in chains}
        for fut in as_completed(futs):
            row = fut.result()
            by_chain[row["chain"]] = row
    results = [by_chain[c] for c in chains if c in by_chain]
    fails = [r for r in results if not r["ok"]]
    ok_n = len(results) - len(fails)

    print(f"{stamp} checked={len(results)} ok={ok_n} fail={len(fails)} dry_run={args.dry_run}")
    for r in results:
        age = r["age_s"] if r["age_s"] is not None else "?"
        flag = "OK" if r["ok"] else "FAIL"
        print(
            f"  {flag} {r['chain']:<14} age_s={age:<6} limit={r['limit_s']:<5} "
            f"num={r['number']} {r['reason']}"
        )
    print(f"SUMMARY {'ALL_OK' if not fails else 'HAS_FAILS'} ok={ok_n} fail={len(fails)}")

    if not fails:
        if not args.dry_run:
            state = load_state()
            state["last_ok_ts"] = now
            state["last_fail_keys"] = []
            save_state(state)
        return 0

    state = load_state()
    notify = args.force_notify or should_notify(fails, state, now)
    detail = (
        f"BlockJinn scanner milestone stale/unreachable ({len(fails)}/{len(results)})\n"
        f"{format_fail_table(fails)}\n"
        f"base={BJ_BASE} channel={channel}"
    )

    if args.dry_run:
        print("dry_run: would notify=" + str(notify))
        print(detail)
        return 1

    if not notify:
        print("dedup: skip slack (same fails within window)")
        return 1

    try:
        notify_slack(channel, "BlockJinn scanner lag FAIL", detail)
        print(f"slack_ok channel={channel}")
        state["last_notify_ts"] = now
        state["last_fail_keys"] = sorted(
            f"{r['chain']}:{r.get('number')}:{r.get('reason')}" for r in fails
        )
        save_state(state)
    except Exception as e:
        print(f"slack_fail {e}")
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
