"""Fill a review with a language model, producing exactly what a human review produces.

Units of analysis:
  * a CALL UNIT is one unit of the page (a block carrying ``model.unit``; see ``render``), sliced into several calls
    above --max_rows question rows or --max_chars prompt characters;
  * an ANSWER is one (row_id, question_id), stored under the page's own answer key (``answerKeys.variable_key``).

Input: the page itself (``eval.json`` by default) -- its blocks carry the ``model`` metadata (``htmleval.json.model``)
that says what the model reads and which questions it answers. The root must carry ``model.page`` (a model-ready page).
Output, in the review directory, in the shape the browser saves and ``Review.close_eval`` downloads:
  closed_<reviewer>.json   {"active": {}, "variables": {key: value}, "timestamps": {key: iso}}
  reasons_<reviewer>.json  {row_id: one-sentence reason}          (the model's reasoning, not part of the review)
  fill_log_<reviewer>.txt  one line per call
  reviewer_ids.json        gains reviewer -> uuid4 (never overwrites an existing id)
  review_<reviewer>.html   built if absent, so a person can open the filled review
and, unless --no_upload, the same blob is PUT to the review server exactly as the page does, so the review page shows
the answers and ``Review.generate_summary`` needs nothing special.

Rows a reply leaves unanswered are re-asked on their own (up to FOLLOWUP_ROUNDS). --replicate K shuffles the question
order with seed K for an independent draw (a new prompt, so no cache hit on a caching service).

Usage:
  python -m htmleval.modelReview.fill --eval_dir <dir> --reviewer astra --client llmclient --model <model>
      [--page eval.json] [--task "..."] [--replicate K] [--workers 6] [--limit N] [--units SUBSTR ...]
      [--dry_run] [--dump DIR] [--no_upload] [--server_url URL] [--api_key KEY] [--base_url URL]
"""
import argparse
import asyncio
import datetime
import difflib
import glob
import json
import os
import sys

from ..json.model import load, page_meta
from . import render as mr

DEFAULT_SERVER = "https://www.kv.econlabs.org/"
CALL_TIMEOUT_S = 1500
MIN_ROWS_PER_CALL = 20
ATTEMPTS = 6
FOLLOWUP_ROUNDS = 2      # re-ask only the rows a reply left unanswered, up to this many times
DEFAULT_TASK = "a review form"

SCHEMA = {
    "type": "object",
    "properties": {"answers": {"type": "array", "items": {
        "type": "object",
        "properties": {"row_id": {"type": "string"}, "value": {"type": "string"}, "reason": {"type": "string"}},
        "required": ["row_id", "value", "reason"], "additionalProperties": False}}},
    "required": ["answers"], "additionalProperties": False,
}
SYSTEM = ("You are a careful human reviewer filling out an evaluation form about {task}. Judge strictly from the "
          "material shown and the definitions given. Answer EVERY question row with exactly one of its option values "
          "(the value, not the label) and a one-sentence reason. Do not skip rows and do not invent row ids.")


# ── slicing a unit into calls ────────────────────────────────────────────────────────────────────

def prompt_text(lines):
    """The user prompt of a call: its tagged lines joined."""
    return "\n".join(line for line, _ in lines)


