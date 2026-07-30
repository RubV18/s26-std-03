from __future__ import annotations

from pathlib import Path

from .exporters.pptx_exporter import PPTXExporter
from .exporters.registry import ExporterRegistry
from .loader import load_document
from .models import WizardDocument
from .options import ExportOptions
from .validation import ValidationIssue, Validator


class PPTXExportEngine:
    """Coordinates loading, validation and PPTX rendering."""

    def __init__(self, exporter: PPTXExporter | None = None, validator: Validator | None = None):
        self.registry = ExporterRegistry()
        self.registry.register(exporter or PPTXExporter())
        self.validator = validator or Validator()

    def load(
        self,
        json_path: str | Path,
        *,
        prefer_external_loader: bool = True,
        depth=None,
        include_bom: bool = True,
    ) -> WizardDocument:
        return load_document(
            json_path,
            prefer_external_loader=prefer_external_loader,
            depth=depth,
            include_bom=include_bom,
        )

    def validate(self, document: WizardDocument) -> list[ValidationIssue]:
        return self.validator.validate(document)

    def export(
        self,
        document: WizardDocument,
        output_path: str | Path,
        options: ExportOptions | None = None,
    ) -> Path:
        exporter = self.registry.get("pptx")
        return exporter.export(document, Path(output_path), options or ExportOptions())

    def load_validate_export(
        self,
        json_path: str | Path,
        output_path: str | Path,
        options: ExportOptions | None = None,
        *,
        stop_on_error: bool = True,
        prefer_external_loader: bool = True,
        depth=None,
        include_bom: bool = True,
    ) -> tuple[Path, list[ValidationIssue]]:
        document = self.load(
            json_path,
            prefer_external_loader=prefer_external_loader,
            depth=depth,
            include_bom=include_bom,
        )
        issues = self.validate(document)
        if stop_on_error and any(issue.severity.lower() == "error" for issue in issues):
            details = "\n".join(str(issue) for issue in issues)
            raise ValueError(f"The JSON contains blocking validation errors:\n{details}")
        result = self.export(document, output_path, options)
        return result, issues
