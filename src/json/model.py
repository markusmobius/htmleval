"""The model-reviewer metadata of a review page.

Unit of analysis: one review page (a block tree, as ``ReviewJSON.get_json()`` serializes it). A page built for people
can also be answered by a language model when its blocks carry an optional ``model`` dict next to the content the
browser renders. The browser ignores that dict; the functions here read it. Nothing in it changes what a person sees.

What the metadata says, per level:
  any block        audience   "both" (default) | "human" (the block, its subtree and its questions are never sent to
                              the model) | "model" (text only the model sees; nothing is shown on the page)
                   text       str or [str]: the block's content as the model should read it, instead of a plain-text
                              rendering of its HTML (graphs, custom elements, layout-dependent phrasing)
                   unit       a label: this subtree is one call unit (one prompt); its questions belong to it
                   role       "instructions": the block's text goes into the system message, not into a unit
  question block   note       a paragraph printed once before this block's questions
  row              question   the question as the model should read it (row text is the item, not the question)
                   about      a pre-rendered string naming what the row is about; rows sharing it are grouped
                   options_text  replaces the "[allowed values]" bracket text; parsing still uses the real options
                   skip       true: never asked
  question         question   default wording for every row of that question (MultiRowSelectQuestion / MultiRowChecked)
  custom component questions  answers a custom element writes itself, declared so the model can give them:
                              [{row_id, question_id, question, options: [[value, label], ...], about?, options_text?}]
  root block       page       {"format": "htmleval-model/1", "task": str, "preamble": str}; a page is model-ready
                              exactly when its root carries this

The policy for anything not listed: ``rowData`` and ``correctValue(s)`` are never shown to the model.
"""
import copy
import html as html_lib
import json
import re
from collections import Counter

from .answerKeys import variable_key

PAGE_FORMAT = "htmleval-model/1"
QUESTION_BLOCKS = ("multi_row_select", "multi_row_checked")

_DROP_ELEMENTS = re.compile(r"<\s*(script|style|svg)\b.*?<\s*/\s*\1\s*>", re.IGNORECASE | re.DOTALL)
_BLOCK_BREAKS = re.compile(r"<\s*(br|/p|/li|/tr|/div|/h[1-6])\s*/?\s*>", re.IGNORECASE)
_ATTRS = r"""(?:[^>"']|"[^"]*"|'[^']*')*"""
_TAGS = re.compile(r"<" + _ATTRS + ">")


def html_to_text(text) -> str:
    """Page HTML as plain text: script/style/svg dropped whole, line-level tags become line breaks, other tags
    removed (quote-aware), entities decoded, spaces collapsed, blank lines collapsed."""
    if text is None:
        return ""
    s = _BLOCK_BREAKS.sub("\n", _DROP_ELEMENTS.sub(" ", str(text)))
    s = html_lib.unescape(_TAGS.sub("", s))
    s = "\n".join(re.sub(r"[ \t\r\f\v ]+", " ", line).strip() for line in s.split("\n"))
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def load(block_json):
    """The page as a dict, from the JSON string or an already-parsed dict."""
    return json.loads(block_json) if isinstance(block_json, str) else block_json


def model_of(node) -> dict:
    """The ``model`` dict of a block, row or question ({} when absent)."""
    m = node.get("model") if isinstance(node, dict) else None
    return m if isinstance(m, dict) else {}


def page_meta(block_json) -> dict | None:
    """The root's ``model.page`` dict, or None: the page was not built for a model reviewer."""
    page = model_of(load(block_json)).get("page")
    return page if isinstance(page, dict) else None


def _first(id_dict):
    if isinstance(id_dict, dict):
        return next(iter(id_dict.values()), "")
    return id_dict


def _options(options):
    """[[value, label], ...] from option objects ({label, value[, color]}) or already-paired lists."""
    out = []
    for o in options or []:
        if isinstance(o, dict):
            out.append([str(o.get("value", "")), str(o.get("label", ""))])
        elif isinstance(o, (list, tuple)) and len(o) == 2:
            out.append([str(o[0]), str(o[1])])
    return out


def page_questions(block_json) -> list[dict]:
    """Every question of a page in page order, with what the model needs to ask it:
    {row_id, question_id, key, text, options, about, options_text, skip, hidden, unit, note, row_data, block_type}.
    ``hidden`` is true under an ``audience: "human"`` block; ``unit`` is the nearest enclosing unit label (or None).
    Covers MultiRowSelect and MultiRowChecked rows anywhere in the tree and the answers a custom component declares."""
    out = []

    def entry(row_id, question_id, text, options, m_row, unit, hidden, note, row_data, block_type):
        out.append({
            "row_id": _first(row_id), "question_id": _first(question_id), "key": variable_key(row_id, question_id),
            "text": text, "options": options, "about": m_row.get("about"), "options_text": m_row.get("options_text"),
            "skip": bool(m_row.get("skip")), "hidden": hidden, "unit": unit, "note": note,
            "row_data": row_data or {}, "block_type": block_type,
        })

    def walk(node, unit, hidden):
        if isinstance(node, list):
            for x in node:
                walk(x, unit, hidden)
            return
        if not isinstance(node, dict):
            return
        m = model_of(node)
        hidden = hidden or m.get("audience") == "human"
        unit = m.get("unit", unit)
        t = node.get("type")
        content = node.get("content")
        if t in QUESTION_BLOCKS and isinstance(content, dict):
            if t == "multi_row_select":
                questions = [(q.get("id"), q.get("label") or "", model_of(q).get("question"), _options(q.get("options")))
                             for q in content.get("questions") or []]
            else:
                questions = [(content.get("id"), content.get("rowLabel") or "", m.get("question"), _options(content.get("options")))]
            for r in content.get("rows") or []:
                mr = model_of(r)
                for qid, label, q_wording, options in questions:
                    text = mr.get("question") or q_wording or label
                    entry(r.get("id"), qid, text, options, mr, unit, hidden, m.get("note"), r.get("rowData"), t)
            return
        if t == "custom_component":
            for q in m.get("questions") or []:
                entry(q.get("row_id"), q.get("question_id"), q.get("question") or "", _options(q.get("options")), q,
                      unit, hidden, m.get("note"), None, t)
            return
        for k, v in node.items():
            if k != "model":
                walk(v, unit, hidden)

    walk(load(block_json), None, False)
    return out


def strip_model(block_json):
    """A deep copy of the page without any ``model`` key: what the page would be if it had never carried metadata.
    Two pages that differ only in metadata compare equal after this (the byte gate for human pages)."""
    def strip(node):
        if isinstance(node, list):
            return [strip(x) for x in node]
        if isinstance(node, dict):
            return {k: strip(v) for k, v in node.items() if k != "model"}
        return node
    return strip(copy.deepcopy(load(block_json)))


def check_declared_keys(block_json) -> int:
    """Validate a page's questions; returns how many the model would be asked.
    Always: no two questions may share an answer key. On a model-ready page (root carries ``model.page``), every
    question the model will see must also have a wording and at least one option. Raises ValueError."""
    block = load(block_json)
    qs = page_questions(block)
    dups = sorted(k for k, n in Counter(q["key"] for q in qs).items() if n > 1)
    if dups:
        raise ValueError(f"duplicate answer keys: {len(dups)} {dups[:5]}")
    asked = [q for q in qs if not q["hidden"] and not q["skip"]]
    if page_meta(block) is None:
        return len(asked)
    bad = [q["key"] for q in asked if not str(q["text"]).strip() or not q["options"]]
    if bad:
        raise ValueError(f"{len(bad)} questions have no wording or no options for the model reviewer: {bad[:5]}")
    return len(asked)