def slice_calls(label, out, rows, max_rows, max_chars):
    """[(label, lines, rows)]: the unit as one call, or as several calls that each repeat every
    context line and carry a slice of the question rows (long pages cannot be answered reliably in one
    structured reply). ``lines`` is the call's subset of the renderer's tagged lines (``prompt_text`` joins
    them). Row order is preserved."""
    context_chars = sum(len(line) + 1 for line, r in out if r is None)
    if len(rows) <= max_rows and context_chars + sum(len(line) + 1 for line, r in out if r is not None) <= max_chars:
        return [(label, out, rows)]
    # size the slices: as many rows per call as fit under both caps, but never fewer than MIN_ROWS_PER_CALL --
    # a page whose context alone exceeds max_chars still gets sensible batches.
    row_chars = [len(line) + 1 for line, r in out if isinstance(r, dict)]
    if context_chars > max_chars:
        # The context is repeated in every batch, so once it exceeds the cap the only lever left is the
        # output size: use full batches rather than many tiny calls that each re-send the whole page.
        per_call = max_rows
        print(f"note: {label}: context alone is {context_chars:,} chars (> --max_chars {max_chars:,}); "
              f"batching {len(rows)} rows by {per_call}", flush=True)
    else:
        fit = (max_chars - context_chars) // max(1, max(row_chars))
        per_call = max(MIN_ROWS_PER_CALL, min(max_rows, fit))
    result, start, part = [], 0, 1
    while start < len(rows):
        keep = {id(r) for r in rows[start:start + per_call]}
        lines = [(line, r) for line, r in out if r is None
                 or (isinstance(r, dict) and id(r) in keep)
                 or (isinstance(r, tuple) and any(id(x) in keep for x in r[1]))]
        result.append((f"{label} (part {part}, rows {start + 1}-{min(start + per_call, len(rows))} of {len(rows)})",
                       lines, rows[start:start + per_call]))
        start += per_call; part += 1
    return result


# ── answers ──────────────────────────────────────────────────────────────────────────────────────

def parse_answers(raw, rows):
    """Map the model's answers onto variable keys; accept the option value or its label, any case."""
    by_id = {r["row_id"]: r for r in rows}
    variables, reasons, rejected = {}, {}, []
    for a in (raw or {}).get("answers", []) or []:
        rid = str(a.get("row_id", "")).strip()
        r = by_id.get(rid)
        if r is None:
            # A mistyped id is repaired to the closest row id when that match is clearly better than the
            # runner-up (so "..._9_..." is not confused with "..._1_...") and unanswered.
            scored = sorted(((difflib.SequenceMatcher(None, rid, cand).ratio(), cand) for cand in by_id), reverse=True)
            best, second = scored[0], (scored[1] if len(scored) > 1 else (0.0, None))
            if best[0] >= 0.85 and best[0] - second[0] >= 0.03 and by_id[best[1]]["key"] not in variables:
                r = by_id[best[1]]
                rejected.append((rid, f"repaired to {best[1]}"))
            else:
                rejected.append((rid, "unknown row_id")); continue
        v = str(a.get("value", "")).strip()
        canon = {**{k.lower(): k for k in r["options"]}, **{lbl.lower(): k for k, lbl in r["options"].items()}}
        value = canon.get(v.lower())
        if value is None:
            rejected.append((rid, f"value {v!r} not an option")); continue
        variables[r["key"]] = value
        reasons[r["row_id"]] = a.get("reason", "")
    return variables, reasons, rejected


def followup(label, lines, rows, variables):
    """The same call with only its unanswered question rows left in: every material line is kept, a question line
    only while its key is unanswered, and an "About ..." group line only while a question under it is."""
    missing = [row for row in rows if row["key"] not in variables]
    kept = []
    for line, tag in lines:
        if tag is None:
            kept.append((line, tag))
        elif isinstance(tag, dict):
            if tag["key"] not in variables:
                kept.append((line, tag))
        elif any(r["key"] not in variables for r in tag[1]):
            kept.append((line, tag))
    return (f"{label} (follow-up, {len(missing)} rows)", kept, missing)


