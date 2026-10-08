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


def page_keys(block_json):
    """Every question of a block tree (the JSON ``ReviewJSON.get_json()`` returns, or the parsed dict), in page
    order: [{"row_id", "question_id", "key", "row_data"}]. Covers MultiRowSelect and MultiRowChecked blocks
    anywhere in the tree, including inside threads and clickable (Interactive) spans, and the answers a custom
    component declares in its ``model.questions`` (see ``htmleval.json.model``)."""
    from .model import page_questions
    return [{"row_id": q["row_id"], "question_id": q["question_id"], "key": q["key"], "row_data": q["row_data"]}
            for q in page_questions(block_json)]
