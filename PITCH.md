# Vicarious — Pitch & Slide Handoff

*Sundai Club Hack #131 · Theme: World Models · Harvard i-Lab · submit by 8:15 PM*

---

## 1. Project card copy (paste-ready)

**Title:** Vicarious — See through my eyes

**Tagline:** Pay $1, live 60 seconds of someone else's life — then hit "Gamify this" and watch a world model turn their real POV into a playable one.

**Description:**
> Vicarious is a paywall on a live first-person video stream: pay $1, watch one broadcaster's real POV for exactly 60 seconds, one viewer at a time. The twist for World Models — a "🎮 Gamify this" button grabs the current POV frame and pipes it through a real generative world model (fal.ai LTX-Video, image→video), returning a short generated clip of that scene *beside* the live feed. We fuse live reality with world-model generation: gamify a real point of view. Built end-to-end in Python (FastAPI + WebSocket, webcam today, smart glasses next).

**Tags:** `world-models` · `generative-video` · `live-streaming` · `smart-glasses` · `full-stack`

---

## 2. The 60-second verbal pitch

> People already pay to live other lives — that's what social media and games *are*. Vicarious sells that directly. Pay a dollar, and for 60 seconds you see through my eyes — my live POV, one viewer at a time.
>
> Now the World Models part. There's a button: **Gamify this**. It takes the frame I'm looking at *right now* and runs it through a real generative world model — fal's LTX image-to-video — and beside my live feed you watch a generated clip of my world start to move. Real reality on the left, a generated world on the right, from the same instant.
>
> To be precise: what's built today is snapshot → generated clip, about 35 seconds to render five seconds of video. It's the **Renderer** class of world model — the Sora/Runway/Kling family. It is *not yet* real-time interactive generation; that's Genie-3 class, demo-only, no public API. That real-time version — where you don't just *watch* my life, you *play* it as it happens — is our north star.
>
> The wedge is one broadcaster and a laptop webcam, swappable to Mentra smart glasses via a stub we already wrote. The vision is: anyone with glasses broadcasts a POV you can pay to see — and to play. **Play your life.**

---

## 3. Slide deck outline (6 slides)

### Slide 1 — Hook: people pay to live other lives
- Social media, streaming, games — billions spent to *be somewhere else, be someone else*.
- Vicarious sells that impulse directly, no algorithm in between.
- **Visual:** big-type title card "See through my eyes." Dark theme.

### Slide 2 — The product
- Pay $1 → watch one broadcaster's **live POV for exactly 60 seconds**.
- One viewer at a time; others queue (a paywall + FIFO lock). Feed goes dark → auto-refund.
- Built in Python: FastAPI + WebSocket streams JPEG frames (~1 / 2s) to the browser.
- **Visual:** `step1-paywall.png` (Pay $1 screen) → `step2-live.png` (live 60s countdown feed).

### Slide 3 — The World Models connection (honest taxonomy)
- "🎮 Gamify this" grabs the **current POV frame** and pipes it through a real generative world model.
- Backend: **fal.ai LTX-Video, image→video** — the **Renderer** class (Sora / Runway / Kling family).
- We combine *live reality* (POV stream) with *world-model generation* — gamify a real point of view.
- **Honest scope, stated up front:** snapshot → one ~5s generated clip, ~35s latency. NOT real-time interactive generation.
- **Visual:** `wm-demo.png` — live real feed **beside** the generated world video.

### Slide 4 — Live demo moment
- Show the live webcam POV. Hit **Gamify this**. "generating your world…"
- ~35s later: a generated moving clip of the exact scene plays beside the real feed.
- Same frame, two realities — one captured, one generated. That's the payload.
- **Visual:** run it live on `localhost:8000`; fallback = `gamify-flow.png` + the pre-rendered `dev/fal_world.mp4`.

### Slide 5 — Vision / roadmap (the north star)
- **Real-time, interactive** POV world generation — don't watch my life, *play* it live. That's **Genie-3 class** (demo-only, no public API today).
- Transport upgrade: WebSocket snapshots → smooth video (WebRTC / RTMP).
- Source swap: laptop webcam → **Mentra Live smart glasses** (`MentraSource` stub already in place, ~30s flip).
- Scale: one broadcaster today → anyone with glasses broadcasting a payable, playable POV.
- **Visual:** taxonomy ladder — Renderer (built) → Interactive/Genie-class (vision), arrow pointing up.

### Slide 6 — The ask
- We built the working seam between **live reality and generative world models**: pay to see a real POV, one click to generate a world from it.
- Verified end-to-end today: real webcam frame → fal LTX → generated video in the viewer.
- Ask: your vote — and pointers to any **real-time world-gen API** the moment one ships.
- **Visual:** logo + tagline "Play your life." + `localhost:8000` QR / URL.

### 3.5 — Where the real demo screenshots live
All in the repo root: **`wm-demo.png`** (real POV feed + generated world side by side — the money shot), `gamify-flow.png`, `step1-paywall.png`, `step2-live.png`, plus the build dashboard at `dash-check.png` and a pre-rendered clip at `dev/fal_world.mp4`.

---

## 4. Anticipated judge Q&A

**Q: Is this real-time? It looks like you're just running an image-to-video model on a snapshot.**
That's exactly right, and we're not claiming otherwise. Tier 1, what's built and verified, is snapshot → ~5s generated clip at ~35s latency. Real-time interactive generation is Genie-3 class — demo-only, no public API today. We shipped the honest thing that works and positioned the real-time version as the roadmap, not the demo.

**Q: How is this actually a "world model" and not just a video-gen gimmick?**
It's the **Renderer** class in the world-models taxonomy — the Sora/Runway/Kling branch: condition on an observation, generate a coherent continuation of that scene. LTX image→video takes a real POV frame and rolls the world forward. What's novel isn't the model; it's the *seam* — a live, monetized, real reality feed as the conditioning input. World models usually start from a prompt or a game state; ours starts from a paid stranger's actual eyes.

**Q: Why 60 seconds and $1 and one viewer? Feels arbitrary.**
It's the minimum honest unit of the thesis — a scarce, priced, exclusive slice of someone's lived experience. Scarcity (one viewer, one minute) is the product, not a limitation. It also keeps the paywall + queue logic real and demoable instead of hand-waved.

**Q: The webcam isn't really "POV" and the model latency breaks immersion. Why should we believe the vision?**
Fair on both. Webcam is the demo-safe stand-in; the `MentraSource` stub means swapping to true head-mounted POV is a config flip, not a rewrite — same frame interface downstream. Latency is the honest gap between Renderer-class (today) and Genie-class interactive generation (north star); we're betting that API arrives, and we've built the product seam that's ready for it the day it does.

**Q: What's genuinely built vs. slideware?**
Built and verified today: FastAPI + WebSocket POV streaming, the $1 paywall + single-viewer queue + auto-refund-on-dark-feed, the swappable frame-source and world-model backends, and a real webcam frame → fal LTX → generated video playing in the viewer. Runs locally: `uv run python run.py` → `localhost:8000`. Slideware: real-time interactive generation and the multi-broadcaster glasses network — clearly labeled roadmap.
