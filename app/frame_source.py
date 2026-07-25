"""Frame source abstraction.

Everything downstream consumes base64 JPEG frames, so the rest of the app never
knows whether a frame came from a webcam (demo-safe) or the Mentra glasses.
Swap the source via FRAME_SOURCE in .env — flip in 30 seconds during the demo.
"""
from __future__ import annotations

import base64
import time
from abc import ABC, abstractmethod
from typing import Optional

from . import config


class FrameSource(ABC):
    """Yields the current POV frame as a base64 JPEG data URL (or None if dark)."""

    @abstractmethod
    def grab(self) -> Optional[str]:
        ...

    def close(self) -> None:
        pass


class WebcamSource(FrameSource):
    """Demo-safe POV: laptop/phone webcam via OpenCV."""

    def __init__(self, index: int = 0):
        import cv2  # local import so the module loads even without opencv

        self._cv2 = cv2
        self._cap = cv2.VideoCapture(index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open webcam index {index}")

    def grab(self) -> Optional[str]:
        ok, frame = self._cap.read()
        if not ok or frame is None:
            return None
        ok, buf = self._cv2.imencode(".jpg", frame, [self._cv2.IMWRITE_JPEG_QUALITY, 70])
        if not ok:
            return None
        b64 = base64.b64encode(buf.tobytes()).decode()
        return f"data:image/jpeg;base64,{b64}"

    def close(self) -> None:
        self._cap.release()


class MentraSource(FrameSource):
    """Live POV from Mentra glasses.

    MentraOS exposes camera capture over its TypeScript SDK. The simplest bridge
    for a Python harness: run a tiny MentraOS app that POSTs the latest captured
    frame to this process (or pushes to a shared buffer), and read it here.

    This stub returns the most recent frame pushed via `push_frame()`. Wire the
    MentraOS camera module (photo capture ~1 frame / FRAME_INTERVAL_SECONDS, or
    pull a keyframe off the RTMP livestream) to call push_frame().
    """

    def __init__(self, api_key: str, package: str):
        self.api_key = api_key
        self.package = package
        self._latest: Optional[str] = None
        self._ts: float = 0.0

    def push_frame(self, data_url: str) -> None:
        self._latest = data_url
        self._ts = time.time()

    def grab(self) -> Optional[str]:
        # Treat frames older than 5s as "feed went dark" → triggers refund.
        if self._latest is None or (time.time() - self._ts) > 5:
            return None
        return self._latest


# Shared across sessions + the /mentra/push receiver so pushed frames land in
# the same instance a session reads from.
_mentra_singleton: Optional[MentraSource] = None


def get_mentra_source() -> MentraSource:
    global _mentra_singleton
    if _mentra_singleton is None:
        _mentra_singleton = MentraSource(config.MENTRA_API_KEY, config.MENTRA_PACKAGE)
    return _mentra_singleton


def build_frame_source() -> FrameSource:
    if config.FRAME_SOURCE == "mentra":
        return get_mentra_source()
    return WebcamSource(config.WEBCAM_INDEX)
