from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .engine import PPTXExportEngine
from .options import ExportOptions


class PPTXExporterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Futurdata JSON → PPTX Exporter")
        self.geometry("980x760")
        self.minsize(850, 660)
        self.engine = PPTXExportEngine()
        self.document = None

        self.json_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.max_groups_var = tk.StringVar()
        self.groups_var = tk.IntVar(value=1)
        self.bom_rows_var = tk.IntVar(value=9)

        self.title_var = tk.BooleanVar(value=True)
        self.overview_var = tk.BooleanVar(value=True)
        self.bom_var = tk.BooleanVar(value=True)
        self.warning_var = tk.BooleanVar(value=True)
        self.tools_var = tk.BooleanVar(value=True)
        self.safety_var = tk.BooleanVar(value=True)
        self.details_var = tk.BooleanVar(value=True)
        self.images_var = tk.BooleanVar(value=True)
        self.closing_var = tk.BooleanVar(value=True)

        self._build()

    def _build(self):
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Futurdata PPTX Exporter", font=("TkDefaultFont", 21, "bold")).pack(anchor="w")
        ttk.Label(root, text="PPTX-only thesis module with validation, range selection, grouping, BoM, tools and images.").pack(anchor="w", pady=(2, 14))

        files = ttk.LabelFrame(root, text="Files", padding=12)
        files.pack(fill="x")
        self._path_row(files, "Input JSON", self.json_var, self._choose_json, 0)
        self._path_row(files, "Output PPTX", self.output_var, self._choose_output, 1)

        range_frame = ttk.LabelFrame(root, text="Action-group selection", padding=12)
        range_frame.pack(fill="x", pady=(12, 0))
        fields = [
            ("First step", self.start_var, 0),
            ("Last step", self.end_var, 2),
            ("Maximum groups", self.max_groups_var, 4),
        ]
        for label, variable, column in fields:
            ttk.Label(range_frame, text=label).grid(row=0, column=column, sticky="w")
            ttk.Entry(range_frame, textvariable=variable, width=9).grid(row=0, column=column + 1, padx=(6, 18))
        ttk.Label(range_frame, text="Groups per slide").grid(row=0, column=6, sticky="w")
        ttk.Spinbox(range_frame, from_=1, to=4, textvariable=self.groups_var, width=6).grid(row=0, column=7, padx=(6, 18))
        ttk.Label(range_frame, text="BoM rows/slide").grid(row=0, column=8, sticky="w")
        ttk.Spinbox(range_frame, from_=5, to=12, textvariable=self.bom_rows_var, width=6).grid(row=0, column=9, padx=6)

        options = ttk.LabelFrame(root, text="PowerPoint contents", padding=12)
        options.pack(fill="x", pady=12)
        entries = [
            ("Title", self.title_var), ("Overview", self.overview_var), ("Warnings", self.warning_var),
            ("Bill of Materials", self.bom_var), ("Tools summary", self.tools_var), ("Safety summary", self.safety_var),
            ("Component details", self.details_var), ("Images", self.images_var), ("Closing slide", self.closing_var),
        ]
        for index, (label, variable) in enumerate(entries):
            ttk.Checkbutton(options, text=label, variable=variable).grid(row=index // 3, column=index % 3, sticky="w", padx=(0, 32), pady=4)

        actions = ttk.Frame(root)
        actions.pack(fill="x")
        ttk.Button(actions, text="Load and validate", command=self._validate).pack(side="left")
        ttk.Button(actions, text="Save settings", command=self._save_settings).pack(side="left", padx=8)
        ttk.Button(actions, text="Load settings", command=self._load_settings).pack(side="left")
        ttk.Button(actions, text="Generate PPTX", command=self._export).pack(side="right")

        self.log = tk.Text(root, height=22, wrap="word")
        self.log.pack(fill="both", expand=True, pady=(12, 0))
        self._log("Select the normalized Wizard JSON. The input file will be read-only.")

    def _path_row(self, parent, label, variable, command, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=8, pady=4)
        ttk.Button(parent, text="Browse", command=command).grid(row=row, column=2)
        parent.columnconfigure(1, weight=1)

    def _choose_json(self):
        value = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if value:
            self.json_var.set(value)
            if not self.output_var.get():
                self.output_var.set(str(Path(value).with_suffix(".pptx")))

    def _choose_output(self):
        value = filedialog.asksaveasfilename(defaultextension=".pptx", filetypes=[("PowerPoint", "*.pptx")])
        if value:
            self.output_var.set(value)

    def _log(self, value: str):
        self.log.insert("end", value + "\n")
        self.log.see("end")

    @staticmethod
    def _optional_int(value: str):
        return int(value) if value.strip() else None

    def _options(self) -> ExportOptions:
        return ExportOptions(
            start_step=self._optional_int(self.start_var.get()),
            end_step=self._optional_int(self.end_var.get()),
            max_action_groups=self._optional_int(self.max_groups_var.get()),
            groups_per_slide=self.groups_var.get(),
            bom_rows_per_slide=self.bom_rows_var.get(),
            include_title=self.title_var.get(),
            include_overview=self.overview_var.get(),
            include_warnings=self.warning_var.get(),
            include_bom=self.bom_var.get(),
            include_tools_summary=self.tools_var.get(),
            include_safety_summary=self.safety_var.get(),
            include_component_details=self.details_var.get(),
            include_images=self.images_var.get(),
            include_closing=self.closing_var.get(),
        ).normalized()

    def _apply_options(self, options: ExportOptions):
        self.start_var.set("" if options.start_step is None else str(options.start_step))
        self.end_var.set("" if options.end_step is None else str(options.end_step))
        self.max_groups_var.set("" if options.max_action_groups is None else str(options.max_action_groups))
        self.groups_var.set(options.groups_per_slide)
        self.bom_rows_var.set(options.bom_rows_per_slide)
        self.title_var.set(options.include_title)
        self.overview_var.set(options.include_overview)
        self.warning_var.set(options.include_warnings)
        self.bom_var.set(options.include_bom)
        self.tools_var.set(options.include_tools_summary)
        self.safety_var.set(options.include_safety_summary)
        self.details_var.set(options.include_component_details)
        self.images_var.set(options.include_images)
        self.closing_var.set(options.include_closing)

    def _validate(self):
        try:
            self.document = self.engine.load(self.json_var.get())
            issues = self.engine.validate(self.document)
            self.log.delete("1.0", "end")
            self._log(f"Product: {self.document.product.name}")
            self._log(f"Steps: {len(self.document.steps)}")
            self._log(f"BoM components: {len(self.document.bill_of_materials)}")
            self._log(f"Depth mode: {self.document.depth_mode}")
            self._log("")
            if issues:
                for issue in issues:
                    self._log(str(issue))
            else:
                self._log("No validation issues found.")
        except Exception as exc:
            messagebox.showerror("Validation failed", str(exc))

    def _save_settings(self):
        try:
            path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Export settings", "*.json")])
            if path:
                self._options().save(path)
                self._log(f"Saved settings: {path}")
        except Exception as exc:
            messagebox.showerror("Save settings failed", str(exc))

    def _load_settings(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("Export settings", "*.json")])
            if path:
                self._apply_options(ExportOptions.load(path))
                self._log(f"Loaded settings: {path}")
        except Exception as exc:
            messagebox.showerror("Load settings failed", str(exc))

    def _export(self):
        try:
            if self.document is None:
                self._validate()
            if self.document is None:
                return
            output = self.output_var.get().strip()
            if not output:
                raise ValueError("Choose an output PPTX file.")
            result = self.engine.export(self.document, output, self._options())
            self._log(f"Created: {result}")
            messagebox.showinfo("PowerPoint created", str(result))
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))


def main():
    PPTXExporterGUI().mainloop()


if __name__ == "__main__":
    main()
