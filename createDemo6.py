"""Demo 6: Custom components (generic `custom_component` block + custom elements).

htmleval stays generic: the `custom_component` block just mounts author HTML, and
real behaviour lives in custom elements (Web Components) whose JS is inlined via
`addCustomElement`. Three tabs:

  Tab 1 "Basic"     — mount arbitrary HTML / inline SVG.
  Tab 2 "Zoomable"  — zoomable=True wraps raw SVG for wheel-zoom + drag-pan.
  Tab 3 "Signals"   — a tiny <demo-badge> custom element registered with
                      addCustomElement that SENDS signals on click and RECEIVES
                      them (highlighting) via the window.htmleval signal API.

Step 1: Run this script to create the review HTML file.
Step 2: Open __demo/demo6/review_reviewer1.html in a browser and try the tabs.
"""
import os

from src.reviewLib import Review, addCustomElement
from src.json.reviewJsonLib import ReviewJSON
from src.json.compoundBlocks.tabs import Tabs
from src.json.compoundBlocks.column import Column
from src.json.simpleBlocks.text import Text
from src.json.simpleBlocks.customComponent import CustomComponent


root = Tabs()
demo = ReviewJSON(root)

# ---------------------------------------------------------------------------
# Tab 1: Basic HTML / SVG mount
# ---------------------------------------------------------------------------
basic_html = """
<div style="max-width:540px;margin:0 auto;padding:16px;border:1px solid #ddd;border-radius:8px;background:#fff;">
  <h4 style="margin-top:0;">Hello from a custom component</h4>
  <p>The <code>custom_component</code> block mounts arbitrary author-provided HTML or SVG
  inside an evaluation, so you can drop in bespoke visualizations without writing a new
  block type.</p>
  <svg width="100%" height="60" viewBox="0 0 500 60" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="2" width="496" height="56" rx="8" fill="#eef2ff" stroke="#6366f1"/>
    <text x="250" y="36" text-anchor="middle" font-family="Arial" font-size="18" fill="#3730a3">Inline SVG works too</text>
  </svg>
</div>
"""
basic_col = Column()
basic_col.add_column([
    Text(title="Mount any HTML or SVG", titleSize=3,
         body=["A custom_component simply renders the markup you give it."]),
    CustomComponent(html=basic_html, title="Basic mount", titleSize=4),
])
root.add_tab(tabName="Basic", block=basic_col)

# ---------------------------------------------------------------------------
# Tab 2: Zoomable SVG (zoomable=True)
# ---------------------------------------------------------------------------
zoom_svg = """
<svg viewBox="0 0 400 300" width="400" height="300" xmlns="http://www.w3.org/2000/svg"
     style="display:block;margin:0 auto;background:#fafafa;">
  <circle cx="120" cy="150" r="70" fill="#fca5a5" stroke="#b91c1c" stroke-width="2"/>
  <rect x="210" y="90" width="120" height="120" rx="10" fill="#93c5fd" stroke="#1d4ed8" stroke-width="2"/>
  <text x="200" y="285" text-anchor="middle" font-family="Arial" font-size="14" fill="#555">scroll to zoom, drag to pan</text>
</svg>
"""
zoom_col = Column()
zoom_col.add_column([
    Text(title="Pan &amp; zoom", titleSize=3,
         body=["With <code>zoomable=True</code> the component wraps raw SVG so it gets "
               "mouse-wheel zoom and click-drag pan for free."]),
    CustomComponent(html=zoom_svg, title="Zoomable SVG", titleSize=4, zoomable=True),
])
root.add_tab(tabName="Zoomable", block=zoom_col)

# ---------------------------------------------------------------------------
# Tab 3: a custom element registered via addCustomElement, using the signal API
# ---------------------------------------------------------------------------
# htmleval has no knowledge of <demo-badge>; it only inlines this JS. The element
# talks to the eval purely through window.htmleval (emit / subscribe).
DEMO_BADGE_JS = r"""
class DemoBadge extends HTMLElement {
  connectedCallback() {
    this.attachShadow({ mode: "open" });
    var sig = this.getAttribute("signal");
    this.shadowRoot.innerHTML =
      '<style>.b{display:inline-block;padding:10px 16px;margin:4px;border:2px solid #7e22ce;' +
      'border-radius:10px;background:#e9d5ff;cursor:pointer;font:14px Arial;}' +
      '.b.on{background:#22c55e;color:#fff;border-color:#16a34a;}</style>' +
      '<span class="b">' + (this.getAttribute("label") || sig) + '</span>';
    var span = this.shadowRoot.querySelector(".b");
    span.addEventListener("click", function () { if (window.htmleval) window.htmleval.emit(sig); });
    if (window.htmleval) window.htmleval.subscribe(function (active) { span.classList.toggle("on", active === sig); });
  }
}
if (!customElements.get("demo-badge")) customElements.define("demo-badge", DemoBadge);
"""
addCustomElement("demo-badge", DEMO_BADGE_JS)

signal_html = (
    '<p>These <code>&lt;demo-badge&gt;</code> custom elements were registered with '
    '<code>addCustomElement</code>. Click one to <b>emit</b> its signal; every badge '
    '<b>receives</b> signals and highlights when its own is active.</p>'
    '<demo-badge signal="alpha" label="ALPHA"></demo-badge>'
    '<demo-badge signal="beta" label="BETA"></demo-badge>'
)

signal_col = Column()
signal_col.add_column([
    Text(title="Custom elements &amp; signals", titleSize=3,
         body=["htmleval stays generic: it only inlines the element JS via "
               "<code>addCustomElement</code>. The element interacts with the eval "
               "through the <code>window.htmleval</code> signal API (emit / subscribe)."]),
    CustomComponent(html=signal_html, title="Signal-wired custom elements", titleSize=4),
    Text(title="Emit 'alpha' from a text block", titleSize=4,
         body=["Clicking here emits <b>alpha</b> — watch the ALPHA badge highlight (if not already selected)."],
         signal="alpha"),
])
root.add_tab(tabName="Signals", block=signal_col)

# ---------------------------------------------------------------------------
# Generate JSON and create review
# ---------------------------------------------------------------------------
json_data = demo.get_json()
target_dir = os.path.join(".", "__demo", "demo6")
os.makedirs(target_dir, exist_ok=True)

with open(os.path.join(target_dir, "demo.json"), "w") as f:
    f.write(json_data)

review = Review(block=json_data, evalTitle="Custom Component Demo", serverURL="https://www.kv.econlabs.org/")
review.create(targetFolder=target_dir, defaults=None, reviewers=["reviewer1"])

print(f"Custom component demo created in {target_dir}")
print("Open review_reviewer1.html in a browser to try the Basic / Zoomable / Signals tabs.")
