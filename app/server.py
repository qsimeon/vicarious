"""FastAPI + WebSocket server.

Browser flow: POST /pay (mock checkout) → open WS /ws → the broadcaster's live
POV frames stream into the viewer's UI for 60s.
"""
from __future__ import annotations

import base64
import pathlib

from fastapi import Body, FastAPI, File, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse

from .frame_source import build_frame_source, get_mentra_source
from .orchestrator import manager, run_session
from .world_model import build_world_model

app = FastAPI(title="Vicarious")
WEB = pathlib.Path(__file__).resolve().parent.parent / "web"
world = build_world_model()


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


@app.post("/pay")
def pay():
    """Mock Stripe checkout. Swap for a real Stripe Checkout + webhook later."""
    return JSONResponse({"paid": True, "viewers_ahead": manager.viewers_ahead})


@app.post("/mentra/photo")
async def mentra_photo(photo: UploadFile = File(...), requestId: str = Form("")):
    """Webhook for the Mentra Bluetooth SDK (Mentra Live camera glasses).

    The phone-side app calls requestPhoto({webhookUrl: ".../mentra/photo"}) and
    the glasses' JPEG arrives here as multipart form-data (`photo` + `requestId`).
    We convert it to a data URL for the shared MentraSource.
    Set FRAME_SOURCE=mentra to stream the glasses feed.
    """
    raw = await photo.read()
    mime = photo.content_type or "image/jpeg"
    data_url = f"data:{mime};base64," + base64.b64encode(raw).decode()
    get_mentra_source().push_frame(data_url)
    return JSONResponse({"ok": True, "requestId": requestId, "bytes": len(raw)})


@app.post("/mentra/push")
def mentra_push(data_url: str = Body(..., embed=True)):
    """JSON variant of the glasses bridge (data URL in, for testing or a custom
    bridge). The Bluetooth SDK itself uses /mentra/photo above."""
    get_mentra_source().push_frame(data_url)
    return JSONResponse({"ok": True})


@app.post("/gamify")
async def gamify(seed: str = Body(..., embed=True), intent: str = Body("", embed=True)):
    """Pipe the current POV frame through the world model → a generated world.

    Demo-safe: if the real backend errors, fall back to a pre-rendered clip so
    the viewer never hangs on 'generating…'.
    """
    import asyncio
    try:
        result = await asyncio.to_thread(world.generate, seed, intent)
        return JSONResponse(result)
    except Exception as e:
        backup = WEB.parent / "dev" / "fal_world.mp4"
        if backup.exists():
            return JSONResponse({"kind": "video", "data_url": "/backup_world.mp4",
                                 "backend": "backup", "note": f"live gen failed ({e}); backup clip"})
        return JSONResponse({"kind": "image", "data_url": seed, "backend": "error",
                             "note": str(e)})


@app.get("/backup_world.mp4")
def backup_world():
    """Pre-rendered generated clip — the demo fallback if live gen is slow/down."""
    return FileResponse(WEB.parent / "dev" / "fal_world.mp4")


@app.websocket("/ws")
async def ws(sock: WebSocket):
    await sock.accept()

    async def emit(event: dict):
        await sock.send_json(event)

    source = None
    try:
        async with manager.session(emit):
            source = build_frame_source()
            await run_session(source, emit)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await emit({"type": "error", "msg": str(e)})
    finally:
        if source is not None:
            source.close()
        try:
            await sock.close()
        except Exception:
            pass
