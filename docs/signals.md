# Signals & Listeners

The **signal** system lets blocks communicate with each other at runtime. A block
can *emit* a signal when the reviewer clicks it, and any other block can *listen*
for that signal and react — either by **highlighting** itself or by **showing/hiding**
itself. This is how you build linked menus, click-to-reveal content, and
cross-column interactions without writing any JavaScript.

Signals are a cross-cutting feature: almost every block accepts the same three
parameters.

## Parameters

| Parameter | Type | Description |
|---|---|---|
| `signal` | `str` | Name of the signal this block **emits** when clicked. |
| `listeners` | `list[str]` | Signal names this block **reacts** to. |
| `highlight` | `bool` | Reaction mode for listeners (see below). Defaults to `False`. |

Blocks that support these parameters include `Text`, `Thread`, `Column`, `Tabs`,
`Interactive`, `MultiRowChecked`, `MultiRowSelect`, and `CustomComponent`.

A single block can be **both** an emitter and a listener (e.g. a menu item that
highlights itself when clicked).

## Reaction modes

The `highlight` flag controls what happens when a listener's signal becomes active:

- **`highlight=True`** — the block toggles a `signal-highlight` CSS class while a
  matching signal is active. The block stays in place; only its styling changes.
- **`highlight=False`** (default) — the block is **shown only** while a matching
  signal is active and hidden otherwise. Use this for click-to-reveal content.

Only **one** signal is active at a time. Emitting a new signal replaces the
previously active one.

## Example: a linked menu

This mirrors `createDemo4.py`. Clicking a menu item on the left emits a signal;
the matching content block on the right becomes visible.

```python
from htmleval.json.simpleBlocks.text import Text

# Menu item: emits "A" and highlights itself while "A" is active.
menu_item = Text(
    title="Click Me for Info A", titleSize=4, body=["Emits Signal A"],
    signal="A", listeners=["A"], highlight=True,
)

# Content block: visible only while "A" is the active signal.
info_a = Text(
    title="Information A", titleSize=3,
    body=["This is the detail shown when A is signalled."],
    listeners=["A"],   # highlight defaults to False -> show/hide
)
```

Place the emitters and listeners in separate `Column` blocks to get a classic
menu-on-the-left, content-on-the-right layout.

## Signal-linked completion coloring

Threads (and other blocks) can be tinted green or red based on the completion of
question blocks that **share their signal name**, even when those questions live
in a different column. When every question linked to a signal is answered, the
linked element turns green (or red if a "No"-style answer was given). Untouched or
partially-answered groups receive no color, so nothing is highlighted by default.

This is what lets a `Thread` header reflect the state of its associated questions
located elsewhere in the layout (see [Compound Blocks](compound_blocks.md#thread)).

## Custom components and descendant-level signals

The `CustomComponent` block can opt into a descendant-level signal system via
`svg_signals=True`, wiring any element carrying `data-listeners` /
`data-questions` attributes into the same machinery. See
[Simple Blocks → CustomComponent](simple_blocks.md#customcomponent) for details
and `createDemo6.py` for a worked example.
