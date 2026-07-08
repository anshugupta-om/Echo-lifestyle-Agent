"""
utils/logger.py
---------------
Centralised logging setup using the standard library (logging module).
No third-party dependency — works with any installed Python.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def _get_log_level() -> str:
    try:
        from config.settings import settings
        return settings.log_level.upper()
    except Exception:
        return "INFO"


def _setup() -> logging.Logger:
    log_level_str = _get_log_level()
    log_level = getattr(logging, log_level_str, logging.INFO)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s — %(message)s",
        datefmt="%H:%M:%S",
    )

    root = logging.getLogger("eco_agent")
    root.setLevel(log_level)

    # Avoid adding duplicate handlers on re-import
    if not root.handlers:
        # Console handler
        ch = logging.StreamHandler(sys.stderr)
        ch.setFormatter(fmt)
        ch.setLevel(log_level)
        root.addHandler(ch)

        # File handler
        log_dir = Path(__file__).resolve().parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        fh = logging.FileHandler(log_dir / "eco_agent.log", encoding="utf-8")
        fh.setFormatter(fmt)
        fh.setLevel(log_level)
        root.addHandler(fh)

    return root


logger = _setup()
