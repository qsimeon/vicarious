"""FastAPI + WebSocket server.

Browser flow: POST /pay (mock checkout) → open WS /ws → the broadcaster's live
POV frames stream into the viewer's UI for 60s.
"""
from __future__ import annotations

import pathlib

from fastapi import Body, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse

from .frame_source import build_frame_source
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


@app.post("/gamify")
async def gamify(seed: str = Body(..., embed=True), intent: str = Body("", embed=True)):
    """Pipe the current POV frame through the world model → a generated world."""
    import asyncio
    result = await asyncio.to_thread(world.generate, seed, intent)
    return JSONResponse(result)


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
