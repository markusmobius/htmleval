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
A generic host block that mounts author-provided HTML into the evaluation. The HTML may include **custom elements** (Web Components, e.g. `<lego-tree>`); htmleval has no knowledge of them — register their JavaScript with [`addCustomElement`](custom_elements.md) and the element handles its own rendering and signalling.
- **Usage**: Hosting a custom element, or dropping in a static diagram / SVG.
- **Properties**:
  - `html`: The HTML to mount (may contain custom-element tags).
  - `title` / `titleSize`: Optional heading above the mounted content.
  - `zoomable`: Convenience wrapper that gives raw SVG wheel-zoom and click-drag pan. Leave `False` for custom elements (they manage their own pan/zoom).
  - `signal` / `listeners` / `highlight`: Block-level signal wiring, shared with every other block (see [Signals & Listeners](signals.md)).
- **Note**: The block is non-interactive on its own (it reports 0/0 completion); any completion comes from the question blocks its components' signals are linked to.
- **Example**: `createDemo6.py` shows a basic mount, a `zoomable` SVG, and a `<demo-badge>` custom element registered with `addCustomElement`. See [Custom Elements](custom_elements.md).

## Signals on simple blocks
Every simple block accepts the shared `signal`, `listeners`, and `highlight` parameters for runtime interactivity. See [Signals & Listeners](signals.md) for the full model.
