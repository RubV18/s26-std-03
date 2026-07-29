# HTML + JavaScript Disassembly Wizard Exporter

A Python-based exporter that converts a Loader Intermediate Representation (IR) JSON file into a self-contained interactive HTML disassembly guide.

The exporter is **product-independent**. The included Nespresso Essenza Mini guide is only an example. The same exporter can generate a guide for a washing machine, air fryer, laptop, printer, or another product, provided that the Loader produces an IR JSON file with the expected schema.

---
## Purpose

The purpose of this exporter is to transform the Loader Intermediate Representation (IR) into an interactive HTML disassembly guide.

The generated guide can be used by operators or technicians to follow a structured disassembly workflow, evaluate recovered components, and generate a final recovery report.

---

## 1. System Architecture

```text
Builder JSON
     ↓
Loader
     ↓
IR JSON
     ↓
HTML + JavaScript Exporter
     ↓
Interactive wizard.html
```

The exporter does **not** parse the original Builder model. It reads only the normalized IR JSON produced by the Loader.

---

## 2. Main Features

- Product welcome screen with product image and basic information
- Start button that opens the disassembly workflow
- Step-by-step wizard navigation
- Previous and Next buttons
- Sidebar with all disassembly steps
- Progress bar and current-step indicator
- Action instructions and required tools
- Main action image for each step
- Recovered output-component cards
- Quality grading for every recovered component:
  - Excellent
  - Working
  - Damaged
  - Scrap
- Optional measured-weight input
- Automatic session saving in the browser using `localStorage`
- Final recovery summary generated from the user's grades and measurements
- Automatic destination suggestion based on the selected grade
- Print / Save as PDF support
- Restart workflow option
- Responsive layout for desktop and smaller screens
- Automatic copying of referenced local images into the output folder
- Fallback display when an image is missing

### Supported Features

The generated HTML guide supports:

- Interactive step-by-step navigation
- Product-independent workflows
- Local and online images
- Progress tracking
- Component grading
- Weight recording
- Automatic recovery summary
- Browser session persistence using localStorage
- Responsive layout
- Print and PDF export

---

## 3. Requirements

No external Python packages are required.
The exporter relies only on the Python Standard Library.

---

## 4. Project Structure

```text
s26-std-03/
│
├── docs/
├── src/
│   ├── main/
│   │   ├── html-js-exporter/
│   │   │   ├── exporters/
│   │   │   ├── data/
│   │   │   ├── images/
│   │   │   ├── output/
│   │   │   ├── main.py
│   │   │   └── README.md
│   │   └── README.md
│   │
│   └── tests/
│
├── AUTHORS.md
├── LICENCE.md
└── README.md
```

### File responsibilities

- `main.py` — starts the export process and defines the input and output paths.
- `html_exporter.py` — loads the IR JSON, copies local images, and generates the HTML guide.
- `renderer.py` — renders the HTML sections.
- `styles.py` — contains the CSS styles.
- `scripts.py` — contains the JavaScript logic.
- `data/` — contains Loader-generated IR JSON examples.
- `images/` — contains local images referenced by the IR.
- `output/` — contains the generated HTML guide.

---

## 5. How to Run the Exporter

1. Open the exporter directory.

```powershell
cd src/main/html-js-exporter
```

2. Place a Loader-generated IR JSON file inside the `data` directory.

Example products included in this repository:

- Nespresso Essenza Mini
- Philips Air Fryer HD9252

3. Run the exporter.

```powershell
python main.py
```

4. Open the generated guide:

```text
output/wizard.html
```

The exporter automatically generates an interactive HTML disassembly guide from the selected Loader IR.

---

## 6. User Workflow

### 1. Welcome screen

The user first sees:

- Product name
- Product image
- Number of steps
- Number of recoverable components
- Product weight
- `Start disassembly` button

### 2. Disassembly steps

After pressing Start, the guide displays:

- Current step number
- Operation title
- Required tools
- Main action image
- Instructions
- Remaining assembly after the current step
- Components removed during the step

### 3. Component assessment

For every recovered component, the user can select:

- `Excellent` — component is in excellent condition and reusable
- `Working` — component functions correctly but may show normal wear
- `Damaged` — component is damaged or partially functional
- `Scrap` — component is unusable and should be recycled or disposed of

The user may also enter the measured component weight.

### 4. Final recovery summary

After the last step, the user can open the final summary. It includes:

- Component image
- Component name
- Material
- Nominal weight
- Measured weight
- Selected grade
- Suggested destination

The summary can be printed or saved as a PDF through the browser print dialog.

---
## 7. Using the Exporter with Another Product

The exporter is not limited to the included Nespresso example.

