"""Test path configuration for the PPTX exporter module."""
from __future__ import annotations

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MAIN_SOURCE = REPOSITORY_ROOT / "src" / "main"

if str(MAIN_SOURCE) not in sys.path:
    sys.path.insert(0, str(MAIN_SOURCE))
