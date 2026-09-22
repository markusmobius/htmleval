# LLM Export

`Review.export_llm_json(targetFolder, filename="eval_llm.json", keep_html=False)` writes the block tree
as plain JSON meant to be read by a language model instead of a browser. It is a second rendering of the
same tree `create()` inlines into the human page; nothing about the page changes.

```python
review = Review(block=json_data, evalTitle="My Demo", serverURL="https://www.kv.econlabs.org/")
review.create(targetFolder=folder, defaults=None, reviewers=["reviewer1"])
review.export_llm_json(folder)            # -> folder/eval_llm.json
```

## The key contract

Every question row in the export carries, per question, the exact variable key the page writes when a
reviewer answers it: `JSON.stringify([row_id, question_id])`, e.g. `["claim_2","fact_check"]`. A program
that answers rows and writes

```json
{"active": {}, "variables": {"[\"claim_2\",\"fact_check\"]": "false"}, "timestamps": {}}
```

to `closed_<reviewer>.json` (and registers the reviewer in `reviewer_ids.json`) produces a file that
`aggregate_closed_reviews` and `generate_summary` treat exactly like a downloaded human review. The key is
built by `llmExport.variable_key`, which mirrors the slot merge in `multiRowSelect.js` / `multiRowChecked.js`.

## Format (`"format": "htmleval-llm/1"`)

The tree is walked in render order. HTML is stripped to text (line breaks kept for `<br>`, `<p>`, `<li>`,
`<tr>`, headings). Node kinds:

| kind | fields |
|---|---|
| `tabs` | `tabs: [{name, block}]` |
| `column` | `columns: [[node, ...], ...]` — one list per side-by-side column |
| `text` | `title`, `text: [paragraph, ...]` or `table: [[cell, ...], ...]`, `highlight` |
| `thread` | as `text`, plus `threads: [node, ...]` |
| `interactive` | `paragraphs: [[{text, block}, ...], ...]` |
| `custom` | `title`, `text` (the mounted HTML stripped; markup and SVG are dropped) |
| `histogram` | `title` |
| `question` | `row_labels`, `questions: [{question_id, label, correct_value, options: [{value, label}]}]`, `rows: [{row_id, text, row_data, correct_values, keys: {question_id: key}}]`, `subjects` |

Every node also carries `signal` and `listeners`. `subjects` is the one resolved field: for a question
block revealed by a signal, the text of the blocks that emit that signal (usually the `Thread` the reviewer
clicks), so the model knows what a question is about without the exporter knowing what the page evaluates.

`keep_html=True` adds the raw `html` body next to `text` on text/thread nodes, for consumers that need an
attribute the stripping removes (e.g. a `title="..."` tooltip).

`llmExport.iter_questions(root)` yields every question node in render order.
