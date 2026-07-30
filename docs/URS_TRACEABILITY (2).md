# URS Traceability — PPTX Thesis Module

| URS ID | Status in this repository | Implementation |
|---|---|---|
| FR 1.0 | Implemented | Tkinter JSON file picker and CLI input. |
| FR 1.1 | Implemented for the normalized Wizard JSON | `WizardDocument`, `Step`, `Action`, and `Component` objects. Original Builder `shapes/connections` parsing remains in the upstream loader. |
| FR 1.2 / NFR 2.1 | Implemented | Input is opened read-only; no write is performed on the source JSON. |
| FR 1.3 | Implemented | Overview, tools/safety preparation slide and paginated Bill of Materials appear before steps. |
| FR 2.0–2.3 | Partially upstream, fully surfaced | Structural validation of the normalized guide is implemented; authoritative graph/topology warnings from the Builder/loader are imported and exported. Proceeding despite warnings is possible with `--allow-errors`; errors block by default. |
| FR 2.4 | Implemented when weights and a source are available | Product/BOM and per-step mass-balance rules. |
| FR 3.0 | Consumed | The selected depth and keep-whole IDs in the Wizard JSON are displayed and respected. Depth selection itself belongs to the upstream Wizard. |
| FR 4.0 | Implemented | Weight, measured weight, material, color, grading/quality and destination are supported when present. |
| FR 4.1 | Implemented | Parent operation, atomic action text, outputs, continuation and local/data-URI images are exported. |
| FR 5.0–5.2 | Consumed | Quality, destination and measured weight are exported when collected by the Wizard. Data entry is not performed inside the exporter. |
| FR 6.2 | Implemented by output format | All generated PowerPoint text, images, tables and shapes remain editable. |
| FR 8.0 | Implemented for export configuration | GUI export settings can be saved and loaded. The execution session itself is preserved in the input Wizard JSON. |
| FR 9.0 | Implemented where data exists | Aggregated tools and safety notices slide. |
| FR 10.0 | Implemented | Atomic actions are grouped below their parent diamond/operation. |
| FR 11.0 | Implemented architecturally | Generic `Exporter` interface and `ExporterRegistry`; this repository registers only PPTX. |
| FR 17.0 | Implemented | Editable PowerPoint 2007+ `.pptx` generated with `python-pptx`. |
| FR 19.0 | Implemented | First/last step, maximum action-group count, groups per slide and BoM rows per slide. |
| NFR 1.0–1.1 | Implemented | Non-programmer GUI and localized warning messages. |
| NFR 1.2 | Implemented | JSON nodes are converted into Python objects. |
| NFR 2.0 | Implemented for the provided normalized schema | Direct parser plus compatibility with `disassembly_loader.build_guide`. |
| NFR 3.0 | Implemented | Python/Tk application. |
| NFR 3.1 | Implemented | Validator rules can be registered dynamically. |
| NFR 4.0 | Implemented for typical models | Parsing/validation/export are synchronous and suitable for interactive use; tests cover the provided 16-step model. |

## Upstream boundary

The supplied JSON is an **ordered Wizard guide**, not the original Builder graph. It does not include `shapes` and `connections`, so cycles, orphan nodes, multiple roots and exact branch-parent relations cannot be reconstructed inside the PPTX exporter alone. The module preserves and displays those warnings when they are produced by the upstream loader.

For exact branch continuity, add a `source` object to every step that starts a new branch. The exporter deliberately reports an unspecified source rather than inventing a false relationship.
