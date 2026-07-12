"""World-model layer: turn a real POV frame into a generated 'world'.

The hack thesis: pipe a live reality feed through a generative world model —
gamify your POV. "Play your life."

Same swappable-backend pattern as frame_source.py: one WorldModel interface,
several backends. FakeWorld works with NO API (canned transform of the seed
frame), so the whole UI + flow is demo-safe before any real model is wired.
Swap the backend via WORLD_MODEL in .env.

    seed frame (data URL) ──▶ WorldModel.generate() ──▶ generated world (data URL)
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from . import config


class WorldModel(ABC):
    """Transforms one POV frame (base64 data URL) into a generated world.

    Returns a dict: {"kind": "image"|"video", "data_url": str, "backend": str,
    "note": str}. kind lets the viewer pick <img> vs <video>.
    """

    @abstractmethod
    def generate(self, seed_frame_data_url: str, intent: str = "") -> dict:
        ...


class FakeWorld(WorldModel):
    """No-API stub: a 'painterly' recolor of the seed frame via OpenCV.

    Proves the end-to-end flow (button → seed → generated world beside real
    feed) with zero external dependency. Visibly different from the real frame
    so the demo reads as 'generated', not a passthrough.
    """

    def generate(self, seed_frame_data_url: str, intent: str = "") -> dict:
        import base64
        import cv2
        import numpy as np

        b64 = seed_frame_data_url.split(",", 1)[-1]
        buf = np.frombuffer(base64.b64decode(b64), dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if img is None:
            return {"kind": "image", "data_url": seed_frame_data_url,
                    "backend": "fake", "note": "decode failed — echoing seed"}

        # stylize → a dreamy, game-like recolor so it clearly looks generated
        styl = cv2.stylization(img, sigma_s=60, sigma_r=0.45)
        styl = cv2.applyColorMap(styl, cv2.COLORMAP_PLASMA)
        styl = cv2.addWeighted(img, 0.35, styl, 0.65, 0)

        ok, out = cv2.imencode(".jpg", styl, [cv2.IMWRITE_JPEG_QUALITY, 80])
        data_url = "data:image/jpeg;base64," + base64.b64encode(out.tobytes()).decode()
        return {"kind": "image", "data_url": data_url, "backend": "fake",
                "note": "FakeWorld stub — swap WORLD_MODEL for a real generator"}


def build_world_model() -> WorldModel:
    # real backends (cosmos / replicate / ...) plug in here once chosen.
    return FakeWorld()