async def ask_unit(client, label, system, prompt, rows, tags=(), attempts=ATTEMPTS, timeout=CALL_TIMEOUT_S):
    """One call: ask, retry on any failure, parse. Returns (label, variables, reasons, rejected)."""
    raw = None
    for attempt in range(attempts):
        try:
            raw = await asyncio.wait_for(client.ask(system, prompt, SCHEMA, list(tags)), timeout=timeout)
        except asyncio.CancelledError:
            raise                                   # a cancelled fill (Ctrl-C) must stop, not retry
        except json.JSONDecodeError:
            return label, {}, {}, [(r["row_id"], "UNPARSEABLE ANSWER") for r in rows]
        except Exception as e:                      # noqa: BLE001 - retry any failure, including a timeout
            raw = None
            print(f"{label}: attempt {attempt + 1} failed: {type(e).__name__}: {e}", flush=True)
        if raw is not None:
            break
        await asyncio.sleep(15)
    if raw is None:
        return label, {}, {}, [(r["row_id"], "NO ANSWER") for r in rows]
    variables, reasons, rejected = parse_answers(raw, rows)
    return label, variables, reasons, rejected


# ── output in the human shape ──────────────────────────────────────────────────────────────────────

def timestamp_key(key):
    """build.js's rule: the answer key with its last element replaced by "timestamp"."""
    try:
        parts = json.loads(key)
        if isinstance(parts, list) and parts:
            parts[-1] = "timestamp"
            return json.dumps(parts, separators=(",", ":"), ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        pass
    return key


def answer_blob(variables):
    """The page's save format for these answers (every answer timestamped now)."""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    return {"active": {}, "variables": dict(variables), "timestamps": {timestamp_key(k): now for k in variables}}


# ── the calls of a page ──────────────────────────────────────────────────────────────────────────

def model_calls(block_json, task=None, replicate=0, units_filter=None, limit=None, max_rows=120, max_chars=400000):
    """(system, units, calls) for a model-ready page: one call unit per ``model.unit`` block (sliced when large).
    ``task`` overrides the page's ``model.page.task``. Raises ValueError when the page is not model-ready."""
    block = load(block_json)
    page = page_meta(block)
    if page is None:
        raise ValueError("the page is not model-ready: its root block carries no model.page "
                         "(see htmleval.json.model; build the page with model metadata or annotate it)")
    system = mr.system_text(block, SYSTEM.format(task=task or page.get("task") or DEFAULT_TASK))
    units = mr.units(block)
    if units_filter:
        units = [u for u in units if any(sub in u[0] for sub in units_filter)]
    if limit:
        units = units[:limit]
    calls = []
    for label, node in units:
        seed = f"{replicate}:{label}" if replicate else None
        out, rows = mr.render_unit(block, label, unit_node=node, shuffle_seed=seed)
        calls.extend(slice_calls(label, out, rows, max_rows, max_chars))
    return system, units, calls


def dump_calls(dump_dir, system, calls):
    """system.txt and one NNNN.txt per call (LABEL, ROWS, blank line, the prompt): the prompt-identity gate."""
    os.makedirs(dump_dir, exist_ok=True)
    with open(os.path.join(dump_dir, "system.txt"), "w", encoding="utf-8") as f:
        f.write(system)
    for i, (label, lines, rows) in enumerate(calls):
        with open(os.path.join(dump_dir, f"{i:04d}.txt"), "w", encoding="utf-8") as f:
            f.write(f"LABEL {label}\nROWS {len(rows)}\n\n{prompt_text(lines)}")


async def fill(eval_dir, reviewer, client, *, page="eval.json", task=None, replicate=0, units_filter=None, limit=None,
               max_rows=120, max_chars=400000, dry_run=False, dump_dir=None, no_upload=False, server_url=None,
               title="Review", tags=None, attempts=ATTEMPTS, timeout=CALL_TIMEOUT_S):
    """Fill one review directory; returns {"answered", "total", "rejected", "closed_path", "url"}."""
    page_path = os.path.join(eval_dir, page)
    if not os.path.exists(page_path):
        sys.exit(f"{page_path} not found")
    with open(page_path, encoding="utf-8") as f:
        block_json = f.read()
    system, units, rendered = model_calls(block_json, task=task, replicate=replicate, units_filter=units_filter,
                                          limit=limit, max_rows=max_rows, max_chars=max_chars)
    total_rows = sum(len(rows) for _, _, rows in rendered)
    print(f"{len(units)} units -> {len(rendered)} calls (max {max_rows} rows / {max_chars:,} chars each); "
          f"{total_rows} question rows; system message {len(system):,} chars", flush=True)
    if dump_dir:
        dump_calls(dump_dir, system, rendered)
        print(f"dumped {len(rendered)} prompts to {dump_dir}", flush=True)
    if dry_run:
        print("\n===== SYSTEM PROMPT =====\n" + system)
        for label, lines, rows in rendered[:2]:
            prompt = prompt_text(lines)
            print(f"\n===== UNIT {label}: {len(prompt):,} chars, {len(rows)} rows =====\n{prompt}")
        for label, lines, rows in rendered:
            print(f"  {label:40s} {len(prompt_text(lines)):>8,} chars {len(rows):4d} rows")
        return {"answered": 0, "total": total_rows, "rejected": 0, "closed_path": None, "url": None}

    tags = list(tags or ["htmleval", "model_review", reviewer])
    variables, reasons, log, rejected_all = {}, {}, [], []
    closed_path = os.path.join(eval_dir, f"closed_{reviewer}.json")
    todo = rendered
    for round_no in range(1 + FOLLOWUP_ROUNDS):
        tasks = [ask_unit(client, label, system, prompt_text(lines), rows, tags, attempts, timeout)
                 for label, lines, rows in todo]
        for coro in asyncio.as_completed(tasks):
            label, v, r, rejected = await coro
            variables.update(v); reasons.update(r); rejected_all.extend(rejected)
            n_rows = next(len(rows) for lab, _, rows in todo if lab == label)
            line = f"{label}: {len(v)}/{n_rows} rows answered" + (f", {len(rejected)} rejected" if rejected else "")
            log.append(line); print(line, flush=True)
            with open(closed_path, "w", encoding="utf-8") as f:       # partial progress survives a crash
                json.dump({**answer_blob(variables), "partial": True}, f, indent=1, ensure_ascii=False)
        # A reply can stop early or garble a row id; asking the SAME prompt again could be a cache hit on a
        # caching service, so the follow-up asks only the unanswered rows -- a new prompt with the same context.
        todo = [followup(label, lines, rows, variables) for label, lines, rows in todo
                if any(row["key"] not in variables for row in rows)]
        if not todo:
            break
        print(f"follow-up round {round_no + 1}: {len(todo)} calls, {sum(len(r) for _, _, r in todo)} unanswered rows", flush=True)
        log.append(f"follow-up round {round_no + 1}: {len(todo)} calls")

    blob = answer_blob(variables)
    with open(closed_path, "w", encoding="utf-8") as f:
        json.dump(blob, f, indent=1, ensure_ascii=False)
    with open(os.path.join(eval_dir, f"reasons_{reviewer}.json"), "w", encoding="utf-8") as f:
        json.dump({"reviewer": reviewer, "model": getattr(client, "model", None), "reasons": reasons}, f, indent=1, ensure_ascii=False)
    with open(os.path.join(eval_dir, f"fill_log_{reviewer}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log + [f"REJECTED {rid}: {why}" for rid, why in rejected_all]))
    print(f"answered {len(variables)}/{total_rows} rows; rejected {len(rejected_all)}; wrote {closed_path}, reasons, log")
    if rejected_all:
        print("first rejected:", rejected_all[:10])
    if not variables:
        sys.exit("no rows were answered: nothing registered or uploaded (see the fill log)")
    url = None
    if not no_upload:                  # a local-only fill (e.g. a replicate draw) registers no reviewer and no page
        from ..reviewLib import Review
        server = server_url or os.getenv("HTMLEVAL_SERVER_URL", DEFAULT_SERVER)
        review = Review(block=block_json, evalTitle=title, serverURL=server)
        reviewer_id = review.register_reviewer(eval_dir, reviewer)
        page_path = os.path.join(eval_dir, f"review_{reviewer}.html")
        others = sorted(p for p in glob.glob(os.path.join(eval_dir, "review_*.html"))
                        if os.path.basename(p) not in (f"review_{reviewer}.html", "review_summary.html"))
        if not os.path.exists(page_path):
            if others:
                # the model's page is the people's page with the reviewer swapped (keeps their custom-element JS)
                Review.clone_reviewer_page(others[0], page_path, reviewer, reviewer_id)
            else:
                review.create(targetFolder=eval_dir, defaults=None, reviewers=[reviewer],
                              reviewerIds={reviewer: reviewer_id}, overwrite=False)
        url = review.upload(eval_dir, reviewer, blob)
        print(f"uploaded and verified: {url}")
        print(f"page: {os.path.join(eval_dir, f'review_{reviewer}.html')}")
    if len(variables) < total_rows:
        print(f"WARNING: {total_rows - len(variables)} rows unanswered")
    await client.close()
    return {"answered": len(variables), "total": total_rows, "rejected": len(rejected_all), "closed_path": closed_path, "url": url}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eval_dir", required=True)
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--client", choices=["llmclient", "openai"], default="llmclient")
    ap.add_argument("--model", required=True)
    ap.add_argument("--page", default="eval.json", help="the page file inside --eval_dir (default: %(default)s)")
    ap.add_argument("--task", default=None, help="what the form is about, for the system prompt (default: the page's model.page.task)")
    ap.add_argument("--title", default=None, help="title of the reviewer page built for the model (default: the page's model.page.title, or 'Review')")
    ap.add_argument("--replicate", type=int, default=0,
                    help="replicate draw K>=1: shuffle each unit's question order with seed K (new prompts); pair with "
                         "--reviewer <name>_rK --no_upload. 0 = the page order")
    ap.add_argument("--workers", type=int, default=6, help="concurrent calls")
    ap.add_argument("--max_rows", type=int, default=120, help="split a unit into calls of at most this many rows")
    ap.add_argument("--max_chars", type=int, default=400000, help="split a unit into calls of at most this many prompt chars")
    ap.add_argument("--limit", type=int, default=None, help="only the first N call units")
    ap.add_argument("--units", nargs="+", default=None, help="only call units whose label contains one of these substrings")
    ap.add_argument("--dry_run", action="store_true", help="print the prompts and row counts; no model calls")
    ap.add_argument("--dump", default=None, help="write system.txt and one file per call prompt into this directory")
    ap.add_argument("--no_upload", action="store_true", help="do not PUT the answers to the review server")
    ap.add_argument("--server_url", default=None, help="review server (default: HTMLEVAL_SERVER_URL, then the econlabs server)")
    ap.add_argument("--api_key", default=None, help="openai client: the API key (default: OPENAI_API_KEY)")
    ap.add_argument("--base_url", default=None, help="openai client: the endpoint base (default: https://api.openai.com/v1)")
    args = ap.parse_args(argv)

    page_path = os.path.join(args.eval_dir, args.page)
    title = args.title
    if title is None and os.path.exists(page_path):
        with open(page_path, encoding="utf-8") as f:
            title = (page_meta(f.read()) or {}).get("title") or "Review"
    if args.dry_run:
        client = None
    else:
        from .clients import make_client
        client = make_client(args.client, args.model, workers=args.workers, api_key=args.api_key, base_url=args.base_url)
    asyncio.run(fill(args.eval_dir, args.reviewer, client, page=args.page, task=args.task, replicate=args.replicate,
                     units_filter=args.units, limit=args.limit, max_rows=args.max_rows, max_chars=args.max_chars,
                     dry_run=args.dry_run, dump_dir=args.dump, no_upload=args.no_upload, server_url=args.server_url,
                     title=title or "Review"))


if __name__ == "__main__":
    main()
