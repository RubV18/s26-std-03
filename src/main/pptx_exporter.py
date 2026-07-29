"""Drop-in PPTX exporter for the Futurdata Disassembly Wizard.

This module is placed in ``src/main`` because the shared GUI imports:

    from pptx_exporter import export_to_pptx

The function accepts the GUI arguments ``depth`` and ``include_bom`` while the
actual rendering is delegated to the modular ``futurdata_pptx`` package.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from futurdata_pptx import ExportOptions, PPTXExportEngine, WizardDocument


def export_to_pptx(
    json_path: str | None = None,
    output_path: str | None = None,
    *,
    depth: Any | None = None,
    include_bom: bool = True,
    guide: Any | None = None,
    source_json_path: str | None = None,
    start_step: int | None = None,
    end_step: int | None = None,
    max_action_groups: int | None = None,
    groups_per_slide: int = 1,
    include_warnings: bool = True,
    include_images: bool = True,
) -> str:
    """Export a Wizard JSON or already-built guide to editable PowerPoint.

    Parameters are compatible with the team GUI:

        export_to_pptx(path, depth=spec, include_bom=bom_needed)

    They are also compatible with direct usage:

        export_to_pptx("example_air_fryer.json", "output.pptx")
    """
    options = ExportOptions(
        start_step=start_step,
        end_step=end_step,
        max_action_groups=max_action_groups,
        groups_per_slide=groups_per_slide,
        include_bom=include_bom,
        include_warnings=include_warnings,
        include_images=include_images,
    )
    engine = PPTXExportEngine()

    if guide is not None:
        source_dir = None
        if source_json_path:
            source_dir = str(Path(source_json_path).expanduser().resolve().parent)
        document = guide if isinstance(guide, WizardDocument) else WizardDocument.from_any(guide, source_dir=source_dir)

        if output_path is None:
            if source_json_path:
                destination = Path(source_json_path).expanduser().resolve().with_suffix(".pptx")
            else:
                destination = Path.cwd() / "disassembly_guide.pptx"
        else:
            destination = Path(output_path).expanduser().resolve()

        if destination.suffix.lower() != ".pptx":
            destination = destination.with_suffix(".pptx")
        result = engine.export(document, destination, options)
        return str(result)

    if not json_path:
        raise ValueError("Either 'json_path' or 'guide' must be provided.")

    source = Path(json_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve() if output_path else source.with_suffix(".pptx")
    if destination.suffix.lower() != ".pptx":
        destination = destination.with_suffix(".pptx")

    result, _ = engine.load_validate_export(
        source,
        destination,
        options,
        stop_on_error=True,
        depth=depth,
        include_bom=include_bom,
    )
    return str(result)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export Futurdata Wizard JSON to PPTX.")
    parser.add_argument("json_path")
    parser.add_argument("output_path", nargs="?")
    parser.add_argument("--start-step", type=int)
    parser.add_argument("--end-step", type=int)
    parser.add_argument("--max-action-groups", type=int)
    parser.add_argument("--groups-per-slide", type=int, default=1)
    parser.add_argument("--no-bom", action="store_true")
    parser.add_argument("--no-warnings", action="store_true")
    parser.add_argument("--no-images", action="store_true")
    args = parser.parse_args()

    print(export_to_pptx(
        args.json_path,
        args.output_path,
        start_step=args.start_step,
        end_step=args.end_step,
        max_action_groups=args.max_action_groups,
        groups_per_slide=args.groups_per_slide,
        include_bom=not args.no_bom,
        include_warnings=not args.no_warnings,
        include_images=not args.no_images,
    ))
