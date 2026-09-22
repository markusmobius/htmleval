"""Export an htmleval block tree as JSON for a language-model reviewer.

Unit of analysis: one block tree (the same JSON ``Review`` inlines into the human page).

The human page is built by the JavaScript block classes from the block JSON; a language model
cannot use that rendering, so this module walks the same tree in the same order the browser
instantiates blocks and emits a plain structure: HTML stripped to text, layout kept as nested
tabs / columns / threads, and every question row carrying the exact variable key the page would
write for it. That key is the contract that lets a model-filled review be aggregated like a human
one: ``closed_<reviewer>.json`` holds ``{"variables": {key: value}}`` and ``Review.aggregate_closed_reviews``
parses the key back into ``[row_id, question_id]``.

Key construction mirrors ``multiRowSelect.js`` / ``multiRowChecked.js``: the row's ``id`` dict and the
question's ``id`` dict are merged by slot index into a list, then ``JSON.stringify``-ed. Python's
``json.dumps(..., separators=(",", ":"), ensure_ascii=False)`` produces the identical string.

The one resolution step performed here is ``subjects``: a question block that is revealed by a
signal (``listeners=[s]``) carries the text of the blocks that emit ``s`` (typically the Thread a
reviewer clicks to reveal the question), so the model sees what the question is about without
knowing anything about the evaluator that built the page. Nothing here is specific to any pipeline.
"""
import html
import json
import re

FORMAT = "htmleval-llm/1"

# Elements whose content is not prose: dropped whole (an inline SVG graph, a <style> or <script> block).
_DROP_ELEMENTS = re.compile(r"<\s*(script|style|svg)\b.*?<\s*/\s*\1\s*>", re.I | re.S)
_BLOCK_BREAKS = re.compile(r"<\s*(br|/p|/li|/tr|/div|/h[1-6])\s*/?\s*>", re.I)
# Inline formatting tags disappear without leaving a space ("<b>Action 3</b>:" -> "Action 3:");
# every other tag becomes a space so adjacent cells/blocks do not run together.
_INLINE_TAGS = re.compile(r"</?\s*(b|i|u|em|strong|span|a|code|small|sup|sub|mark|abbr)\b[^>]*>", re.I)
_TAGS = re.compile(r"<[^>]+>")
_SPACES = re.compile(r"[ \t\r\f\v ]+")
_BLANKS = re.compile(r"\n\s*\n+")


def strip_html(text):
    """HTML → plain text. script/style/svg elements are dropped whole; line-level breaks (br, p,
    li, tr, div, headings) become newlines so lists and tables stay readable; inline formatting
    tags vanish; runs of spaces collapse; entities are decoded."""
    if text is None:
        return ""
    s = _DROP_ELEMENTS.sub(" ", str(text))
    s = _BLOCK_BREAKS.sub("\n", s)
    s = _INLINE_TAGS.sub("", s)
    s = _TAGS.sub(" ", s)
    s = html.unescape(s)
    s = "\n".join(_SPACES.sub(" ", line).strip() for line in s.split("\n"))
    return _BLANKS.sub("\n", s).strip()


def variable_key(row_id, question_id):
    """The page's variable key for one (row, question): ``JSON.stringify([row_id, question_id])``.

    ``row_id`` / ``question_id`` are the ``id`` dicts ({slot: value}) the Python blocks store; the
    browser merges them by slot into one array. Passing plain strings uses slots 0 and 1."""
    slots = {}
    for part, default_slot in ((row_id, 0), (question_id, 1)):
        if isinstance(part, dict):
            for k, v in part.items():
                slots[int(k)] = v
        else:
            slots[default_slot] = part
    full = [""] * (max(slots) + 1)
    for k, v in slots.items():
        full[k] = v
    return json.dumps(full, separators=(",", ":"), ensure_ascii=False)


def _first_id(id_dict):
    if isinstance(id_dict, dict):
        return list(id_dict.values())[0] if id_dict else ""
    return id_dict


def _title(content):
    t = content.get("title") if isinstance(content, dict) else None
    if isinstance(t, dict):
        return strip_html(t.get("text", "")) or None
    if isinstance(t, str):
        return strip_html(t) or None
    return None


def _body(content):
    """Return (text_paragraphs, table_rows). A Text block body is either a list of paragraphs or,
    with ``is_table``, a list of rows (each a list of cells or a single string)."""
    b = content.get("body") if isinstance(content, dict) else None
    if not b:
        return [], None
    rows = b.get("text") if isinstance(b, dict) else b
    rows = rows if isinstance(rows, list) else [rows]
    if isinstance(b, dict) and b.get("is_table"):
        table = [[strip_html(c) for c in r] if isinstance(r, list) else [strip_html(r)] for r in rows]
        return [], table
    return [strip_html(p) for p in rows if strip_html(p)], None


def _raw_body(content):
    b = content.get("body") if isinstance(content, dict) else None
    if not b:
        return None
    rows = b.get("text") if isinstance(b, dict) else b
    return rows if isinstance(rows, list) else [rows]


