# Disassembly Wizard — Load Phase (`disassembly_loader`)

This package is the **load phase** of the Disassembly Wizard. It reads a Builder
JSON model of a product's disassembly graph and produces a **linearized guide**:
an ordered list of disassembly steps, ready for an output generator (PDF, TXT,
MD, HTML+JS, PPTX, DOCX, VIDEO) to render.

You do **not** receive the raw graph. You receive a guide that has already been
traversed, validated, and ordered for you. Iterate the steps and render them —
no graph logic on your side.

The formal output contract is `disassembly_loader/ir_schema.json` (JSON Schema,
Draft 2020-12). This README is the practical guide; the schema is the authority.
Two real, ready-to-inspect outputs live in `disassembly_loader/examples/`:
`example_bialetti_ir.json` (a clean model — all weights, no warnings) and
`example_airfryer_ir.json` (a richer model — output branching, operations with no
instructions, a mass-balance advisory). Read them alongside the schema to see the
shape on real data.

---

## Install

Plain Python (3.10+). Copy the `disassembly_loader/` folder into your project or
put it on your `PYTHONPATH`. No runtime dependencies. (Tests use `pytest` and
`jsonschema`.)

---

## Two entry points

### As a Python object — `build_guide`

For Python generators. Returns a typed `Guide` you iterate directly.

```python
from disassembly_loader import build_guide

guide = build_guide("models/BialettiGioia.json")
for step in guide.steps:
    print(step.index, step.operation)
    for action in step.actions:      # ordered "how-to" instructions
        print("   -", action.text)
    for part in step.outputs:        # parts obtained
        print("   =>", part.name)
```

### As a JSON file — `build_ir_file`

For non-Python generators (HTML+JS, VIDEO) or any file-based toolchain.

```python
from disassembly_loader import build_ir_file
build_ir_file("models/BialettiGioia.json", "out/ir.json")
```

```javascript
const ir = await fetch("ir.json").then(r => r.json());
ir.steps.forEach(s => console.log(s.index, s.operation));
```

Both doors produce the **same IR**, described by `ir_schema.json`.

### Options (both entry points)

| Option        | Default | Meaning                                                          |
|---------------|---------|------------------------------------------------------------------|
| `depth`       | full    | How deep to disassemble (see `DepthSpec` below).                 |
| `include_bom` | `False` | If `True`, fill `bill_of_materials` with the final leaf parts.   |
| `traversal`   | strict  | Anomaly handling. `LENIENT` is reserved, not yet implemented.    |

```python
from disassembly_loader import build_guide, DepthSpec, DepthMode

build_guide(path, depth=DepthSpec(mode=DepthMode.FULL))          # everything
build_guide(path, depth=DepthSpec(mode=DepthMode.KEEP_MAIN))     # main assemblies whole
build_guide(path, depth=DepthSpec(mode=DepthMode.MANUAL, keep_whole_ids=(12, 17)))
```

The IR schema is identical under every depth — only the number of steps changes.

---

## How an input model must be built

This section is for whoever authors the graph (the Builder GUI). A model is a
directed graph of shapes. Three node types matter, with distinct roles:

- **Component** — a part: the whole product (the root), an intermediate
  sub-assembly, or a final leaf part.
- **Diamond** — an *operation* (e.g. "remove the cover"): one disassembly action
  that produces parts.
- **Action** — a single micro-instruction describing *how* to perform an
  operation (e.g. "unscrew the 4 screws").

**The grammar (how to wire them):**

1. **One root.** Exactly one component has no incoming edge and starts the
   disassembly. A node with no edges at all is an orphan (ignored), not a root.
2. **A composite continues into exactly one operation.** A component that is not
   yet fully taken apart leads to **one** diamond. Extract one part; the rest
   continues to the next single operation, forming a chain — never two diamonds
   off the same component, and never a component or an action directly: a
   component -> component or component -> action edge is invalid — the loader
   does not traverse it, and everything reachable only through it is absent
   from the guide (reported as an `error` finding).
3. **An operation produces one or more components.** A diamond's component
   outputs are the parts obtained. Any number may be final leaves; one *or more*
   may themselves continue into further operations (the disassembly may branch
   here — several sub-assemblies each taken apart along their own path). An
   operation NEVER connects directly to another operation: continuation always
   passes through a component. A diamond -> diamond edge is invalid — the loader
   does not traverse it, and everything reachable only through it is absent from
   the guide (reported as an `error` finding).
4. **An operation's instructions are optional.** A diamond may carry action
   nodes describing how it is performed, laid out either as a **chain**
   (action -> action -> ...) or as a **fan-out** (several actions directly under
   the diamond). Both are accepted; you always get them all, in order. An
   operation whose name is self-explanatory ("unscrew 4 screws") may have **no**
   actions.
5. **An action is a single step.** At most one predecessor and one successor when
   chained.

Weights, materials, colors, and images on components are optional. Weights, when
present on every part, are checked to sum to the product weight.

**Validation is permissive.** A model that breaks these rules still produces a
guide on a best-effort basis; the problems come back as `warnings` (see below),
never as a refusal. Only a file that cannot be parsed as a graph at all is
rejected (see Errors).

