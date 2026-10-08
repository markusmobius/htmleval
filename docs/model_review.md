# Model review: a page answered by a language model

Any review page built with htmleval can be filled by a language model as if it were one more reviewer. The page
carries a little metadata next to the content people see; htmleval renders the page into prompts from that
metadata, asks a model, and stores the answers exactly as the browser stores a person's (same answer keys, same
`closed_<reviewer>.json`, same server slot), so `close_eval`, `aggregate_closed_reviews` and `generate_summary`
treat the model like anyone else.

Nothing in the metadata changes what a person sees: the browser ignores it.

## The `model` metadata

Every block, question row, question and interactive fragment accepts `model=` (a dict). It is serialized into the
page JSON only when given, so pages built without it are byte-identical to before.

| Level | Key | Meaning |
|---|---|---|
| any block | `audience` | `"both"` (default); `"human"`: the block, its subtree and its questions are never sent to the model. The page always renders a block's content; text meant for the model alone goes in `text` |
| any block | `text` | `str` or `[str]`: the block's content as the model should read it, used instead of a plain-text rendering of its HTML (graphs, custom elements, layout-dependent phrasing) |
| any block | `unit` | a label: this subtree is one **call unit** (one prompt); its questions belong to it |
| any block | `role` | `"instructions"`: the block's text goes into the system message, not into a unit |
| question block | `note` | a paragraph printed once before this block's questions |
| row (`add_row(..., model=)`) | `question` | the question as the model should read it (row text is usually the *item*, not the question) |
| row | `about` | a short string naming what the row is about; rows sharing it are grouped under one line |
| row | `options_text` | replaces the `[allowed values]` bracket text; answers are still parsed against the real options |
| row | `skip` | `true`: never asked (worked examples) |
| `MultiRowSelectQuestion`, `MultiRowChecked` | `question` | default wording for every row of that question |
| `CustomComponent` | `questions` | answers the element writes itself (see below), declared so the model can give them |
| root block | `page` | `{"format": "htmleval-model/1", "task": str, "preamble": str, "title": str}`; a page is model-ready exactly when its root carries this |

Policy: `rowData` and `correctValue(s)` are never shown to the model.

A question's wording is resolved row `question` → question `question` → the question's label (the column header);
on a model-ready page an empty wording is an error (`check_declared_keys`).

### Custom components that write answers

A custom element stores answers with `window.htmleval.setAnswer(key, value)` (and reads them back with
`getAnswer(key)`), where `key` is the same `JSON.stringify([row_id, question_id])` the built-in blocks use. Declare
those answers on the host block so `page_keys` and the model see them:

```python
CustomComponent(html="<my-sort data-cards='...'></my-sort>", model={
    "text": "Card 1: ...\nCard 2: ...",
    "questions": [
        {"row_id": "card-1", "question_id": "group", "question": "Group number for card 1",
         "options": [["3:1", "1"], ["3:2", "2"]], "options_text": "1-2; same number = same group"},
    ],
})
```

The option *value* is what the element stores (here `"3:1"`, group 1 of block 3); the *label* is what the model may
answer (`"1"`). The filler accepts either.

## Rendering (`htmleval.modelReview.render`)

- `units(page)`: every block with `model.unit` (outside `audience: "human"` subtrees), plus a `"Page"` unit when
  questions sit outside any unit.
- `render_unit(page, label)`: the unit's material (`model.text`, or its blocks as plain text), then
  `Questions — answer each id with one of the values in brackets.`, any `note`, then the questions grouped by
  `about` as `id: wording [allowed values]`, where `id` is the row id, or `row_id#question_id` when a row carries
  several questions. A unit nested inside a unit is a unit of its own; unit labels must be unique on a page.
- `system_text(page, head)`: `head`, the page's `preamble` (or the generic one), then `THE REVIEWER INSTRUCTIONS:`
  and the text of every `role: "instructions"` block.

## Filling (`htmleval.modelReview.fill`)

```
python -m htmleval.modelReview.fill --eval_dir evaluations/my_eval --reviewer astra \
    --client llmclient --model gpt-6-astra_2026-09-03 [--task "an automatic ..."] [--workers 6] \
    [--replicate K] [--limit N] [--units SUBSTR ...] [--dry_run] [--dump DIR] [--no_upload] \
    [--server_url URL] [--api_key KEY] [--base_url URL] [--page eval.json]
```

Each unit becomes one call (sliced above `--max_rows` rows or `--max_chars` characters, every slice repeating the
material; a unit without questions is skipped). The page is validated first (`check_declared_keys`). The model
answers `{"answers": [{"row_id", "value", "reason"}]}` (`row_id` = the id shown in the prompt); rows left unanswered
are re-asked alone (up to two rounds). The per-call timeout covers the request, not the wait for a free worker. Outputs in the review directory: `closed_<reviewer>.json` (the browser's save format),
`reasons_<reviewer>.json`, `fill_log_<reviewer>.txt`; unless `--no_upload`, the reviewer is registered in
`reviewer_ids.json`, `review_<reviewer>.html` is built if absent (a copy of a person's page built from the same
block JSON, so it carries their custom-element JavaScript; otherwise a fresh page), and the blob is PUT to the
server and read back.

`--replicate K` shuffles each unit's question groups with seed K: a fresh prompt for an independent draw.
`--dump DIR` writes `system.txt` and one file per call, to diff prompts across code changes.

### Clients (`htmleval.modelReview.clients`)

`ModelClient` is one method: `async ask(system, user, schema, tags) -> dict | None`.

- `LlmClientAdapter(model, workers)`: the in-house LlmClient (imported only when used; needs its environment,
  `LLM_SERVER_URL`, `LLM_USER_CODE`, `LLM_CACHE`). One connected client per in-flight call.
- `OpenAIAdapter(model, api_key, base_url, workers)`: any OpenAI-compatible `/chat/completions` endpoint with an
  API key (`--api_key` or `OPENAI_API_KEY`), strict JSON-schema output, `requests` only.

## Helpers (`htmleval.json.model`)

- `page_questions(page)`: every question with its key, wording, options, `about`, unit and hiding.
- `check_declared_keys(page)`: no duplicate keys anywhere; wording and options present on a model-ready page.
- `strip_model(page)`: the page without any metadata, for byte comparisons of what people see.
- `html_to_text(html)`: the plain-text rendering used when a block has no `model.text`.
