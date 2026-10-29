"""Fetch SendGrid stats and write data.json for the dashboard.

Runs inside GitHub Actions. Needs env SENDGRID_API_KEY (a restricted key
with "Stats" read access only). Uses the standard library only.

When config.json has a "category" (the campaign app on the computer writes it),
only that campaign's emails are counted. Otherwise the whole account is counted.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
DATA_PATH = ROOT / "data.json"
MAX_SNAPSHOTS = 800
API_BASE = os.environ.get("SENDGRID_API_BASE", "https://api.sendgrid.com")

METRICS = [
    "requests", "processed", "delivered", "deferred",
    "opens", "unique_opens", "clicks", "unique_clicks",
    "bounces", "blocks", "spam_reports", "unsubscribes",
    "invalid_emails", "bounce_drops", "spam_report_drops", "unsubscribe_drops",
]


def fetch(api_key: str) -> list:
    today = datetime.now(timezone.utc).date().isoformat()
    start = min(CONFIG["start_date"], today)
    params = {"start_date": start, "end_date": today, "aggregated_by": "day"}
    endpoint = "/v3/stats"
    if CONFIG.get("category"):
        endpoint = "/v3/categories/stats"
        params["categories"] = CONFIG["category"]
    req = urllib.request.Request(
        f"{API_BASE}{endpoint}?{urllib.parse.urlencode(params)}",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main() -> int:
    api_key = os.environ.get("SENDGRID_API_KEY", "").strip()
    if not api_key:
        print("SENDGRID_API_KEY is not set", file=sys.stderr)
        return 1
    try:
        days = fetch(api_key)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        if CONFIG.get("category") and (e.code == 404 or "does not exist" in body):
            days = []  # a brand-new campaign has no stats yet
        else:
            print(f"SendGrid API error {e.code}: {body}", file=sys.stderr)
            return 1

    totals = {m: 0 for m in METRICS}
    per_day = []
    for day in days:
        m = {}
        for block in day.get("stats", []):
            for k, v in block.get("metrics", {}).items():
                m[k] = m.get(k, 0) + (v or 0)
        per_day.append({"date": day["date"], **{k: m.get(k, 0) for k in METRICS}})
        for k in METRICS:
            totals[k] += m.get(k, 0)

    old = {}
    if DATA_PATH.exists():
        try:
            old = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old = {}

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    # A new campaign starts a fresh history instead of continuing the previous one's
    same_campaign = old.get("category") == CONFIG.get("category")
    snaps = old.get("snapshots", []) if same_campaign else []
    snap = {"t": now, **{k: totals[k] for k in
            ("requests", "delivered", "unique_opens", "unique_clicks", "bounces", "spam_reports")}}
    if not snaps or any(snaps[-1].get(k) != snap[k] for k in snap if k != "t"):
        snaps.append(snap)
    snaps = snaps[-MAX_SNAPSHOTS:]

    data = {"updated_at": now, "category": CONFIG.get("category"), "totals": totals,
            "per_day": per_day, "snapshots": snaps}
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK requests={totals['requests']} delivered={totals['delivered']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