---

## What the IR looks like

Top level:

```
schema_version    : str          contract version ("1.1")
product           : Component    the whole product (the root)
depth             : object       which depth was applied
tools             : [str]        every tool used across the guide (deduplicated)
steps             : [Step]       the operations, in order   <-- iterate this
warnings          : [Warning]    validation findings
bill_of_materials : [Component] | null   final leaf parts, or null if not requested
```

`tools` is the union of every step's `tools_required` — render it at the top of
your output next to the bill of materials; you never need to recompute it.

A **Step** (one operation):

```
index          : int             1-based order
operation      : str             the operation name
input          : Component       the piece this operation is performed ON
actions        : [Action]        ordered instructions (may be empty)
outputs        : [Component]     the final parts extracted here (leaves)
continues_as   : [Component]     the pieces that continue (empty if none does)
tools_required : [str]           tools used across this step (deduplicated)
```

**Narrating a step:** take `input`, perform `operation` (following `actions`),
obtain `outputs`; each entry of `continues_as` is opened by a LATER step — the
one whose `input.node_id` matches. A disassembly may branch (several
sub-assemblies each taken apart along their own path), so do not assume the
next step in the list continues the current one: steps are ordered depth-first
(one branch completed before the next), and the `input` field is the reliable
link. An empty `continues_as` means this branch is finished — it does NOT mean
the guide is over.

**Worked example — how graph roles land in a Step.** Given this fragment of a
model (a component entering an operation, with two instructions, one extracted
part and one part that continues):

```
                       Coffee machine (id 1)
                              |
              Remove the outer shell (diamond, id 2)
              /        |             \
  action id 10     Outer shell     Chassis
  "Unscrew the      (id 3,          (id 4, continues into
   4 rear screws"    a leaf)         "Extract the pump", id 5)
      |
  action id 11
  "Slide the shell upwards"
```

the loader emits (trimmed of the always-present null fields for readability):

```json
{
  "index": 1,
  "operation": "Remove the outer shell",
  "input":        { "node_id": 1, "name": "Coffee machine" },
  "actions": [
    { "text": "Unscrew the 4 rear screws", "tools": "Phillips PH1" },
    { "text": "Slide the shell upwards",   "tools": "Hands" }
  ],
  "outputs":      [ { "node_id": 3, "name": "Outer shell" } ],
  "continues_as": [ { "node_id": 4, "name": "Chassis" } ],
  "tools_required": [ "Phillips PH1", "Hands" ]
}
```

The mapping to remember:

| Graph node | Becomes, in the IR |
|---|---|
| a **diamond** | one **Step** (its label is `operation`) |
| the **component entering** the diamond | that step's `input` |
| component children that do **not** continue (leaves) | `outputs` |
| component children that **do** continue | `continues_as` — and each one is the `input` of a later step |
| the diamond's **action** nodes | `actions`, in order (their tools, split and de-duplicated, feed `tools_required`) |

Here the Chassis (id 4) reappears as `"input": { "node_id": 4, ... }` of step 2
("Extract the pump") — that `node_id` match, not list adjacency, is how the
steps chain together.

An **Action** has `text`, `tools`, `image`. A **Component** has `name`, `weight`,
`weight_unit`, `material`, `color`, `image`, plus `kept_whole` and
`contained_leaf_count` (for depth cuts).

**Optional fields are always present**, set to `null` when empty — never omitted.
So `action.image` is an image object or `null`, never missing.

**Images:** `image` is `null` or `{ "path": "...", "is_url": true|false }`. Use
`is_url` to decide whether to fetch a URL or load a local/relative path. The path
is passed through unchanged.

**Kept-whole blocks:** under a depth cut, a sub-assembly kept intact appears in
`outputs` with `kept_whole: true` and `contained_leaf_count` (parts hidden
inside).

---

## Warnings

The loader never refuses a flawed model; it produces the guide plus `warnings`
explaining every problem. Each warning:

```
rule      : str   which check fired
severity  : "info" | "warning" | "error"
message   : str   human-readable explanation
node_ids  : [int] the source node(s) concerned
```

**All severities are non-blocking.** `error` = a serious problem, `warning` = a
real anomaly (e.g. a cycle), `info` = an advisory (e.g. weights missing, so mass
balance was not checked; or a diamond using the fan-out layout). A guide may be
**empty** if the model is too malformed to linearize — the warnings explain why;
an empty guide is not a crash.

---

## Errors

The loader raises only `UnparsableModelError`, and only when the input cannot be
read as a model at all (corrupt JSON, missing `shapes`). A valid-but-flawed model
becomes warnings, never an exception.

```python
from disassembly_loader import build_guide, UnparsableModelError
try:
    guide = build_guide(path)
except UnparsableModelError as e:
    print("Could not read the model:", e)
```

---

## Guarantees

- **Read-only.** The source model is never modified.
- **Stable contract.** The IR shape is described by `ir_schema.json` and
  versioned by `schema_version`; it will not change shape without a version bump.
- **Deterministic.** The same model and options always produce the same guide.