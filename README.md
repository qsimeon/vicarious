# Vicarious — see through my eyes

Pay $1, watch my live POV for exactly 60 seconds. One viewer at a time.

The thesis: people already pay to live other lives — that's social media and
games. Vicarious sells that directly. Start with just my POV; later, anyone with
smart glasses can broadcast to paying viewers.

> **This is the fundamental product, not the hackathon demo.** An earlier build
> had an AI agent crew + Weave tracing; that was stripped out on 2026-07-01. The
> product needs no LLM — it streams camera frames to a remote viewer. See
> `../HANDOFF.md` for the full story and roadmap.

## What's here

```
app/
  config.py        # frame-source + session settings
  frame_source.py  # FrameSource interface · WebcamSource (works) · MentraSource (stub)
  orchestrator.py  # 60s session loop: grab frame → push to viewer · single-viewer lock
  server.py        # FastAPI + WebSocket, streams POV frames to the browser
web/
  index.html       # viewer UI: paywall → live 60s → done
run.py             # entrypoint: uvicorn app.server:app
```

## Run (≈2 min, with uv)

```bash
uv sync                       # build the locked env from pyproject.toml
cp .env.example .env          # defaults are fine for the webcam demo
uv run python run.py          # open http://localhost:8000
```

Click **Pay $1** (mock) → a 60s session starts, frames from your webcam stream
into the viewer. No API keys needed for the webcam path.

## How it works

- **Frame source** (`frame_source.py`): one interface, two implementations.
  `WebcamSource` grabs JPEG frames from your laptop camera (works today).
  `MentraSource` is the stub where the glasses plug in — wire it once the Mentra
  hello-world is running (see `../HANDOFF.md §4`).
- **Session loop** (`orchestrator.py`): for 60 seconds, grab a frame every
  `FRAME_INTERVAL_SECONDS` and push it to the viewer over the WebSocket. One
  active viewer at a time; others queue.
- **Transport**: currently ~1 frame / 2s over a WebSocket (honest-simplest). The
  main upgrade path is smooth video (WebRTC / MJPEG / RTMP) — that's the real
  engineering axis, not more features.

## Demo-safety

`FRAME_SOURCE=webcam` (the default) runs the whole app on your laptop camera.
Flip to `mentra` once the glasses SDK is wired — the loop is identical; only the
frame source swaps.
