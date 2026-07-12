"""Env-driven settings."""
import os
from dotenv import load_dotenv

load_dotenv()


def _int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


FRAME_SOURCE = os.getenv("FRAME_SOURCE", "webcam").lower()
WEBCAM_INDEX = _int("WEBCAM_INDEX", 0)

MENTRA_API_KEY = os.getenv("MENTRA_API_KEY", "")
MENTRA_PACKAGE = os.getenv("MENTRA_PACKAGE", "com.vicarious.glasses")

SESSION_SECONDS = _int("SESSION_SECONDS", 60)
FRAME_INTERVAL_SECONDS = _int("FRAME_INTERVAL_SECONDS", 2)
MAX_FRAME_MISSES = _int("MAX_FRAME_MISSES", 3)  # consecutive drops before refund
