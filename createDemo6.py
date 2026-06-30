"""Demo 6: Custom component block (`custom_component`).

The custom_component block mounts author-provided HTML/SVG inside an evaluation
and opts in to shared htmleval behaviors instead of each visualization
re-implementing them. This demo shows its three modes across three tabs:

  Tab 1 "Basic"     — mount arbitrary HTML / inline SVG (no extra behavior).
  Tab 2 "Zoomable"  — zoomable=True wraps raw SVG so it gets wheel-zoom + drag-pan
                      (via build.js's initZoomableSVGs).
  Tab 3 "Signals"   — svg_signals=True wires descendants that carry:
                        * data-listeners="sig"          -> class "svg-sel" while
                          the matching signal is active (style it via CSS), and
                        * data-questions='[["row","q"]]' -> reveal a ".svg-tick"
                          child once every listed answer key is filled.

Step 1: Run this script to create the review HTML file.
Step 2: Open __demo/demo6/review_reviewer1.html in a browser:
        - Tab 2: scroll / drag the shapes to zoom and pan.
        - Tab 3: click Shape ALPHA to highlight it; click the "Highlight Shape
          BETA" text to highlight BETA; answer "Approve?" to reveal ALPHA's tick.
"""
import os
import json

from src.reviewLib import Review
from src.json.reviewJsonLib import ReviewJSON
from src.json.compoundBlocks.tabs import Tabs
from src.json.compoundBlocks.column import Column
from src.json.simpleBlocks.text import Text
from src.json.simpleBlocks.customComponent import CustomComponent
from src.json.simpleBlocks.multiRowSelect import MultiRowSelect, MultiRowSelectQuestion
from src.json.simpleBlocks.multiRowOption import MultiRowOption


def answer_key(row_id, question_id):
    """Storage key for a MultiRowSelect answer, matching JS JSON.stringify
    (no spaces) so it lines up with what data-questions expects."""
    return json.dumps([row_id, question_id], separators=(",", ":"))


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
# Tab 3: Signal highlighting + completion ticks (svg_signals=True)
# ---------------------------------------------------------------------------
alpha_key = answer_key("shape_alpha", "approve")
alpha_questions = json.dumps([alpha_key])  # value for the data-questions attribute

signal_svg = f"""
<svg viewBox="0 0 460 220" width="460" height="220" xmlns="http://www.w3.org/2000/svg"
     style="display:block;margin:0 auto;">
  <defs><style>
    g.svg-sel &gt; rect {{ stroke: #22c55e !important; stroke-width: 5 !important; }}
    g.svg-sel {{ filter: drop-shadow(0 0 10px rgba(34,197,94,0.8)); }}
  </style></defs>

  <!-- Shape ALPHA: emits + listens to its own 'alpha' signal (click to highlight),
       and reveals a green tick once its "Approve?" question is answered. -->
  <g onclick="emitSignal('alpha')" style="cursor:pointer"
     data-listeners="alpha" data-questions='{alpha_questions}'>
    <rect x="30" y="50" width="170" height="110" rx="10" fill="#e9d5ff" stroke="#7e22ce" stroke-width="2"/>
    <text x="115" y="103" text-anchor="middle" font-family="Arial" font-size="15" fill="#4c1d95">Shape ALPHA</text>
    <text x="115" y="126" text-anchor="middle" font-family="Arial" font-size="11" fill="#6b21a8">click me to highlight</text>
    <g class="svg-tick" style="display:none">
      <circle cx="185" cy="65" r="11" fill="#16a34a" stroke="#ffffff" stroke-width="1.5"/>
      <path d="M 180 65 L 184 69 L 191 60" stroke="#ffffff" stroke-width="2.5" fill="none"
            stroke-linecap="round" stroke-linejoin="round"/>
    </g>
  </g>

  <!-- Shape BETA: only listens to 'beta', emitted by the text block below. -->
  <g data-listeners="beta">
    <rect x="260" y="50" width="170" height="110" rx="10" fill="#cffafe" stroke="#0e7490" stroke-width="2"/>
    <text x="345" y="103" text-anchor="middle" font-family="Arial" font-size="15" fill="#155e75">Shape BETA</text>
    <text x="345" y="126" text-anchor="middle" font-family="Arial" font-size="11" fill="#0e7490">highlighted by the emitter</text>
  </g>
</svg>
"""

approve_q = MultiRowSelectQuestion(
    label="Approve?",
    id={1: "approve"},
    options=[
        MultiRowOption(label="Yes", value="yes", color="success"),
        MultiRowOption(label="No", value="no", color="danger"),
    ],
)
approve_table = MultiRowSelect(rowLabels=["Shape"], questions=[approve_q])
approve_table.add_row(["Shape ALPHA"], id={0: "shape_alpha"})

signal_col = Column()
signal_col.add_column([
    Text(title="Highlighting &amp; ticks", titleSize=3,
         body=["With <code>svg_signals=True</code>, elements opt in via "
               "<code>data-listeners</code> (highlight while a signal is active) and "
               "<code>data-questions</code> (show a tick once the listed answers are filled)."]),
    CustomComponent(html=signal_svg, title="Signal-wired SVG", titleSize=4, svg_signals=True),
    Text(title="Highlight Shape BETA", titleSize=4,
         body=["Click here to emit the <b>beta</b> signal and highlight Shape BETA above."],
         signal="beta"),
    Text(title="", body=["Answer below to reveal Shape ALPHA's completion tick:"]),
    approve_table,
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
