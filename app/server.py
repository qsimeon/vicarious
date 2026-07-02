"""FastAPI + WebSocket server.

Browser flow: POST /pay (mock checkout) → open WS /ws → the broadcaster's live
POV frames stream into the viewer's UI for 60s.
"""
from __future__ import annotations

import pathlib

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse

from .frame_source import build_frame_source
from .orchestrator import manager, run_session

app = FastAPI(title="Vicarious")
WEB = pathlib.Path(__file__).resolve().parent.parent / "web"


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


@app.post("/pay")
def pay():
    """Mock Stripe checkout. Swap for a real Stripe Checkout + webhook later."""
    return JSONResponse({"paid": True, "viewers_ahead": manager.viewers_ahead})


@app.websocket("/ws")
async def ws(sock: WebSocket):
    await sock.accept()

    async def emit(event: dict):
        await sock.send_json(event)

    source = None
    try:
        await manager.acquire(emit)
        source = build_frame_source()
        await run_session(source, emit)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await emit({"type": "error", "msg": str(e)})
    finally:
        if source is not None:
            source.close()
        manager.release()
        try:
            await sock.close()
        except Exception:
            pass
