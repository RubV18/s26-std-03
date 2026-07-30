from __future__ import annotations

import argparse
from pathlib import Path

from .engine import PPTXExportEngine
from .options import ExportOptions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transform a Futurdata Wizard JSON into an editable PPTX guide.")
    parser.add_argument("json_file", help="Input normalized Wizard JSON")
    parser.add_argument("output", nargs="?", help="Output .pptx path")
    parser.add_argument("--start-step", type=int)
    parser.add_argument("--end-step", type=int)
    parser.add_argument("--max-action-groups", type=int)
    parser.add_argument("--groups-per-slide", type=int, default=1, choices=range(1, 5))
    parser.add_argument("--bom-rows-per-slide", type=int, default=9)
    parser.add_argument("--no-title", action="store_true")
    parser.add_argument("--no-overview", action="store_true")
    parser.add_argument("--no-bom", action="store_true")
    parser.add_argument("--no-warnings", action="store_true")
    parser.add_argument("--no-tools", action="store_true")
    parser.add_argument("--no-safety", action="store_true")
    parser.add_argument("--no-details", action="store_true")
    parser.add_argument("--no-images", action="store_true")
    parser.add_argument("--no-closing", action="store_true")
    parser.add_argument("--allow-errors", action="store_true")
    parser.add_argument("--direct-json", action="store_true", help="Do not use disassembly_loader.build_guide even if available")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    source = Path(args.json_file)
    output = Path(args.output) if args.output else source.with_suffix(".pptx")
    options = ExportOptions(
        start_step=args.start_step,
        end_step=args.end_step,
        max_action_groups=args.max_action_groups,
        groups_per_slide=args.groups_per_slide,
        bom_rows_per_slide=args.bom_rows_per_slide,
        include_title=not args.no_title,
        include_overview=not args.no_overview,
        include_bom=not args.no_bom,
        include_warnings=not args.no_warnings,
        include_tools_summary=not args.no_tools,
        include_safety_summary=not args.no_safety,
        include_component_details=not args.no_details,
        include_images=not args.no_images,
        include_closing=not args.no_closing,
    )
    result, issues = PPTXExportEngine().load_validate_export(
        source,
        output,
        options,
        stop_on_error=not args.allow_errors,
        prefer_external_loader=not args.direct_json,
    )
    for issue in issues:
        print(issue)
    print(f"Created: {result}")


if __name__ == "__main__":
    main()
