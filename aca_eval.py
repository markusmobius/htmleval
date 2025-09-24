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

def load_classification_results(file_path):
    """Load the classification results JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get('detailed_results', [])
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []

def read_article_file(filename, article_dir):
    """Read an article file and extract title and body."""
    file_path = os.path.join(article_dir, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            lines = content.split('\n')
            title = lines[0] if lines else "No title"
            body = '\n'.join(lines[1:]) if len(lines) > 1 else "No content"
            return title, body
    except FileNotFoundError:
        return "File not found", "File not found"

def categorize_articles(results):
    """Categorize articles into 4 groups based on original_label and gpt_classification."""
    categories = {
        'science_to_scientific': [],
        'science_to_non_scientific': [],
        'non_science_to_scientific': [],
        'non_science_to_non_scientific': []
    }

    for article in results:
        original = article.get('original_label', '')
        gpt_class = article.get('gpt_classification', '')

        if original == 'science' and gpt_class == 'scientific':
            categories['science_to_scientific'].append(article)
        elif original == 'science' and gpt_class == 'non-scientific':
            categories['science_to_non_scientific'].append(article)
        elif original == 'non_science' and gpt_class == 'scientific':
            categories['non_science_to_scientific'].append(article)
        elif original == 'non_science' and gpt_class == 'non-scientific':
            categories['non_science_to_non_scientific'].append(article)

    return categories

# --- Main Script ---

# Define file paths
demo_dir = os.path.join(script_dir, "__demo", "academicnews")
scientific_dir = os.path.join(demo_dir, "science_articles")
non_scientific_dir = os.path.join(demo_dir, "non_science_articles")
classification_results_path = os.path.join(demo_dir, 'python_server_article_classification_results_seed42.json')

# Load data
classification_results = load_classification_results(classification_results_path)

if not classification_results:
    print("Could not load classification results. Exiting.")
    sys.exit(1)

# Categorize articles
categories = categorize_articles(classification_results)

# Create the root of the JSON structure for the HTML
root = Tabs()
demo = ReviewJSON(root)

# Define options for the user's agreement decision
agreement_options = [
    MultiRowOption(label="Yes", value="yes", color="success"),
    MultiRowOption(label="No", value="no", color="danger")
]

# Tab configurations
tab_configs = [
    {
        'name': 'Science → Scientific',
        'key': 'science_to_scientific',
        'description': 'Articles originally labeled as Science that GPT classified as Scientific'
    },
    {
        'name': 'Science → Non-Scientific',
        'key': 'science_to_non_scientific',
        'description': 'Articles originally labeled as Science that GPT classified as Non-Scientific'
    },
    {
        'name': 'Non-Science → Scientific',
        'key': 'non_science_to_scientific',
        'description': 'Articles originally labeled as Non-Science that GPT classified as Scientific'
    },
    {
        'name': 'Non-Science → Non-Scientific',
        'key': 'non_science_to_non_scientific',
        'description': 'Articles originally labeled as Non-Science that GPT classified as Non-Scientific'
    }
]

# Create tabs for each category
for tab_config in tab_configs:
    articles_in_category = categories[tab_config['key']]

    if not articles_in_category:
        continue

    # Create main column for this tab
    main_column = Column()
    root.add_tab(tabName=tab_config['name'], block=main_column)

    # Add description
    main_column.add_column([
        Text(title=f"{tab_config['name']} ({len(articles_in_category)} articles)",
             titleSize=3,
             body=[tab_config['description']])
    ])

    # Create article selection using MultiRowSelect
    article_options = []
    for i, article in enumerate(articles_in_category):
        filename = article.get('filename', f'article_{i}')
        title = article.get('title', 'Untitled')
        article_options.append(
            MultiRowOption(label=f"{filename} - {title[:50]}{'...' if len(title) > 50 else ''}",
                         value=str(i), color="primary")
        )

    # File selection using MultiRowSelect
    # file_selector = MultiRowSelect(
    #     rowLabels=["Select Article"],
    #     questions=[MultiRowSelectQuestion(
    #         label="Choose an article to review:",
    #         id={1: f"file_selection_{tab_config['key']}"},
    #         options=article_options
    #     )]
    # )
    # file_selector.add_row(
    #     id={0: f"select_{tab_config['key']}"},
    #     text=["Available articles in this category:"]
    # )

    # main_column.add_column([file_selector])
    candidate_tabs = Tabs()

    # Create content for each article (will be shown based on selection)
    for i, article in enumerate(articles_in_category):
        filename = article.get('filename', '')
        # Determine which directory to read from based on original label
        article_dir = scientific_dir if article.get('original_label') == 'science' else non_scientific_dir
        title, body = read_article_file(filename, article_dir)

        # Create two-column layout for article content
        article_column = Column()

        # Left column: Article content
        article_column.add_column([
            Text(title="Article Title", titleSize=4, body=[title]),
            Text(title="Article Content", titleSize=5, body=[body], scrollable=True)
        ])

        # Right column: GPT analysis and user question
        gpt_info = [
            f"GPT Confidence: {article.get('gpt_confidence', 'N/A')}",
            f"GPT Reasoning: {article.get('gpt_reasoning', 'N/A')}"
        ]

        user_question = MultiRowSelect(
            rowLabels=["Your Assessment"],
            questions=[MultiRowSelectQuestion(
                label="Do you agree with GPT classification?",
                id={1: "agreement_decision"},
                options=agreement_options
            )]
        )
        user_question.add_row(
            id={0: f"agree_{tab_config['key']}_{i}"},
            text=[f"GPT classified this as: {article.get('gpt_classification', 'N/A')}"]
        )

        article_column.add_column([
            Text(title="GPT Analysis", titleSize=4, body=gpt_info),
            user_question
        ])

        # Add article content to tab column (this creates a conditional display)
        candidate_tabs.add_tab(tabName=f"{filename}", block=article_column)

    main_column.add_column([candidate_tabs])

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
review.create(reviewers=["reviewer1", "reviewer2"])

print(f"Successfully created HTML review files in {output_dir}")