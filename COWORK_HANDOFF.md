# Vicarious — Cowork Handoff Packet

> **What this is:** the cold-start packet for a fresh Cowork/Cursor/Claude session
> (or a human collaborator) picking up Vicarious. Open this first. It is
> self-contained: current state, how to run, what's next, and the traps.
> Written 2026-07-12. Lives *inside* the git repo so it travels with the code.
> For the deeper "why / learning-from-zero" narrative, see `../HANDOFF.md` (parent dir).

---

## 30-second orientation

**Vicarious** = pay to watch a live first-person POV stream ("see through my eyes")
for 60 seconds. The hackathon twist: pipe that real POV frame through a **generative
world model** so a real feed becomes a *playable generated world* — "play your life."

Two layers, both built and committed:
1. **POV streaming** (the product) — camera → server → viewer browser, 60s sessions.
2. **World-model gamify** (the hack) — freeze a POV frame → world model → generated world.

---

## Run it (≈2 min)

```bash
cd vicarious-hack
uv sync                      # reproducible env from pyproject.toml + uv.lock
cp .env.example .env         # webcam defaults work with no keys
uv run python run.py         # → http://localhost:8000
```
Then: open :8000 → **Pay $1** → 60s of your webcam streams to the viewer → click
**🌍 Gamify this** → the current frame is piped through the world model → generated world.

**Follow-along dashboard** (optional, for watching a build):
```bash
dev/monitor.sh               # → http://localhost:8001  (phases, services, git, files)
```

---

## Architecture (current, verified)

```
camera ─▶ frame_source ─▶ orchestrator ─▶ server ─────▶ viewer browser
          WebcamSource     (60s loop,      (FastAPI +     renders frames
          MentraSource      frame-drop      WebSocket)     (NO getUserMedia)
          (glasses stub)    tolerant)           │
                                                 │  POST /gamify {seed frame}
                                                 ▼
                                          world_model ─▶ generated world
                                          FakeWorld (no API, OpenCV transform)
                                          FalWorld  (real: fal.ai LTX img→video)
                                          + backup clip fallback (demo-safe)
```

**Swappable-backend pattern is the key design idiom** (used twice): both
`frame_source.py` and `world_model.py` define an ABC + interchangeable backends
selected by an env var. A "fake"/local backend always exists so the full flow runs
with zero API keys. Follow this pattern for any new capability.

## File map

| File | Role |
|------|------|
| `app/config.py` | env settings: `FRAME_SOURCE`, `WORLD_MODEL`, `FAL_KEY`, session timing, `MAX_FRAME_MISSES` |
| `app/frame_source.py` | `WebcamSource` (works), `MentraSource` (glasses stub — the slot) |
| `app/orchestrator.py` | 60s session loop, single-viewer lock + queue, frame-drop tolerance |
| `app/server.py` | FastAPI: `/pay`, `/ws` (stream), `/gamify`, `/backup_world.mp4` |
| `app/world_model.py` | `WorldModel` ABC · `FakeWorld` (no API) · `FalWorld` (fal.ai LTX) |
| `web/index.html` | viewer UI: paywall → live POV → gamify + style presets → world card |
| `dev/` | build dashboard (`monitor.sh`, `gen_state.py`, `dashboard.html`), demo recorder |

## Config knobs (`.env`)

- `FRAME_SOURCE=webcam|mentra` — camera source (webcam works today)
- `WORLD_MODEL=fake|fal` — `fake` = no API (safe default); `fal` = real gen, needs `FAL_KEY`
- `FAL_KEY=` — fal.ai key, only if `WORLD_MODEL=fal`
- `SESSION_SECONDS=60`, `FRAME_INTERVAL_SECONDS=2`, `MAX_FRAME_MISSES=3`

---

## What's next (pick up here)

1. **Mentra glasses** (task #8, deferred to last) — register app at console.mentra.glass,
   get API key, run the TS hello-world, then fill in `MentraSource`. See `../HANDOFF.md §4`.
   This is the "real hardware" upgrade; webcam already proves the pipe.
2. **World-model depth** — Tier-1 (frame→clip) is done. Tier-2 = explorable 3D
   (HunyuanWorld); Tier-3 = real-time playable (Genie 3, north star). See `../PITCH_HANDOFF.md §5`.
3. **Real payments** — `/pay` is a mock; swap for Stripe Checkout + webhook.

## Known limitations (documented, not bugs to panic over)

An adversarial review (2026-07-12, in `../HANDOFF.md`) found these — **all require
concurrent viewers, which a solo demo never hits**, so they're deferred:
- Single-viewer lock is ownership-blind (disconnect race with 3+ clients → two streams).
- Queue position/ETA off-by-one; `_waiting` can inflate on a narrow error path.
- Session may over-deliver ≤1 frame past 60s (telemetry only).

## Traps (don't relearn these the hard way)

- **Don't add an LLM to the core.** The product is video transport, not AI narration.
  The original hackathon agent-crew was deleted on purpose (see `../HANDOFF.md`).
- **Don't reintroduce `getUserMedia` on the viewer page** — the viewer must render
  frames *from the server*, not its own camera. That was the original bug.
- **Don't mix in Octopus** — separate project (`~/mas664-hw4`); `octopus-swarm/` was
  moved out to `../octopus-swarm`. Different repo, different goal.
- **`FakeWorld` first, real backend second** — keep the no-API path working so demos
  never hard-depend on a live API mid-presentation.

## Repo facts

- Python 3.13, `uv` (not pip/conda). `uv sync` → `uv run python run.py`.
- git: `main`, clean. ~579 LOC of product code. Latest commit: demo polish + backup fallback.
- `.env` gitignored; secrets never committed. `dev/` scratch artifacts gitignored.
