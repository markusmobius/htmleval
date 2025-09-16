import os
import sys
import re
import json

# Add the root directory (parent of htmleval) to Python path so 'htmleval' module can be found
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)  # Go up one level from htmleval to the root
sys.path.insert(0, root_dir)

from htmleval.src.reviewLib import Review
from htmleval.src.json.reviewJsonLib import ReviewJSON
from htmleval.src.json.compoundBlocks.tabs import Tabs
from htmleval.src.json.compoundBlocks.column import Column
from htmleval.src.json.simpleBlocks.multiRowSelect import MultiRowSelect, MultiRowSelectQuestion
from htmleval.src.json.simpleBlocks.multiRowChecked import MultiRowChecked
from htmleval.src.json.simpleBlocks.multiRowOption import MultiRowOption
from htmleval.src.json.simpleBlocks.text import Text

def parse_clusters_file(file_path):
    """Parse the clusters_summary.txt file and return a dictionary of cluster data keyed by ID."""
    clusters = {}
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return clusters

    cluster_sections = re.split(r'--- CLUSTER (\d+) ---', content)[1:]
    
    for i in range(0, len(cluster_sections), 2):
        cluster_id = int(cluster_sections[i])
        cluster_content = cluster_sections[i + 1].strip()
        
        topic_match = re.search(r'Topic: (.*)', cluster_content)
        opinions_section = re.search(r'Opinions:\s*(.*)', cluster_content, re.DOTALL)
        opinions = []
        if opinions_section:
            opinion_lines = opinions_section.group(1).strip().split('\n')
            opinions = [line.strip('- ').strip() for line in opinion_lines if line.strip().startswith('-')]
        
        clusters[cluster_id] = {
            'id': cluster_id,
            'topic': topic_match.group(1) if topic_match else "N/A",
            'opinions': opinions
        }
    return clusters

def load_merge_log(file_path):
    """Load the merge log JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []

# --- Main Script ---

# Define file paths
demo_dir = os.path.join(script_dir, "__demo", "cluster1")
clusters_file_path = os.path.join(demo_dir, 'clusters_topics.txt')
merge_log_path = os.path.join(demo_dir, 'merge_log.json')

# Load data
clusters_data = parse_clusters_file(clusters_file_path)
merge_log_data = load_merge_log(merge_log_path)

# Sort the merge log data by anchor cluster ID
merge_log_data.sort(key=lambda x: x.get('anchor_cluster', 0))

if not clusters_data or not merge_log_data:
    print("Could not load necessary data files. Exiting.")
    sys.exit(1)

# Create the root of the JSON structure for the HTML
root = Tabs()
demo = ReviewJSON(root)

# Define options for the user's decision
merge_options = [
    MultiRowOption(label="Yes", value="yes", color="success"),
    MultiRowOption(label="No", value="no", color="danger")
]

# Create a tab for each anchor cluster in the merge log
for merge_item in merge_log_data:
    anchor_id = merge_item['anchor_cluster']
    anchor_cluster = clusters_data.get(anchor_id)

    if not anchor_cluster:
        continue

    # Each tab will contain a single vertical column
    page_column = Column()

    # Add anchor cluster info at the top of the tab
    page_column.add_column([
        Text(title=f"Anchor Cluster: {anchor_id} (Size: {merge_item['anchor_size']})", titleSize=3, body=anchor_cluster['opinions'], is_table=True, scrollable=True)
    ])

    # Process each candidate for this anchor
    for candidate in merge_item['candidates']:
        candidate_id = candidate['candidate_cluster']
        candidate_cluster = clusters_data.get(candidate_id)
        if not candidate_cluster:
            continue

        # Create a two-column layout for the candidate comparison
        comparison_column = Column()
        
        # Left column: Candidate opinions
        comparison_column.add_column([
            Text(title=f"Candidate: {candidate_id}", titleSize=5, body=candidate_cluster['opinions'], is_table=True, scrollable=True)
        ])

        # Right column: Merge info and user input
        decision_info = [
            f"Automated Decision: {candidate.get('decision', 'N/A')}",
            f"Similarity: {candidate.get('similarity', 0):.2f}",
        ]
        if 'gpt_score' in candidate:
            decision_info.append(f"GPT Score: {candidate['gpt_score']}")
        if 'reason' in candidate:
            decision_info.append(f"Reason: {candidate['reason']}")

        user_question = MultiRowSelect(
            rowLabels=["Your Decision"],
            questions=[MultiRowSelectQuestion(label="Merge?", id={1: "merge_decision"}, options=merge_options)]
        )
        user_question.add_row(id={0: f"merge_{anchor_id}_with_{candidate_id}"}, text=["Should these clusters be merged?"])

        comparison_column.add_column([
            Text(title="Merge Details", titleSize=5, body=decision_info),
            user_question
        ])
        
        # Add the comparison block to the main page column
        page_column.add_column([comparison_column])

    root.add_tab(tabName=f"{anchor_id}", block=page_column)

# --- Generate and Save Files ---

# Create the JSON for the review tool
output_json = demo.get_json()

# Ensure the output directory exists
output_dir = os.path.join(demo_dir, "merge_review")
os.makedirs(output_dir, exist_ok=True)

# Save the JSON file
json_path = os.path.join(output_dir, "merge_review.json")
with open(json_path, 'w') as f:
    f.write(output_json)

print(f"Successfully generated {json_path}")

# Create the HTML files
review = Review(targetFolder=output_dir, block=output_json, evalTitle="Cluster Merge Review", serverURL="https://www.kv.econlabs.org/")
review.create(reviewers=["reviewer1", "reviewer2"])

print(f"Successfully created HTML review files in {output_dir}")