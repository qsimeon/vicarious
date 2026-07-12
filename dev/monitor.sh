#!/usr/bin/env bash
# Build monitor: regenerate state.json on a loop + serve dev/ on :8001.
set -euo pipefail
DEV="$(cd "$(dirname "$0")" && pwd)"
PORT="${1:-8001}"

# background: refresh the snapshot every 2s
( while true; do python3 "$DEV/gen_state.py" >/dev/null 2>&1 || true; sleep 2; done ) &
REFRESH_PID=$!
trap 'kill $REFRESH_PID 2>/dev/null || true' EXIT

echo "[monitor] dashboard → http://localhost:$PORT/dashboard.html"
cd "$DEV"
python3 -m http.server "$PORT" --bind 127.0.0.1
