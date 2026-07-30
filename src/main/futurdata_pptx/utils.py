from __future__ import annotations

import base64
import io
import re
from pathlib import Path
from typing import Any, Iterator, TypeVar

from PIL import Image

T = TypeVar("T")


def chunks(items: list[T], size: int) -> Iterator[list[T]]:
    size = max(1, int(size))
    for index in range(0, len(items), size):
        yield items[index:index + size]


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())


def safe_filename(value: str, fallback: str = "disassembly_guide") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._")
    return cleaned or fallback


def resolve_image(value: str | None, source_dir: str | None = None) -> Path | io.BytesIO | None:
    if not value:
        return None
    if value.startswith("data:image/"):
        try:
            _, encoded = value.split(",", 1)
            return io.BytesIO(base64.b64decode(encoded))
        except (ValueError, base64.binascii.Error):
            return None
    if value.startswith(("http://", "https://")):
        return None
    path = Path(value).expanduser()
    if not path.is_absolute() and source_dir:
        path = Path(source_dir) / path
    return path.resolve() if path.exists() and path.is_file() else None


def image_dimensions(source: Path | io.BytesIO) -> tuple[int, int]:
    if isinstance(source, io.BytesIO):
        source.seek(0)
        with Image.open(source) as image:
            size = image.size
        source.seek(0)
        return size
    with Image.open(source) as image:
        return image.size


def fit_rect(image_width: int, image_height: int, box_width: float, box_height: float) -> tuple[float, float]:
    if image_width <= 0 or image_height <= 0:
        return box_width, box_height
    image_ratio = image_width / image_height
    box_ratio = box_width / box_height
    if image_ratio >= box_ratio:
        return box_width, box_width / image_ratio
    return box_height * image_ratio, box_height
