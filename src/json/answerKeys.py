"""Answer keys: the variable key a review page saves for each (row, question).

The page's JavaScript (``multiRowSelect.js`` / ``multiRowChecked.js``) merges a row's ``id`` dict and a question's
``id`` dict by slot index into a list and saves the answer under ``JSON.stringify(list)``. Anything that writes answers
for a page outside the browser -- e.g. a program filling a review -- must use the same key, or
``Review.aggregate_closed_reviews`` will not match its answers to the page's questions.

``variable_key`` reproduces that string; ``page_keys`` lists every question of a block tree with its key.
"""
import json


def variable_key(row_id, question_id):
    """The page's variable key for one (row, question): ``JSON.stringify([row_id, question_id])``.

    ``row_id`` / ``question_id`` are the ``id`` dicts ({slot: value}) the Python blocks store; the browser merges
    them by slot into one array. Plain strings use slots 0 and 1."""
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


def _first(id_dict):
    if isinstance(id_dict, dict):
        return next(iter(id_dict.values()), "")
    return id_dict


def page_keys(block_json):
    """Every question of a block tree (the JSON ``ReviewJSON.get_json()`` returns, or the parsed dict), in page
    order: [{"row_id", "question_id", "key", "row_data"}]. Covers MultiRowSelect and MultiRowChecked blocks
    anywhere in the tree, including inside threads and clickable (Interactive) spans."""
    block = json.loads(block_json) if isinstance(block_json, str) else block_json
    out = []

    def walk(node):
        if isinstance(node, list):
            for x in node:
                walk(x)
            return
        if not isinstance(node, dict):
            return
        t = node.get("type")
        content = node.get("content")
        if t in ("multi_row_select", "multi_row_checked") and isinstance(content, dict):
            if t == "multi_row_select":
                questions = [q.get("id") for q in content.get("questions") or []]
            else:
                questions = [content.get("id")]
            for r in content.get("rows") or []:
                for qid in questions:
                    out.append({"row_id": _first(r.get("id")), "question_id": _first(qid),
                                "key": variable_key(r.get("id"), qid), "row_data": r.get("rowData") or {}})
            return
        for v in node.values():
            walk(v)

    walk(block)
    return out
