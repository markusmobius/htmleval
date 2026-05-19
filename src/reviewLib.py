import os
import json
import uuid
import requests
from typing import Dict, Any, Optional, Callable, List
from collections import Counter
from importlib.resources import files


class Review:

    def __init__(self, block : str, evalTitle : str, serverURL: str):
        self.block=block
        self.evalTitle=evalTitle
        self.serverURL = serverURL

    #create new review
    def create(self, targetFolder : str, defaults : Dict[str, str], reviewers : list[str], reviewerIds : Dict[str, str]=None, readOnly : bool = False, metadata : Dict[str, Any] = None):
        # Path to the reviewer IDs file
        reviewerIdsDisk = os.path.join(targetFolder, "reviewer_ids.json")

        # Initialize / load existing reviewer IDs
        if reviewerIds is None:
            reviewerIds = {}
        # Merge with on-disk file if it exists (disk is authoritative for existing IDs)
        reviewerIdsDisk_existing = {}
        if os.path.exists(reviewerIdsDisk):
            try:
                with open(reviewerIdsDisk, 'r') as f:
                    reviewerIdsDisk_existing = json.load(f)
                # Update only missing keys so passed-in reviewerIds (if any) can override intentionally
                for k, v in reviewerIdsDisk_existing.items():
                    reviewerIds.setdefault(k, v)
            except Exception as e:
                print(f"Warning: could not read existing reviewer IDs '{reviewerIdsDisk}': {e}")

        # Track whether we actually add any new reviewer IDs (or overwrite HTML files)
        # Detect if passed-in reviewerIds already contain entries not on disk
        reviewer_ids_changed = reviewerIds != reviewerIdsDisk_existing

        for reviewer in reviewers: 
            htmlFileName=f"review_{reviewer}.html"
            htmlFileName = os.path.join(targetFolder,htmlFileName)
            if os.path.exists(htmlFileName):
                print(f"ignoring {htmlFileName}: already exists. Would you like to overwrite?")
                overwrite = input("y/n: ")
                if overwrite.lower() != "y":
                    continue
    
            #read HTML template
            #Use module path, to run with pip install
            try:
                html = (files("htmleval.html") / "template.html").read_text()
            #if we can't find the module, assume run it relative path (assume it was cloned)
            except ModuleNotFoundError as e:
                with open(os.path.join(".","src","html","template.html"), 'r') as f:
                    html = f.read()
            
            #replace reviewer and evaltitle
            html=html.replace("REVIEWERNAME",reviewer)
            html=html.replace("EVALTITLE",self.evalTitle)
            if reviewer not in reviewerIds:
                reviewerID = str(uuid.uuid4())
                reviewerIds[reviewer] = reviewerID
                reviewer_ids_changed = True
            else:
                reviewerID = reviewerIds[reviewer]
            html=html.replace("REVIEWERID",reviewerID)

            #replace BLOCKDATA in template
            html=html.replace("BLOCKDATA", self.block)

            #replace DEFAULTS data in template
            if defaults!=None:
                html=html.replace("DEFAULTS", json.dumps(defaults))            
            else:
                html=html.replace("DEFAULTS", "{}")

            #replace READONLY flag
            html=html.replace("READONLY", "true" if readOnly else "false")

            #include all javascript
            js=[]
            #cycle over the compound blocks

            try:
                compound_dir = files("htmleval") / "js" / "compoundBlocks"
                for entry in compound_dir.iterdir():
                    if entry.is_file():
                        js.append(entry.read_text())

            except ModuleNotFoundError as e:
                compoundDir=os.path.join(".","src","js","compoundBlocks")
                for fname in os.listdir(compoundDir):
                    if os.path.isfile(os.path.join(compoundDir, fname)):
                        with open(os.path.join(compoundDir,fname)) as f:
                            js.append(f.read())

            #cycle over the simple blocks
            try:
                simple_dir = files("htmleval") / "js" / "simpleBlocks"
                for entry in simple_dir.iterdir():
                    if entry.is_file():
                        js.append(entry.read_text())
            
            except ModuleNotFoundError as e:
                simpleDir=os.path.join(".","src","js","simpleBlocks")
                for fname in os.listdir(simpleDir):
                    if os.path.isfile(os.path.join(simpleDir, fname)):
                        with open(os.path.join(simpleDir,fname)) as f:
                            js.append(f.read())            
            
            #add the main build script
            try:
                js_text = (files("htmleval.js") / "build.js").read_text()
                js.append(js_text)
            except ModuleNotFoundError as e:
                with open(os.path.join(".","src","js","build.js"), 'r') as f:
                    js.append(f.read())
            
            #insert the JS scripts
            html=html.replace("BUILDJS", '\n'.join(js))            
            html=html.replace("SERVERURL",self.serverURL)

            #save the HTML file
            with open(htmlFileName, 'w') as f:
                f.write(html)

        # Save reviewer IDs only if any new IDs were added
        if reviewer_ids_changed:
            try:
                with open(reviewerIdsDisk, 'w') as f:
                   json.dump(reviewerIds, f, indent=4)
                print(f"Reviewer IDs updated in {reviewerIdsDisk}")
            except Exception as e:
                print(f"Error writing reviewer IDs file '{reviewerIdsDisk}': {e}")
        else:
            print("No new reviewer IDs added; existing reviewer_ids.json left unchanged.")

        # Save metadata if provided
        if metadata is not None:
            metadata_path = os.path.join(targetFolder, "metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=4)

    def close_eval(self, targetFolder : str):
        # Path to the reviewer IDs file
        reviewerIdsDisk = os.path.join(targetFolder, "reviewer_ids.json")

        # Merge with on-disk file if it exists (disk is authoritative for existing IDs)
        if os.path.exists(reviewerIdsDisk):
            try:
                with open(reviewerIdsDisk, 'r') as f:
                    reviewerIds = json.load(f)
            except Exception as e:
                print(f"Warning: could not read existing reviewer IDs '{reviewerIdsDisk}': {e}")
                return
        else:
            print(f"No reviewer IDs file found at '{reviewerIdsDisk}'. Nothing to close.")
            return
        for reviewer, reviewerID in reviewerIds.items():
            if reviewer.startswith("_") or reviewer == "summary":
                continue
            print(f"Retrieving data for reviewer {reviewer}")
            # Do a get request to pull down the data.
            url = self.serverURL + reviewerID

            # Send a GET request to the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON data
                data = response.json()
    
                # Save the JSON data to a file
                with open(os.path.join(targetFolder,  f"closed_{reviewer}.json"), "w") as file:
                    json.dump(data, file, indent=4)        
            else:
                print(f"Failed to download data. HTTP Status code: {response.status_code}")

    def aggregate_closed_reviews(self, targetFolder: str, id_parser: Optional[Callable] = None) -> Dict[str, Any]:
        """Aggregate closed review data from all reviewers.
        
        Args:
            targetFolder: path to the evaluation directory
            id_parser: optional function(row_id_string) -> dict of parsed fields.
                       Used to enrich records when rowData is not available.
        
        Returns a dict with:
            - 'majority_votes': {variable_key: majority_value} for use as defaults
            - 'per_question': {variable_key: {value: count}} raw counts per question
            - 'reviewers': list of reviewer names that had closed data
            - 'stats': summary statistics (error_rate, agreement_rate, total_items)
            - 'records': flat list of per-(reviewer, row, question) dicts for analysis
        """
        # Load block JSON to extract correctValue mappings and rowData
        block_data = json.loads(self.block)
        correct_values, row_correct_values = self._extract_correct_values(block_data)
        row_data_map = self._extract_row_data(block_data)

        # Load all closed review files
        closed_reviews = {}
        reviewerIdsDisk = os.path.join(targetFolder, "reviewer_ids.json")
        if os.path.exists(reviewerIdsDisk):
            with open(reviewerIdsDisk, 'r') as f:
                reviewer_ids = json.load(f)
        else:
            return {"majority_votes": {}, "per_question": {}, "reviewers": [], "stats": {}}

        for reviewer, _ in reviewer_ids.items():
            if reviewer.startswith("_") or reviewer == "summary":
                continue
            closed_path = os.path.join(targetFolder, f"closed_{reviewer}.json")
            if os.path.exists(closed_path):
                with open(closed_path, 'r') as f:
                    data = json.load(f)
                closed_reviews[reviewer] = data.get("variables", {})

        if not closed_reviews:
            return {"majority_votes": {}, "per_question": {}, "reviewers": [], "stats": {}}

        # Collect all variable keys across reviewers
        all_keys = set()
        for variables in closed_reviews.values():
            all_keys.update(variables.keys())

        # Compute per-question counts and majority votes
        per_question = {}
        majority_votes = {}
        agreements = 0
        total_items = 0
        correct_count = 0
        total_with_correct = 0

        for key in sorted(all_keys):
            counts = Counter()
            for reviewer, variables in closed_reviews.items():
                if key in variables:
                    counts[variables[key]] += 1
            per_question[key] = dict(counts)

            # Majority vote
            if counts:
                majority = counts.most_common(1)[0][0]
                majority_votes[key] = majority
                total_items += 1

                # Agreement: all reviewers gave the same answer
                if len(counts) == 1 and sum(counts.values()) == len(closed_reviews):
                    agreements += 1

                # Error rate: check against per-row correctValues first, then question-level
                # Variable keys are JSON-stringified [row_id_dict, question_id]
                try:
                    parsed_key = json.loads(key)
                    if isinstance(parsed_key, list) and len(parsed_key) >= 2:
                        row_id = parsed_key[0]
                        question_id = parsed_key[-1]
                        row_id_json = json.dumps(row_id, sort_keys=True)
                        
                        # Check per-row correctValue first
                        row_key = (row_id_json, question_id)
                        if row_key in row_correct_values:
                            total_with_correct += 1
                            if majority == row_correct_values[row_key]:
                                correct_count += 1
                        elif question_id in correct_values:
                            total_with_correct += 1
                            if majority == correct_values[question_id]:
                                correct_count += 1
                except (json.JSONDecodeError, TypeError):
                    pass

        stats = {
            "total_items": total_items,
            "num_reviewers": len(closed_reviews),
            "agreement_rate": agreements / total_items if total_items > 0 else 0,
        }
        if total_with_correct > 0:
            stats["majority_error_rate"] = 1.0 - (correct_count / total_with_correct)
            stats["total_with_correct_value"] = total_with_correct

        # Per-reviewer error rates against correctValue
        per_reviewer_error = {}
        for reviewer, variables in closed_reviews.items():
            r_correct = 0
            r_total = 0
            for key, value in variables.items():
                try:
                    parsed_key = json.loads(key)
                    if isinstance(parsed_key, list) and len(parsed_key) >= 2:
                        row_id = parsed_key[0]
                        question_id = parsed_key[-1]
                        row_id_json = json.dumps(row_id, sort_keys=True)
                        
                        row_key = (row_id_json, question_id)
                        if row_key in row_correct_values:
                            r_total += 1
                            if value == row_correct_values[row_key]:
                                r_correct += 1
                        elif question_id in correct_values:
                            r_total += 1
                            if value == correct_values[question_id]:
                                r_correct += 1
                except (json.JSONDecodeError, TypeError):
                    pass
            if r_total > 0:
                per_reviewer_error[reviewer] = 1.0 - (r_correct / r_total)
        if per_reviewer_error:
            stats["per_reviewer_error_rate"] = per_reviewer_error

        # Build flat records for analysis
        records = []
        for reviewer, variables in closed_reviews.items():
            for key, answer in variables.items():
                parsed_key = None
                try:
                    parsed_key = json.loads(key)
                    if isinstance(parsed_key, list) and len(parsed_key) >= 2:
                        row_id = str(parsed_key[0])
                        question_id = str(parsed_key[-1])
                    else:
                        row_id = str(parsed_key)
                        question_id = ""
                except (json.JSONDecodeError, TypeError):
                    row_id = key
                    question_id = ""
                
                # Get correct value for this record
                row_id_json = json.dumps(parsed_key[0], sort_keys=True) if isinstance(parsed_key, list) and len(parsed_key) >= 2 else ""
                row_key = (row_id_json, question_id)
                cv = row_correct_values.get(row_key, correct_values.get(question_id, None))
                
                record = {
                    "reviewer": reviewer,
                    "row_id": row_id,
                    "question_id": question_id,
                    "answer": answer,
                    "correct_value": cv,
                }
                
                # Enrich with rowData if available (prefer per-question key)
                row_q_key = (row_id, question_id)
                if row_q_key in row_data_map:
                    record.update(row_data_map[row_q_key])
                elif row_id in row_data_map:
                    record.update(row_data_map[row_id])
                elif id_parser is not None:
                    try:
                        parsed = id_parser(row_id)
                        if isinstance(parsed, dict):
                            record.update(parsed)
                    except Exception:
                        pass
                
                records.append(record)

        return {
            "majority_votes": majority_votes,
            "per_question": per_question,
            "reviewers": list(closed_reviews.keys()),
            "stats": stats,
            "records": records
        }

    def _serialize_block(self, obj):
        """Serialize a block object to a JSON-compatible dict."""
        return json.loads(json.dumps(obj, default=lambda x: x.__dict__))

    def _prompt_overwrite(self, path):
        """If path exists, prompt for overwrite. Returns True if ok to write."""
        if os.path.exists(path):
            print(f"ignoring {path}: already exists. Would you like to overwrite?")
            return input("y/n: ").lower() == "y"
        return True

    def generate_summary(self, targetFolder: str, group_by: Optional[List[str]] = None, id_parser: Optional[Callable] = None):
        """Generate a read-only summary reviewer HTML with majority-vote defaults.
        
        Args:
            targetFolder: path to the evaluation directory
            group_by: optional list of record field names to group breakdown tables by.
                      First field splits into separate tables, remaining fields add sub-rows.
                      Fields come from rowData, id_parser, or built-in derived fields.
            id_parser: optional function(row_id_string) -> dict of parsed fields.
                       Used when rowData is not available on rows.
        
        Metadata is loaded from metadata.json (saved by create()).
        """
        from src.json.compoundBlocks.column import Column as ColumnBlock
        from src.json.simpleBlocks.text import Text as TextBlock

        # Load metadata from disk
        metadata_path = os.path.join(targetFolder, "metadata.json")
        metadata = None
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

        aggregated = self.aggregate_closed_reviews(targetFolder, id_parser=id_parser)
        stats = aggregated["stats"]
        records = aggregated.get("records", [])
        correct_values, row_correct_values = self._extract_correct_values(json.loads(self.block))

        # Stats table
        stats_rows = [
            ["Reviewers", ", ".join(aggregated["reviewers"])],
            ["Total items", str(stats.get("total_items", 0))],
            ["Agreement rate (unanimous)", f"{stats.get('agreement_rate', 0):.1%}"],
        ]
        if "majority_error_rate" in stats:
            n = stats["total_with_correct_value"]
            stats_rows.append([f"Majority error rate ({n} items with correctValue)", f"{stats['majority_error_rate']:.1%}"])
        for reviewer, rate in stats.get("per_reviewer_error_rate", {}).items():
            stats_rows.append([f"Error rate ({reviewer})", f"{rate:.1%}"])

        # Breakdown tables
        breakdown_tables = []
        if records:
            if group_by:
                # First group_by field splits into separate tables,
                # remaining group_by fields add sub-rows within each table.
                primary_field = group_by[0]
                sub_fields = group_by[1:]

                # Split records by primary field
                primary_groups = {}
                for r in records:
                    pval = r.get(primary_field, "unknown")
                    if pval not in primary_groups:
                        primary_groups[pval] = []
                    primary_groups[pval].append(r)

                for pval in sorted(primary_groups.keys()):
                    p_records = primary_groups[pval]
                    all_values = sorted(set(r["answer"] for r in p_records))
                    has_correct = any(r.get("correct_value") is not None for r in p_records)

                    # Build row groups: Overall + sub-field breakdowns
                    row_groups = [("Overall", p_records)]
                    for sub_field in sub_fields:
                        sub_groups = {}
                        for r in p_records:
                            sval = r.get(sub_field, None)
                            if sval is None:
                                continue
                            if sval not in sub_groups:
                                sub_groups[sval] = []
                            sub_groups[sval].append(r)
                        for sval in sorted(sub_groups.keys()):
                            row_groups.append((f"{sub_field}={sval}", sub_groups[sval]))

                    table_label = pval

                    if has_correct:
                        header = [f"<b>{table_label}</b>", "<b>Error Rate</b>", "<b>n</b>"]
                        table_rows = [header]
                        for label, group_records in row_groups:
                            with_cv = [r for r in group_records if r.get("correct_value") is not None]
                            if not with_cv:
                                table_rows.append([label, "-", "0"])
                                continue
                            n = len(with_cv)
                            errors = sum(1 for r in with_cv if r["answer"] != r["correct_value"])
                            table_rows.append([label, f"{errors/n:.0%}", str(n)])
                        breakdown_tables.append((table_rows, True))
                    else:
                        header = [f"<b>{table_label}</b>"] + [f"<b>{v}</b>" for v in all_values]
                        table_rows = [header]
                        for label, group_records in row_groups:
                            n = len(group_records)
                            counts = Counter(r["answer"] for r in group_records)
                            row = [label] + [f"{counts.get(v,0)/n:.0%} ({counts.get(v,0)})" if n > 0 else "-" for v in all_values]
                            table_rows.append(row)
                        breakdown_tables.append((table_rows, False))
            else:
                # No group_by: one table per question_id (original behavior)
                by_question = {}
                for r in records:
                    qid = r.get("question_id", "")
                    if qid not in by_question:
                        by_question[qid] = []
                    by_question[qid].append(r)

                for qid in sorted(by_question.keys()):
                    q_records = by_question[qid]
                    all_values = sorted(set(r["answer"] for r in q_records))
                    has_correct = any(r.get("correct_value") is not None for r in q_records)

                    if has_correct:
                        header = [f"<b>{qid}</b>", "<b>Error Rate</b>", "<b>n</b>"]
                        table_rows = [header]
                        n_cv = [r for r in q_records if r.get("correct_value") is not None]
                        if n_cv:
                            n = len(n_cv)
                            errors = sum(1 for r in n_cv if r["answer"] != r["correct_value"])
                            table_rows.append(["Overall", f"{errors/n:.0%}", str(n)])
                        breakdown_tables.append((table_rows, True))
                    else:
                        header = [f"<b>{qid}</b>"] + [f"<b>{v}</b>" for v in all_values]
                        table_rows = [header]
                        n = len(q_records)
                        counts = Counter(r["answer"] for r in q_records)
                        row = ["Overall"] + [f"{counts.get(v,0)/n:.0%} ({counts.get(v,0)})" if n > 0 else "-" for v in all_values]
                        table_rows.append(row)
                    breakdown_tables.append((table_rows, False))

        # Build TSV data for copy-paste
        tsv_data = self._build_tsv(records)

        # Build block data: original tabs + Summary + Data + Metadata
        block_data = json.loads(self.block)
        if block_data.get("type") == "tabs":
            summary_blocks = [
                TextBlock(title="Statistics", titleSize=3, body=stats_rows, is_table=True),
            ]
            # Group breakdown tables by (has_correct, ncols) so columns align
            if breakdown_tables:
                groups = {}
                for bt, has_correct in breakdown_tables:
                    ncols = len(bt[0]) if bt else 0
                    key = (has_correct, ncols)
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(bt)
                for key in sorted(groups.keys()):
                    combined_rows = []
                    for i, bt in enumerate(groups[key]):
                        for row in bt:
                            combined_rows.append(row)
                        if i < len(groups[key]) - 1:
                            ncols = len(bt[0]) if bt else 1
                            combined_rows.append([""] * ncols)
                    summary_blocks.append(TextBlock(title="", titleSize=4, body=combined_rows, is_table=True))

            summary_col = ColumnBlock()
            summary_col.add_column(summary_blocks)
            block_data["content"].append({"tabName": "Summary", "block": self._serialize_block(summary_col)})

            # Data tab with download button and copyable TSV
            import html as html_mod
            tsv_escaped = html_mod.escape(tsv_data)
            download_btn = (
                f"<button onclick=\"var a=document.createElement('a');"
                f"a.href='data:text/tab-separated-values;charset=utf-8,'+encodeURIComponent(document.getElementById('tsv-data').textContent);"
                f"a.download='review_data.tsv';a.click();\" "
                f"class='btn btn-primary btn-sm mb-2'>Download TSV</button>"
            )
            data_col = ColumnBlock()
            data_col.add_column([
                TextBlock(title="Review Data", titleSize=3,
                          body=[f"{download_btn}<pre id='tsv-data' style='max-height: 500px; overflow: auto; font-size: 11px; white-space: pre;'>{tsv_escaped}</pre>"])
            ])
            block_data["content"].append({"tabName": "Data", "block": self._serialize_block(data_col)})

            if metadata:
                metadata_rows = [[f"<b>{k}</b>", f"<pre>{json.dumps(v, indent=2)}</pre>" if isinstance(v, (dict, list)) else str(v)] for k, v in metadata.items()]
                block_data["content"].append({"tabName": "Metadata", "block": self._serialize_block(TextBlock(title="Evaluation Metadata", titleSize=3, body=metadata_rows, is_table=True))})

        # Create read-only summary HTML
        summary_review = Review(block=json.dumps(block_data), evalTitle=self.evalTitle + " (Summary)", serverURL=self.serverURL)
        summary_review.create(targetFolder=targetFolder, defaults=aggregated["majority_votes"], reviewers=["summary"], reviewerIds={"summary": str(uuid.uuid4())}, readOnly=True)

        # Save aggregated data
        summary_json_path = os.path.join(targetFolder, "summary.json")
        if self._prompt_overwrite(summary_json_path):
            with open(summary_json_path, "w") as f:
                json.dump(aggregated, f, indent=4, default=str)

        return aggregated

    @staticmethod
    def _build_tsv(records: List[Dict]) -> str:
        """Build a TSV string from a list of record dicts."""
        if not records:
            return "(no data)"
        # Collect all keys across all records to build headers
        all_keys = []
        seen = set()
        # Ensure standard columns come first
        for k in ["reviewer", "row_id", "question_id", "answer", "correct_value"]:
            if any(k in r for r in records):
                all_keys.append(k)
                seen.add(k)
        # Add any extra keys (from rowData / id_parser)
        for r in records:
            for k in r:
                if k not in seen:
                    all_keys.append(k)
                    seen.add(k)
        
        lines = ["\t".join(all_keys)]
        for r in records:
            lines.append("\t".join("" if r.get(k) is None else str(r.get(k, "")) for k in all_keys))
        return "\n".join(lines)

    @staticmethod
    def _extract_correct_values(block_data: Any, result: Optional[Dict] = None, row_result: Optional[Dict] = None) -> Dict:
        """Walk the block tree and extract correctValue mappings.
        
        Returns two dicts via result and row_result:
            result: {question_id: correctValue} — question-level defaults
            row_result: {(row_id_json, question_id): correctValue} — per-row overrides
        """
        if result is None:
            result = {}
        if row_result is None:
            row_result = {}
        if isinstance(block_data, dict):
            # Check for MultiRowSelect questions with correctValue
            if block_data.get("type") == "multi_row_select":
                questions = block_data.get("content", {}).get("questions", [])
                rows = block_data.get("content", {}).get("rows", [])
                for q in questions:
                    if "correctValue" in q and "id" in q:
                        qid = q["id"]
                        if isinstance(qid, dict):
                            qid = list(qid.values())[0]
                        result[qid] = q["correctValue"]
                # Extract per-row correctValues
                for row in rows:
                    if "correctValues" in row and "id" in row:
                        rid = row["id"]
                        if isinstance(rid, dict):
                            rid = list(rid.values())[0]
                        row_id_json = json.dumps(rid, sort_keys=True)
                        for q_key, cv in row["correctValues"].items():
                            row_result[(row_id_json, q_key)] = cv
            # Check for MultiRowChecked with correctValue
            if block_data.get("type") == "multi_row_checked":
                content = block_data.get("content", {})
                if "correctValue" in content and "id" in content:
                    cid = content["id"]
                    if isinstance(cid, dict):
                        cid = list(cid.values())[0]
                    result[cid] = content["correctValue"]
            # Recurse into all dict values
            for v in block_data.values():
                Review._extract_correct_values(v, result, row_result)
        elif isinstance(block_data, list):
            for item in block_data:
                Review._extract_correct_values(item, result, row_result)
        return result, row_result

    @staticmethod
    def _extract_row_data(block_data: Any, result: Optional[Dict] = None) -> Dict:
        """Walk the block tree and extract rowData mappings.
        
        Keys in the result dict:
        - row_id string: rowData (general fallback)
        - (row_id, question_id) tuple: rowData (precise per-question lookup,
          used when separate blocks share a row_id but have different rowData)
        """
        if result is None:
            result = {}
        if isinstance(block_data, dict):
            if block_data.get("type") in ("multi_row_select", "multi_row_checked"):
                rows = block_data.get("content", {}).get("rows", [])
                questions = block_data.get("content", {}).get("questions", [])
                q_ids = []
                q_labels = {}  # question_id -> label
                for q in questions:
                    qid = q.get("id", {})
                    label = q.get("label", "")
                    if isinstance(qid, dict):
                        for v in qid.values():
                            q_ids.append(v)
                            q_labels[str(v)] = label
                for row in rows:
                    if "rowData" in row and "id" in row:
                        rid = row["id"]
                        if isinstance(rid, dict):
                            rid = list(rid.values())[0]
                        rid = str(rid)
                        result[rid] = row["rowData"]
                        for qid in q_ids:
                            enriched = dict(row["rowData"])
                            # Auto-populate question_name from question label if not set
                            if "question_name" not in enriched and str(qid) in q_labels:
                                enriched["question_name"] = q_labels[str(qid)]
                            result[(rid, str(qid))] = enriched
            for v in block_data.values():
                Review._extract_row_data(v, result)
        elif isinstance(block_data, list):
            for item in block_data:
                Review._extract_row_data(item, result)
        return result


