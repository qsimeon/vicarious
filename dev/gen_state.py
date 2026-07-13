"""Regenerate dev/state.json — the snapshot the build dashboard polls.

Source of truth for phase status is the PHASES list below (edited as the build
progresses). Everything else (git, ports, file tree) is probed live.
Stdlib only, so it runs before the uv migration.
"""
from __future__ import annotations

import json
import socket
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- phase status: hand-edited as the build advances -----------------------
# status ∈ {"done", "active", "pending"}
PHASES = [
    {"id": 0, "title": "Follow-along dashboard",
     "detail": "Live build monitor on :8001", "status": "done"},
    {"id": 1, "title": "Migrate to uv + pyproject.toml",
     "detail": "requirements.txt → pyproject, .python-version", "status": "done"},
    {"id": 2, "title": "Boot app on webcam",
     "detail": ":8000 serves, WebSocket connects, frames grab", "status": "done"},
    {"id": 3, "title": "Verify Pay→live→done flow",
     "detail": "Playwright drives the UI, screenshots each step", "status": "done"},
    {"id": 4, "title": "Commit MVP + anchor HANDOFF",
     "detail": "git commit 'MVP verified', doc note", "status": "done"},
    {"id": 5, "title": "World-model layer (Tier-1)",
     "detail": "POV frame → fal.ai LTX → generated world video", "status": "done"},
    {"id": 6, "title": "Mentra glasses (guided)",
     "detail": "register app, tunnel, capture, bridge MentraSource", "status": "pending"},
]

# --- live probes ------------------------------------------------------------

def port_up(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.25)
        return s.connect_ex((host, port)) == 0


def git_info() -> dict:
    def run(*args):
        try:
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                  text=True, timeout=3).stdout.strip()
        except Exception:
            return ""
    dirty = bool(run("status", "--porcelain"))
    return {
        "branch": run("rev-parse", "--abbrev-ref", "HEAD") or "—",
        "last_commit": run("log", "-1", "--pretty=%h %s"),
        "dirty": dirty,
        "n_files": len(run("ls-files").splitlines()) if run("ls-files") else 0,
    }


def app_tree() -> list[dict]:
    """The product files (excludes dev/, .venv, caches)."""
    out = []
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        parts = rel.parts
        if any(x in parts for x in (".git", ".venv", "__pycache__", "dev",
                                     ".playwright-mcp", ".DS_Store")):
            continue
        if p.suffix in (".png", ".jpeg", ".jpg"):  # screenshot artifacts
            continue
        if p.is_file():
            out.append({"path": str(rel), "lines": _count_lines(p)})
    return out


def _count_lines(p: Path) -> int:
    try:
        return sum(1 for _ in p.open("rb"))
    except Exception:
        return 0


def build() -> dict:
    done = sum(1 for p in PHASES if p["status"] == "done")
    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "generated_epoch": int(time.time()),
        "project": "Vicarious — see through my eyes",
        "thesis": "Pay $1, watch my live POV for 60 seconds.",
        "phases": PHASES,
        "progress_pct": round(done / len(PHASES) * 100),
        "services": [
            {"name": "Build dashboard", "port": 8001, "up": port_up(8001)},
            {"name": "Vicarious app", "port": 8000, "up": port_up(8000)},
        ],
        "git": git_info(),
        "files": app_tree(),
    }


if __name__ == "__main__":
    (Path(__file__).parent / "state.json").write_text(json.dumps(build(), indent=2))
    print("state.json regenerated")
