from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import WizardDocument


def load_document(
    json_path: str | Path,
    *,
    prefer_external_loader: bool = True,
    depth: Any | None = None,
    include_bom: bool = True,
) -> WizardDocument:
    """Load the guide without modifying the source JSON.

    When the team's ``disassembly_loader.build_guide`` is importable, its
    normalized object is used. Otherwise this module reads the normalized
    Wizard JSON directly. Both paths are converted into the same internal
    ``WizardDocument`` representation.

    ``depth`` and ``include_bom`` are accepted to remain compatible with the
    shared CustomTkinter GUI, which calls ``export_to_pptx(path, depth=spec,
    include_bom=bom_needed)``. If the external loader does not support those
    keyword arguments, the function safely falls back to ``build_guide(path)``.
    """
    path = Path(json_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"JSON file not found: {path}")
    if path.suffix.lower() != ".json":
        raise ValueError(f"Expected a .json input file, received: {path.name}")

    source: Any
    if prefer_external_loader:
        try:
            from disassembly_loader import build_guide  # type: ignore
        except ImportError:
            source = None
        else:
            try:
                source = build_guide(str(path), depth=depth, include_bom=include_bom)
            except TypeError:
                source = build_guide(str(path))
        if source is not None:
            return WizardDocument.from_any(source, source_dir=str(path.parent))

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return WizardDocument.from_any(payload, source_dir=str(path.parent))
