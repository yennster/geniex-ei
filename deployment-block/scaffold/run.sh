#!/usr/bin/env bash
# Start the GenieX server (if not already running) and the agent loop.
set -euo pipefail
cd "$(dirname "$0")"

BASE_URL="$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['geniex'].get('base_url','http://127.0.0.1:18181/v1'))")"

if ! curl -fsS -m 2 "$BASE_URL/models" >/dev/null 2>&1; then
    echo "==> starting geniex serve (logs: geniex-serve.log)"
    nohup geniex serve > geniex-serve.log 2>&1 &
    for i in $(seq 1 60); do
        curl -fsS -m 2 "$BASE_URL/models" >/dev/null 2>&1 && break
        sleep 1
    done
    curl -fsS -m 2 "$BASE_URL/models" >/dev/null 2>&1 || {
        echo "error: GenieX server did not come up at $BASE_URL (see geniex-serve.log)" >&2
        exit 1
    }
fi

exec python3 agent.py "$@"