To generate a guide for another product:

1. Create the product model in the Builder.
2. Process the Builder JSON using the Loader.
3. Replace the existing:

```text
data/
    nespresso.json
    Air_fryer_Philips_HD9252.json
```

with the new Loader-generated IR JSON.

4. Replace or add the corresponding images inside the `images/` folder.

5. Run:

```powershell
python main.py
```

The exporter will automatically generate a new interactive HTML guide.

No changes to the Python source code, HTML templates, CSS, or JavaScript are required, provided that the Loader generates a valid IR JSON following the expected schema.

---


## 8. Expected IR Data

The exporter reads these main sections:

```json
{
  "schema_version": "1.0",
  "product": {},
  "depth": {},
  "steps": [],
  "warnings": [],
  "bill_of_materials": []
}
```

Each step can contain:

```json
{
  "index": 1,
  "operation": "Remove external components",
  "actions": [],
  "outputs": [],
  "continues_as": {},
  "tools_required": []
}
```

Important fields:

- `product.name` — displayed product name
- `product.image.path` — welcome-screen product image
- `steps[].operation` — step title
- `steps[].actions[].text` — instruction text
- `steps[].actions[].image.path` — action image
- `steps[].outputs[]` — components removed during the step
- `steps[].continues_as` — remaining assembly after the step
- `bill_of_materials[]` — all recovered components used in the final report

---

## 9. Local and URL Images

### Local image

```json
"image": {
  "path": "images/component.jpg",
  "is_url": false
}
```

The exporter copies this image to the output folder.

### Online image

```json
"image": {
  "path": "https://example.com/component.jpg",
  "is_url": true
}
```

Online images are referenced directly and are not copied.

For a completely offline guide, use local images.

---

## 10. Browser Session Storage

Grades, measured weights, and wizard progress are saved automatically in the browser using `localStorage`.

This means that refreshing the page does not immediately delete the user's assessment data.

The `Restart` button clears the saved session and returns to the welcome screen.

> Session data is saved only in the current browser and device. It is not uploaded to a server.

---

## 11. Print or Save the Final Report as PDF

1. Complete the steps.
2. Open the final summary.
3. Click `Print / Save PDF`.
4. Select `Save as PDF` in the browser print dialog.
5. Choose the destination and save the file.

---

## 12. Troubleshooting

### The HTML file is not generated

Make sure that:

- Python is installed
- The command is executed from the project root
- data/
    nespresso.json
    Air_fryer_Philips_HD9252.json
- The JSON syntax is valid

### An image is not displayed

Check that:

- The path in the IR JSON exactly matches the filename
- The file exists in the project folder
- Capitalization is correct
- Windows path separators are not used inside JSON image paths

Correct:

```text
images/water_tank.jpg
```

Avoid:

```text
images\water_tank.jpg
```

### Changes are not visible

Regenerate the guide:

```powershell
python main.py
```

Then refresh the browser with:

```text
Ctrl + F5
```

### The wrong product is displayed

Check the input file selected in `main.py`:

```python
ir_path="data/Nespresso.json"
```

### Old grades are still visible

Click `Restart`, or clear the browser's local site data for the HTML file.

### Browser shows an old version

If the browser still displays an older version of the guide:

- Regenerate the HTML guide.
- Refresh the browser using `Ctrl + F5`.
- If necessary, clear the browser cache.

---

## 13. Export Process Summary

```text
1. Create or obtain a product model
2. Run the Loader
3. Obtain the IR JSON
4. Add the referenced images
5. Replace the IR JSON in data/
    nespresso.json
    Air_fryer_Philips_HD9252.json
6. Run python main.py
7. Open output/wizard.html
8. Follow the disassembly steps
9. Grade and measure recovered components
10. View and print the final recovery report
```

---

## 14. Included Example Products

The repository includes two complete example products.

### Nespresso Essenza Mini

Features:

- 9 disassembly steps
- Local action images
- Component images
- Remaining assembly images
- Interactive grading
- Recovery summary

### Philips Air Fryer HD9252

Features:

- 16 disassembly steps
- Complete Loader-generated IR
- Local action images
- Component images
- Remaining assembly images
- Interactive grading
- Recovery summary

These examples demonstrate that the exporter is completely product-independent.

Any Builder model supported by the Loader can be exported without modifying the exporter source code.

---

## Repository Status

This repository contains the final implementation of the HTML + JavaScript exporter together with multiple example products demonstrating compatibility with the Loader Intermediate Representation.

The exporter has been successfully validated using:

- Nespresso Essenza Mini
- Philips Air Fryer HD9252

Both examples confirm that the exporter works with different products without requiring changes to the exporter implementation.