"""Session orchestrator: the 60-second POV stream.

The product in its simplest honest form: for one paid minute, grab frames from
the broadcaster's camera and push them to the viewer's browser. One viewer at a
time; others wait in line.

No LLM, no agents — just live POV video from a camera to a remote screen. The
agent crew from the hackathon build is gone; this is the fundamental product.
"""
from __future__ import annotations

import asyncio
import time
from typing import Awaitable, Callable

from . import config
from .frame_source import FrameSource

Emit = Callable[[dict], Awaitable[None]]


class SessionManager:
    """Single active session + FIFO queue (one human, one pair of eyes)."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._waiting = 0

    @property
    def viewers_ahead(self) -> int:
        return self._waiting

    async def acquire(self, emit: Emit):
        self._waiting += 1
        pos = self._waiting - 1
        if pos > 0:
            await emit({"type": "queue", "ahead": pos,
                        "eta_sec": pos * config.SESSION_SECONDS})
        await self._lock.acquire()
        self._waiting -= 1

    def release(self):
        if self._lock.locked():
            self._lock.release()


manager = SessionManager()


async def run_session(source: FrameSource, emit: Emit) -> dict:
    """One paid 60-second session: stream the broadcaster's POV to the viewer."""
    start = time.time()
    deadline = start + config.SESSION_SECONDS
    frames = 0
    refund = False
    misses = 0  # consecutive dropped frames; only a sustained gap is "feed dark"

    await emit({"type": "session_start", "seconds": config.SESSION_SECONDS})

    while time.time() < deadline:
        remaining = max(0, int(deadline - time.time()))
        frame = await asyncio.to_thread(source.grab)

        if frame is None:
            # Tolerate transient drops (flaky USB / a single stale glasses frame);
            # only refund if the feed stays dark for several grabs in a row.
            misses += 1
            if misses >= config.MAX_FRAME_MISSES:
                refund = True
                await emit({"type": "feed_dark", "msg": "Feed went dark — issuing refund."})
                break
            await asyncio.sleep(config.FRAME_INTERVAL_SECONDS)
            continue

        misses = 0
        await emit({"type": "frame", "data_url": frame, "remaining": remaining})
        frames += 1
        await asyncio.sleep(config.FRAME_INTERVAL_SECONDS)

    summary = {
        "frames": frames,
        "duration_sec": round(time.time() - start, 2),
        "refund_issued": refund,
    }
    await emit({"type": "session_end", **summary})
    return summary
