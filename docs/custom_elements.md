# Custom Elements (Web Components)

htmleval lets you add bespoke, interactive visualizations as **custom elements**
(Web Components) without modifying htmleval itself. htmleval stays generic: it has
no knowledge of any specific element. You write a component as a single JavaScript
file, register it with `addCustomElement`, and use its tag inside any block's HTML.

This keeps concerns separated — you can develop and test a component in isolation,
then drop it into an evaluation.

## How it fits together

```
your_component.js   --addCustomElement(name, js)-->   inlined into every
(customElements.define)                                generated review HTML
        |                                                      |
        +-- talks to the eval only via window.htmleval  <------+
```

1. Write a custom element (`customElements.define("my-thing", …)`).
2. Register its JS: `addCustomElement("my-thing", js_code)`.
3. Put `<my-thing …></my-thing>` in any block's HTML (e.g. a `CustomComponent` or
   `Text` body).
4. `Review.create(...)` inlines the registered JS into the single self-contained
   review HTML. Nothing is shipped separately.

## Registering

```python
from htmleval.reviewLib import addCustomElement

with open("path/to/my_thing.js") as f:
    addCustomElement("my-thing", f.read())
```

Call it once before `Review.create(...)`. Every eval built afterwards inlines the
element's JS. htmleval never needs to change to support a new component.

## The signal contract: `window.htmleval`

A custom element interacts with the evaluation **only** through the global
`window.htmleval` object — the same signal bus the built-in blocks use:

| Method | Purpose |
|---|---|
| `window.htmleval.emit(signal)` | **Send** a signal (e.g. when the user clicks part of your component). |
| `window.htmleval.subscribe(handler)` | **Receive** signals: `handler(activeSignal)` is called on every emit (and after each answer save). Returns an unsubscribe function. |
| `window.htmleval.isAnswered(key)` | Returns `true` if the answer stored under `key` is filled — use it to reflect completion. |

This is the whole contract. Anything else (rendering, layout, styling) is up to
you. Because the built-in blocks emit/listen on the same bus, your element
interoperates with them: a `Text` span that emits `"x"` will reach your element's
`subscribe` handler, and a signal your element emits will highlight any block
listening for it.

## Writing a component

A minimal element that **sends** a signal on click and **receives** signals to
highlight itself:

```js
class MyThing extends HTMLElement {
  connectedCallback() {
    this.attachShadow({ mode: "open" });               // isolate styles
    const sig = this.getAttribute("signal");
    this.shadowRoot.innerHTML = '<button id="b">' + (this.getAttribute("label") || sig) + '</button>';
    const b = this.shadowRoot.getElementById("b");

    // SEND
    b.addEventListener("click", () => window.htmleval && window.htmleval.emit(sig));

    // RECEIVE
    if (window.htmleval) {
      window.htmleval.subscribe(active => b.classList.toggle("on", active === sig));
    }
  }
}
if (!customElements.get("my-thing")) customElements.define("my-thing", MyThing);
```

Notes:
- Custom-element tag names **must contain a hyphen** (`my-thing`, not `mything`).
- Guard on `window.htmleval` so the element still renders in a plain test page
  where the bus may be absent or mocked.
- Pass data via attributes (e.g. `data-... ='{"…":…}'` JSON) or properties.

## Testing in isolation

Ship a `test.html` next to each component that loads only the component and a
**mock** `window.htmleval`, then asserts that sending and receiving signals work.
This is a plain page, not an htmleval:

```html
<script>
  // mock bus
  window.htmleval = {
    _subs: [], emitted: [],
    emit(s) { this.emitted.push(s); this._subs.forEach(f => f(s)); },
    subscribe(f) { this._subs.push(f); return () => {}; },
    isAnswered() { return false; }
  };
</script>
<script src="./my_thing.js"></script>
<my-thing signal="x" label="X"></my-thing>
<!-- then assert: emit('x') highlights it; a click pushes 'x' to emitted -->
```

Open `test.html` in a real browser (loading a sibling `.js` over `file://` works
there; some sandboxed in-IDE previews block it).

## Example

`createDemo6.py` registers a small `<demo-badge>` element with `addCustomElement`
and shows it sending and receiving signals alongside the basic and zoomable
`CustomComponent` modes.