class _Exporter:
    def __init__(self, keep_html):
        self.keep_html = keep_html
        self.emitters = {}   # signal -> [summary dict]

    # -- pass 1: index every block that emits a signal -----------------------------------------
    def index(self, block):
        if isinstance(block, dict):
            sig = block.get("signal")
            if sig and isinstance(block.get("type"), str):
                self.emitters.setdefault(sig, []).append(self._summary(block))
            for v in block.values():
                self.index(v)
        elif isinstance(block, list):
            for x in block:
                self.index(x)

    def _summary(self, block):
        content = block.get("content")
        out = {"signal": block.get("signal"), "kind": block.get("type")}
        if isinstance(content, dict):
            out["title"] = _title(content)
            text, table = _body(content)
            out["text"] = text if text else ([" | ".join(r) for r in table] if table else [])
            if self.keep_html and _raw_body(content) is not None:
                out["html"] = _raw_body(content)
        return out

    # -- pass 2: convert in render order -------------------------------------------------------
    def node(self, block):
        if not isinstance(block, dict):
            return {"kind": "unknown"}
        t = block.get("type")
        content = block.get("content")
        base = {"kind": t, "signal": block.get("signal"), "listeners": list(block.get("listeners") or [])}
        if t == "tabs":
            base["tabs"] = [{"name": strip_html(tab.get("tabName", "")), "block": self.node(tab.get("block"))}
                            for tab in (content or [])]
        elif t == "column":
            base["columns"] = [[self.node(b) for b in col] for col in (content or [])]
        elif t in ("text", "thread"):
            base["highlight"] = bool((content or {}).get("highlight"))
            base["title"] = _title(content or {})
            text, table = _body(content or {})
            base["text"] = text
            if table is not None:
                base["table"] = table
            if self.keep_html and _raw_body(content or {}) is not None:
                base["html"] = _raw_body(content or {})
            if t == "thread":
                base["threads"] = [self.node(b) for b in (block.get("threads") or [])]
        elif t == "interactive":
            base["paragraphs"] = [[{"text": strip_html(f.get("text", "")), "block": self.node(f.get("block"))}
                                   for f in (p.get("fragments") or [])] for p in (content or [])]
        elif t == "custom_component":
            base["title"] = _title(content or {})
            base["text"] = strip_html((content or {}).get("html", ""))
        elif t == "histogram":
            base["title"] = _title(content or {})
        elif t in ("multi_row_select", "multi_row_checked"):
            base = self.question(block, base)
        return base

    def question(self, block, base):
        content = block.get("content") or {}
        base["kind"] = "question"
        base["highlight"] = bool(content.get("highlight"))
        if block.get("type") == "multi_row_select":
            base["row_labels"] = [strip_html(x) for x in (content.get("rowLabels") or [])]
            questions = content.get("questions") or []
        else:
            base["row_labels"] = [strip_html(content.get("rowLabel", ""))]
            questions = [{"label": "", "id": content.get("id"), "options": content.get("options") or [],
                          "correctValue": content.get("correctValue")}]
        base["questions"] = [{
            "question_id": _first_id(q.get("id")),
            "label": strip_html(q.get("label", "")),
            "correct_value": q.get("correctValue"),
            "options": [{"value": o.get("value"), "label": strip_html(o.get("label", ""))}
                        for o in (q.get("options") or [])],
        } for q in questions]
        rows = []
        for r in content.get("rows") or []:
            text = r.get("text")
            text = text if isinstance(text, list) else [text]
            rows.append({
                "row_id": _first_id(r.get("id")),
                "text": [strip_html(x) for x in text],
                "row_data": r.get("rowData") or {},
                "correct_values": r.get("correctValues"),
                "keys": {_first_id(q.get("id")): variable_key(r.get("id"), q.get("id")) for q in questions},
            })
        base["rows"] = rows
        base["subjects"] = [s for sig in base["listeners"] for s in self.emitters.get(sig, [])]
        return base


def to_llm_json(block_json, keep_html=False):
    """Convert a block tree (the JSON string ``ReviewJSON.get_json()`` returns, or the parsed
    dict) into the LLM export structure. Pure: no files, no network."""
    block = json.loads(block_json) if isinstance(block_json, str) else block_json
    ex = _Exporter(keep_html)
    ex.index(block)
    return {"format": FORMAT, "root": ex.node(block)}


def iter_questions(node):
    """Yield every question node in render order (helper for consumers)."""
    if not isinstance(node, dict):
        return
    if node.get("kind") == "question":
        yield node
        return
    for tab in node.get("tabs") or []:
        yield from iter_questions(tab.get("block"))
    for col in node.get("columns") or []:
        for b in col:
            yield from iter_questions(b)
    for b in node.get("threads") or []:
        yield from iter_questions(b)
    for para in node.get("paragraphs") or []:
        for f in para:
            yield from iter_questions(f.get("block"))
