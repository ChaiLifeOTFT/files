#!/usr/bin/env python3
"""
DigiUs Service Coordinator CLI
Connects to SynthExecutionAgent's Service Management API v1.
Usage:
    python3 service_coordinator.py setup <api-key>
    python3 service_coordinator.py list
    python3 service_coordinator.py status <service_id>
    python3 service_coordinator.py start <service_id>
    python3 service_coordinator.py stop <service_id>
    python3 service_coordinator.py restart <service_id>
    python3 service_coordinator.py stream
    python3 service_coordinator.py keys
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing 'requests' library. Install with: pip install requests")
    sys.exit(1)

CONFIG_FILE = Path.home() / ".digius_coordinator.json"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(cfg: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def get_api(cfg: dict) -> tuple:
    base = cfg.get("base_url", "http://127.0.0.1:5000")
    key = cfg.get("api_key", "")
    if not key:
        print("No API key configured. Run:  python3 service_coordinator.py setup <api-key>")
        sys.exit(1)
    return base, key


def headers(key: str) -> dict:
    return {"X-API-Key": key, "Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_setup(args):
    if not args:
        print("Usage: service_coordinator.py setup <api-key> [base-url]")
        sys.exit(1)
    api_key = args[0]
    base_url = args[1] if len(args) > 1 else "http://127.0.0.1:5000"
    cfg = load_config()
    cfg["api_key"] = api_key
    cfg["base_url"] = base_url
    save_config(cfg)
    print(f"Config saved to {CONFIG_FILE}")
    print(f"  Base URL: {base_url}")
    print(f"  API Key:  {api_key[:8]}...{api_key[-8:]}")

    # Test connection
    try:
        r = requests.get(f"{base_url}/api/v1/services", headers=headers(api_key), timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"\n  Connection OK — {data['total']} services registered")
        else:
            print(f"\n  Warning: API returned {r.status_code}: {r.text[:200]}")
    except requests.ConnectionError:
        print(f"\n  Warning: Could not reach {base_url} — is SynthExecutionAgent running?")


def cmd_list(_args):
    cfg = load_config()
    base, key = get_api(cfg)
    r = requests.get(f"{base}/api/v1/services", headers=headers(key), timeout=10)
    r.raise_for_status()
    data = r.json()

    summary = data.get("summary", {})
    print(f"DigiUs Service Mesh — {data['total']} services")
    print(f"  online: {summary.get('online',0)}  offline: {summary.get('offline',0)}  "
          f"degraded: {summary.get('degraded',0)}  unknown: {summary.get('unknown',0)}")
    print("-" * 72)
    fmt = "{:<24} {:>5}  {:<10} {:<10} {}"
    print(fmt.format("SERVICE", "PORT", "STATUS", "LATENCY", "CATEGORY"))
    print("-" * 72)

    for sid, svc in sorted(data["services"].items(), key=lambda x: x[1]["port"]):
        health = svc.get("health", {})
        status = health.get("status", "unknown")
        latency = health.get("response_time_ms", "")
        latency_str = f"{latency}ms" if latency else "-"
        status_icon = {"online": "+", "offline": "x", "degraded": "~", "unknown": "?"}.get(status, "?")
        print(fmt.format(f"[{status_icon}] {svc['name']}", svc["port"], status, latency_str, svc["category"]))


def cmd_status(args):
    if not args:
        print("Usage: service_coordinator.py status <service_id>")
        sys.exit(1)
    sid = args[0]
    cfg = load_config()
    base, key = get_api(cfg)
    r = requests.get(f"{base}/api/v1/services/{sid}", headers=headers(key), timeout=10)
    if r.status_code == 404:
        print(f"Service '{sid}' not found.")
        sys.exit(1)
    r.raise_for_status()
    svc = r.json()
    print(json.dumps(svc, indent=2))


def cmd_control(action, args):
    if not args:
        print(f"Usage: service_coordinator.py {action} <service_id>")
        sys.exit(1)
    sid = args[0]
    cfg = load_config()
    base, key = get_api(cfg)

    # Step 1: Issue command
    r = requests.post(
        f"{base}/api/v1/services/{sid}/command",
        headers=headers(key),
        json={"action": action},
        timeout=10,
    )
    if r.status_code == 404:
        print(f"Service '{sid}' not found.")
        sys.exit(1)
    r.raise_for_status()
    cmd_data = r.json()
    token = cmd_data.get("token")
    print(f"Command: {action} {sid}")
    print(f"Token:   {token}")
    print(f"Expires: {cmd_data.get('expires_in_seconds')}s")

    # Step 2: Confirm
    confirm = input("\nConfirm execution? [y/N] ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    r2 = requests.post(
        f"{base}/api/v1/commands/{token}/confirm",
        headers=headers(key),
        timeout=30,
    )
    r2.raise_for_status()
    result = r2.json()
    print(json.dumps(result, indent=2))


def cmd_stream(_args):
    cfg = load_config()
    base, key = get_api(cfg)
    print("Streaming health status (Ctrl+C to stop)...")
    print()
    try:
        r = requests.get(
            f"{base}/api/v1/health/stream",
            headers=headers(key),
            stream=True,
            timeout=None,
        )
        for line in r.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            payload = json.loads(line[6:])
            ts = time.strftime("%H:%M:%S", time.localtime(payload["timestamp"]))
            summary = payload.get("summary", {})
            statuses = payload.get("services", {})
            online = [sid for sid, s in statuses.items() if s.get("status") == "online"]
            offline = [sid for sid, s in statuses.items() if s.get("status") == "offline"]
            print(f"[{ts}] online:{len(online)} offline:{len(offline)} "
                  f"degraded:{summary.get('degraded',0)} unknown:{summary.get('unknown',0)}")
            if offline:
                print(f"         down: {', '.join(offline)}")
    except KeyboardInterrupt:
        print("\nStream stopped.")


def cmd_keys(_args):
    cfg = load_config()
    base, key = get_api(cfg)
    r = requests.get(f"{base}/api/v1/auth/keys", headers=headers(key), timeout=10)
    r.raise_for_status()
    data = r.json()
    print("Registered API keys:")
    for entry in data.get("keys", []):
        print(f"  [{entry['key_prefix']}]  label={entry['label']}  scopes={entry['scopes']}  created={entry['created']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

COMMANDS = {
    "setup": cmd_setup,
    "list": cmd_list,
    "status": cmd_status,
    "start": lambda a: cmd_control("start", a),
    "stop": lambda a: cmd_control("stop", a),
    "restart": lambda a: cmd_control("restart", a),
    "stream": cmd_stream,
    "keys": cmd_keys,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        sys.exit(0)

    cmd_name = sys.argv[1]
    cmd_args = sys.argv[2:]

    fn = COMMANDS.get(cmd_name)
    if not fn:
        print(f"Unknown command: {cmd_name}")
        print(f"Available: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    fn(cmd_args)


if __name__ == "__main__":
    main()
