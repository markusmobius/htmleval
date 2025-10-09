import os
import sys
import json

# Add the root directory (parent of htmleval) to Python path so 'htmleval' module can be found
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)  # Go up one level from htmleval to the root
sys.path.insert(0, root_dir)

from htmleval.src.reviewLib import Review
from htmleval.src.json.reviewJsonLib import ReviewJSON
from htmleval.src.json.compoundBlocks.tabs import Tabs
from htmleval.src.json.compoundBlocks.column import Column
from htmleval.src.json.compoundBlocks.interactive import Interactive
from htmleval.src.json.compoundBlocks.interactive import InteractiveParagraph
from htmleval.src.json.compoundBlocks.interactive import InteractiveFragment
from htmleval.src.json.simpleBlocks.multiRowSelect import MultiRowSelect
from htmleval.src.json.simpleBlocks.multiRowSelect import MultiRowSelectQuestion
from htmleval.src.json.simpleBlocks.multiRowChecked import MultiRowChecked
from htmleval.src.json.simpleBlocks.multiRowOption import MultiRowOption
from htmleval.src.json.simpleBlocks.text import Text


def read_article_file(filename, article_dir):
    """Read an article file and extract title and body."""
    file_path = os.path.join(article_dir, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Find the first non-empty line for the title
            title = "No Title"
            body_start_index = 0
            for i, line in enumerate(lines):
                if line.strip(): # if the line is not just whitespace
                    title = line.strip()
                    body_start_index = i + 1
                    break
            
            # Join the rest of the lines to form the full body text
            full_body_text = "".join(lines[body_start_index:]).strip()
            
            # Split the body text into paragraphs (separated by blank lines)
            # and replace single newlines within paragraphs with spaces.
            paragraphs = [p.strip().replace('\n', ' ') for p in full_body_text.split('\n\n') if p.strip()]
            
            return title, paragraphs
    except FileNotFoundError:
        return "File not found", []

# --- Main Script ---

# Define file paths
demo_dir = os.path.join(script_dir, "__demo", "academicnews")
sample_dir = os.path.join(demo_dir, "eval4")

# Create the root of the JSON structure for the HTML
root = Tabs()
demo = ReviewJSON(root)

# Define options for the user's agreement decision
agreement_options = [
    MultiRowOption(label="Yes", value="yes", color="success"),
    MultiRowOption(label="No", value="no", color="danger")
]
count = 0
# Create tabs for each category
for article in os.listdir(sample_dir):
    if not article.endswith(".txt"):
        continue
    title, body_paragraphs = read_article_file(article, sample_dir)
    # Create main column for this tab
    main_column = Column()
    count += 1
    root.add_tab(tabName=str(count), block=main_column)

    main_column.add_column([
        Text(title=title, titleSize=3, body=body_paragraphs)
    ])
    user_question = MultiRowChecked(rowLabel="Your Assessment", id={0: f"{article}_science_decision"},
 options=agreement_options)
    user_question.add_row(id={1: article}, text="Do you think this is a scientific article?")

    # user_question = MultiRowSelect(
    #         rowLabels=["Your Assessment"],
    #         questions=[MultiRowSelectQuestion(
    #             label="Yes or No?",
    #             id={1: f"{article}_science_decision"},
    #             options=agreement_options
    #         )]
    #     )
    # user_question.add_row(id={0:article},text=["Do you think this is a scientific article?"])


    main_column.add_column([
        Text(title="Prompt",
             titleSize=3,body=["You are an expert academic classifier. Your task is to analyze a news article and extract key information about its content and style.", 
"An article is 'scientific' if its primary focus is on science. This includes, but is not limited to:", 
"-Reporting on new research findings from studies, experiments, or clinical trials.",
"- Featuring interviews with or analysis from scientific experts, researchers, or authoritative figures on a scientific subject.",
"- Explaining established scientific concepts, theories, or phenomena in depth (e.g., an article explaining CRISPR technology).",
"- Discussing the process, funding, ethics, or policy related to the scientific community.",
"- Synthesizing information from multiple scientific sources to provide a broader view on a topic (e.g., a report on the state of climate change).",
"- Reporting on significant technological advancements rooted in scientific principles.",
"An article is 'non-scientific' if science is not its main focus. This includes articles on general news, politics, entertainment, sports, or opinion pieces not centered on a scientific debate. An article that only briefly mentions a statistic or a study to support a non-scientific main point should be classified as 'non-scientific'."
                     ]),
        user_question
    ])
# --- Generate and Save Files ---

# Create the JSON for the review tool
output_json = demo.get_json()

# Ensure the output directory exists
output_dir = os.path.join(demo_dir, "classification_review")
os.makedirs(output_dir, exist_ok=True)

# Save the JSON file
json_path = os.path.join(output_dir, "classification_review.json")
with open(json_path, 'w') as f:
    f.write(output_json)

print(f"Successfully generated {json_path}")

# Create the HTML files
review = Review(targetFolder=output_dir, block=output_json, evalTitle="Article Classification Review", serverURL="https://www.kv.econlabs.org/")
review.create(reviewers=["reviewer1", "reviewer2", "reviewer3"])

print(f"Successfully created HTML review files in {output_dir}")