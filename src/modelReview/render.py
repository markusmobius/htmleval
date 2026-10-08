"""Render a review page as the text a model reviewer answers.

Unit of analysis: one call unit of one page -> one prompt (the filler slices a unit into several calls only when it
has more question rows than fit). A unit is a block carrying ``model.unit`` (its label); questions outside any unit
form one unit named "Page". The prompt states the unit's material (its ``model.text``, or a plain-text rendering of
its blocks), then a question list where each line gives the row id, the wording and the allowed values.

Nothing here reads HTML the metadata already replaces, and nothing hidden from people (``rowData``,
``correctValue(s)``) or marked ``audience: "human"`` is rendered.
"""
import random
import re

from ..json.model import QUESTION_BLOCKS, html_to_text, load, model_of, page_meta, page_questions

MODEL_PREAMBLE = "The material below is a plain-text version of the review form, followed by its questions."
QUESTIONS_HEAD = "Questions — answer each id with one of the values in brackets."
DEFAULT_UNIT = "Page"

_GENERIC = {"action", "yes", "no", "a", "an", "the"}


def _texts(value):
    """A ``model.text`` value as a list of lines (a string is split on newlines, a list is one entry per line)."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.split("\n")
    return [str(x) for x in value]


def instructions(block_json) -> list[str]:
    """The paragraphs of every block with ``model.role == "instructions"`` (its ``model.text``, or its content as
    plain text), in page order."""
    out = []

    def walk(node):
        if isinstance(node, list):
            for x in node:
                walk(x)
            return
        if not isinstance(node, dict):
            return
        m = model_of(node)
        if m.get("role") == "instructions":
            out.extend(_texts(m.get("text")) if m.get("text") is not None else block_text(node))
            return
        for k, v in node.items():
            if k != "model":
                walk(v)

    walk(load(block_json))
    return [p for p in out if str(p).strip()]


def system_text(block_json, system_head: str) -> str:
    """The system message: ``system_head``, the page's preamble (``model.page.preamble`` or the generic one) and the
    page's instructions."""
    page = page_meta(block_json) or {}
    paras = "\n".join(instructions(block_json))
    text = system_head + "\n\n" + (page.get("preamble") or MODEL_PREAMBLE)
    return text + ("\n\nTHE REVIEWER INSTRUCTIONS:\n" + paras if paras else "")


def block_text(node) -> list[str]:
    """One block's content as plain-text lines, for a block without ``model.text``: title and paragraphs (table
    rows as cells joined by " | ") of a text or thread block, the fragments of an interactive block, the HTML of a
    custom component. Question blocks render nothing (their rows are questions, listed separately). Children
    (threads, tabs, columns, fragments' blocks) are rendered by ``unit_material``, not here."""
    content = node.get("content")
    t = node.get("type")
    lines = []
    if t in ("text", "thread") and isinstance(content, dict):
        title = (content.get("title") or {}).get("text")
        if title:
            lines.append(html_to_text(title))
        body = content.get("body") or {}
        for item in body.get("text") or []:
            if isinstance(item, list):
                lines.append(" | ".join(html_to_text(c) for c in item))
            else:
                lines.extend(html_to_text(item).split("\n"))
    elif t == "custom_component" and isinstance(content, dict):
        title = (content.get("title") or {}).get("text")
        if title:
            lines.append(html_to_text(title))
        lines.extend(html_to_text(content.get("html")).split("\n"))
    return [ln for ln in lines if ln.strip()]


def unit_material(node) -> list[str]:
    """The material lines of a unit: its ``model.text`` when given, else the texts of its blocks in page order
    (blocks with ``audience: "human"`` and their subtrees skipped; instruction blocks skipped)."""
    m = model_of(node)
    if m.get("text") is not None:
        return _texts(m.get("text"))
    out = []

    def walk(n, top):
        if isinstance(n, list):
            for x in n:
                walk(x, False)
            return
        if not isinstance(n, dict):
            return
        mm = model_of(n)
        if mm.get("audience") == "human" or mm.get("role") == "instructions":
            return
        if "tabName" in n and "block" in n:
            out.append(f"Tab: {html_to_text(n['tabName'])}")
            walk(n["block"], False)
            return
        if "fragments" in n and isinstance(n.get("fragments"), list):          # an interactive paragraph
            for frag in n["fragments"]:
                if isinstance(frag, dict):
                    fm = model_of(frag)
                    out.extend(_texts(fm["text"]) if fm.get("text") is not None else html_to_text(frag.get("text")).split("\n"))
                    walk(frag.get("block"), False)
            return
        if not top and mm.get("unit") is not None:
            return                                                              # a nested unit renders itself
        if mm.get("text") is not None:
            out.extend(_texts(mm["text"]))
        elif n.get("type") in QUESTION_BLOCKS:
            pass
        elif n.get("type") is not None:
            out.extend(block_text(n))
        for k in ("content", "threads"):
            if k in n and n.get("type") not in QUESTION_BLOCKS:
                walk(n[k], False)

    walk(node, True)
    return [ln for ln in out if ln is not None]


