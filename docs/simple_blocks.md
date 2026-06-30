# Simple Blocks

Simple blocks are used for content display and data collection.

## Text
The `Text` block is the most basic block for displaying static content.
- **Usage**: Displaying instructions, articles, or context.
- **Properties**: Title, Body (list of strings/paragraphs).

## MultiRowOption
This is a helper class, not a standalone block, used to define the available choices for questions.
- **Properties**: Label (display text), Value (internal value), Color (visual hint like 'danger' or 'success').

## MultiRowChecked
A block that presents a list of "rows" (items), and for each row, a set of options that can be checked.
- **Usage**: "Check all that apply" style questions for multiple items.
- **Structure**:
  - `options`: A list of `MultiRowOption`.
  - rows are added via `.add_row()`.

## MultiRowSelect
A block that presents a list of "rows", and for each row, a set of specific questions answered via dropdowns or selections.
- **Usage**: When you need to ask multiple distinct questions (columns) for each item (row).
- **Structure**:
  - `questions`: A list of `MultiRowSelectQuestion`, each having its own `MultiRowOption` set.

## CustomComponent
A generic host block for mounting author-provided, pre-rendered HTML/SVG into the evaluation. It is the supported extension point for adding bespoke visualizations (e.g. an action graph) while staying inside the standard block pipeline.
- **Usage**: Embedding custom markup, diagrams, or interactive SVGs that opt into shared htmleval behaviors instead of re-implementing them.
- **Properties**:
  - `html`: The pre-rendered HTML/SVG string to mount.
  - `title` / `titleSize`: Optional heading above the mounted content.
  - `zoomable`: Wrap the content so it gains wheel-zoom and click-drag pan. Leave `False` if your `html` already provides its own `.zoomable-svg` wrapper (to avoid double-wrapping).
  - `svg_signals`: Wire descendant elements that carry `data-listeners` and/or `data-questions` attributes into htmleval's signal system and answer store:
    - `data-listeners="sigA sigB"` — the element gains the class `svg-sel` while a matching signal is active (style it via CSS).
    - `data-questions='[["row","q"], ...]'` — a descendant `.svg-tick` element is shown once every listed answer key is filled.
  - `signal` / `listeners` / `highlight`: Block-level signal wiring, shared with every other block (see [Signals & Listeners](signals.md)).
- **Note**: The block is non-interactive on its own (it reports 0/0 completion); any completion comes from the question blocks its signals are linked to.
- **Example**: `createDemo6.py` demonstrates all three modes across separate tabs — a basic HTML/SVG mount, a `zoomable` SVG, and an `svg_signals` SVG with highlighting and completion ticks.

## Signals on simple blocks
Every simple block accepts the shared `signal`, `listeners`, and `highlight` parameters for runtime interactivity. See [Signals & Listeners](signals.md) for the full model.