def units(block_json) -> list[tuple[str, dict]]:
    """[(label, unit block)] in page order: every block with ``model.unit`` outside an ``audience: "human"`` subtree,
    plus ("Page", root) when some question belongs to no unit."""
    root = load(block_json)
    out = []

    def walk(n, hidden):
        if isinstance(n, list):
            for x in n:
                walk(x, hidden)
            return
        if not isinstance(n, dict):
            return
        m = model_of(n)
        hidden = hidden or m.get("audience") == "human"
        if m.get("unit") is not None:
            if not hidden:
                out.append((str(m["unit"]), n))
            return
        for k, v in n.items():
            if k != "model":
                walk(v, hidden)

    walk(root, False)
    if any(q["unit"] is None and not q["hidden"] and not q["skip"] for q in page_questions(root)):
        out.append((DEFAULT_UNIT, root))
    return out


def _options(options):
    """Allowed values, with the page's label only where it says more than the value itself."""
    parts = []
    for value, label in options:
        words = set(re.sub(r"\((?:grey|gray|yellow|green|red|blue)\)", "", label.lower()).replace("&mdash;", " ").split())
        words = {re.sub(r"[^a-z]", "", w) for w in words} - {""} - _GENERIC
        value_words = set(value.lower().split("_")) - _GENERIC
        parts.append(value if words <= value_words else f'{value} ("{re.sub("&mdash;", "—", label)}")')
    return " | ".join(parts)


def render_unit(block_json, label: str, unit_node=None, shuffle_seed=None):
    """(lines, rows) for one unit. ``lines`` is [(line, tag)] with tag None (material), a row dict (a question line)
    or ("group", [rows]) (an "About" line kept in a slice only with its questions). ``rows`` are the question dicts
    {row_id, question_id, key, options: {value: label}} in prompt order. ``shuffle_seed`` shuffles the order of the
    question groups (a replicate draw; the material is unchanged)."""
    root = load(block_json)
    if unit_node is None:
        unit_node = next((n for lab, n in units(root) if lab == label), None)
        if unit_node is None:
            raise KeyError(f"no unit labelled {label!r}")
    is_page = unit_node is root and label == DEFAULT_UNIT
    out = [(ln, None) for ln in unit_material(unit_node)]
    questions = [q for q in page_questions(root) if not q["hidden"] and not q["skip"]
                 and (q["unit"] is None if is_page else q["unit"] == label)]
    out.append((QUESTIONS_HEAD, None))
    seen_notes = []
    for q in questions:
        if q["note"] and q["note"] not in seen_notes:
            seen_notes.append(q["note"])
    out.extend((note, None) for note in seen_notes)
    groups, order = {}, []
    for q in questions:
        about = q["about"]
        if about not in groups:
            groups[about] = []
            order.append(about)
        groups[about].append(q)
    if shuffle_seed is not None:
        random.Random(shuffle_seed).shuffle(order)
    rows = []
    for about in order:
        grp = [{"row_id": str(q["row_id"]), "question_id": str(q["question_id"]), "key": q["key"],
                "options": {v: lab for v, lab in q["options"]}, "_q": q} for q in groups[about]]
        out.append(("", None))
        if about:
            out.append((about, ("group", grp)))
        for row in grp:
            q = row.pop("_q")
            allowed = q["options_text"] if q["options_text"] else _options(q["options"])
            out.append((f"{row['row_id']}: {q['text']} [{allowed}]", row))
            rows.append(row)
    return out, rows
