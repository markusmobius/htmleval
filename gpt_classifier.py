import json
import os
import random
import sys
import argparse
import shutil
from tqdm import tqdm
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

# Add the path to your library and import the new classes
script_dir = os.path.dirname(os.path.abspath(__file__))
gpt_query_path = os.path.join(script_dir, 'GPTQuery')
sys.path.append(gpt_query_path)
print(f"Added {gpt_query_path} to sys.path")
from LlmLib import Chat, Llm

def load_human_reviews(review_file_path):
    """Loads human review data from the specified JSON file."""
    print(f"Loading human reviews from {review_file_path}...")
    try:
        with open(review_file_path, 'r', encoding='utf-8') as f:
            review_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Review file not found at {review_file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {review_file_path}")
        return {}

    human_labels = {}
    for key, value in review_data.get('variables', {}).items():
        try:
            # The key is a JSON string array, e.g., "[\"sci-829.txt_science_decision\",\"sci-829.txt\"]"
            key_list = json.loads(key)
            filename = key_list[1]
            # Convert "yes"/"no" to "science"/"non_science"
            human_labels[filename] = "science" if value == "yes" else "non_science"
        except (json.JSONDecodeError, IndexError):
            print(f"Warning: Could not parse key from review file: {key}")
            continue
    
    print(f"Loaded {len(human_labels)} human-reviewed labels.")
    return human_labels

def load_articles_from_folder(folder_path):
    """
    Load all articles from a single folder.
    Infers the 'original_label' from the filename prefix ('sci-' or 'non-').
    """
    articles = []
    if not os.path.exists(folder_path):
        print(f"Error: Folder {folder_path} does not exist.")
        return articles
    
    files_to_load = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    print(f"Loading all {len(files_to_load)} articles from {os.path.basename(folder_path)}")
    
    for filename in files_to_load:
        filepath = os.path.join(folder_path, filename)
        try:
            # Infer label from prefix
            if filename.startswith('sci-'):
                label = 'science'
            elif filename.startswith('non-'):
                label = 'non_science'
            else:
                label = 'unknown'

            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                # Custom parsing for the new format
                title = "No Title"
                body_start_index = 0
                for i, line in enumerate(lines):
                    if line.strip():
                        title = line.strip()
                        body_start_index = i + 1
                        break
                
                text = "".join(lines[body_start_index:]).strip()

                articles.append({
                    'filename': filename,
                    'filepath': filepath,
                    'title': title,
                    'text': text,
                    'original_label': label, # Based on filename prefix
                })
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    return articles

def create_classification_chat(article, model_name):
    """
    Creates an LlmLib.Chat object for classifying a single article.
    """
    system_prompt = """
    You are an expert academic classifier. Your task is to analyze a news article and extract key information about its content and style.

    An article is "scientific" if its primary focus is on science. This includes, but is not limited to:
    - Reporting on new research findings from studies, experiments, or clinical trials.
    - Featuring interviews with or analysis from scientific experts, researchers, or authoritative figures on a scientific subject.
    - Explaining established scientific concepts, theories, or phenomena in depth (e.g., an article explaining CRISPR technology).
    - Discussing the process, funding, ethics, or policy related to the scientific community.
    - Synthesizing information from multiple scientific sources to provide a broader view on a topic (e.g., a report on the state of climate change).
    - Reporting on significant technological advancements rooted in scientific principles.

    An article is "non-scientific" if science is not its main focus. This includes articles on general news, politics, entertainment, sports, or opinion pieces not centered on a scientific debate. An article that only briefly mentions a statistic or a study to support a non-scientific main point should be classified as "non-scientific".
    """
    
    user_prompt = f"""
    Please analyze the following news article:

    TITLE: {article['title']}
    PUBLISHER: {article['publisher'] if 'publisher' in article else 'Unknown'}
    CONTENT: {article['text']}

    Provide your analysis as a JSON object with the following two fields:
    1. "science topics": Provide a list of the main scientific topics/debates discussed in the article. If none, return a list with the single element "no science topic".
    2. "reasoning": Briefly explain why these topics are or are not present.

    Example Response 1 (Study-based):
    {{
      "science topics": ["Alzheimer's disease", "drug treatment", "dementia caregiving"],
      "reasoning": "The article reports on a specific study regarding a new drug for dementia and discusses the challenges in treatment, which is a clear focus on scientific and medical research."
    }}

    Example Response 2 (Expert-based):
    {{
      "science topics": ["vaccine safety", "immunology", "public health policy"],
      "reasoning": "The article is structured around an interview with an expert in immunology who provides their perspective on vaccine safety, making it a scientific article focused on expert analysis."
    }}
    """
    
    chat = Chat(requestJSON=True, model=model_name)
    chat.AddSystemMessage(system_prompt)
    chat.AddUserMessage(user_prompt)
    return chat

def main(args):
    """
    Main function to load, classify, and evaluate articles.
    """
    # Check for the required environment variable
    if 'llmcode' not in os.environ:
        print("Error: The 'llmcode' environment variable is not set.")
        print("Please set it before running the script.")
        # You can set it temporarily in your shell like this:
        # export llmcode='tuantunaheringbearings'
        return

    # Set seed for reproducibility
    random.seed(args.seed)
    print(f"Using random seed: {args.seed}")

    # --- MODIFIED: Point to the evaluation sample directory ---
    base_dir = os.path.join(script_dir, "__demo", "academicnews")
    sample_folder = os.path.join(base_dir, "eval4")
    review_file = os.path.join(base_dir, "classification_review", "reviewer1_closed.json")

    print("\nLoading articles from folder...")
    all_articles = load_articles_from_folder(sample_folder)
    
    if not all_articles:
        print("No articles found. Please check the folder path.")
        return
    
    random.shuffle(all_articles)
    print(f"\nTotal articles to analyze: {len(all_articles)}")
    
    # --- MODIFIED: Load human review data for evaluation ---
    human_labels = load_human_reviews(review_file)
    if not human_labels:
        print("No human labels to compare against. Exiting.")
        return

    # --- REMOVED: Copying logic is not needed for this task ---

    print("\nPreparing analysis chats...")
    chats = [create_classification_chat(article, args.model) for article in all_articles]
    
    print(f"Sending chats to the LLM service ({args.batch_size} in parallel)...")
    llm = Llm(batch_size=args.batch_size)
    # Execute chats with required tags
    tags = ["academic-classifier", f"seed-{args.seed}"]
    responses = llm.execute_chats(chats, tags=tags)
    
    print("\nProcessing responses...")
    analysis_results = []
    y_true = []
    y_pred = []
    
    # Create a dictionary for quick lookup of GPT results by filename
    gpt_results = {}

    for i, response in enumerate(tqdm(responses, desc="Processing results")):
        article = all_articles[i]
        result = {}
        
        if response.get("error"):
            result = {"reasoning": response['error'], "science topics": []}
        else:
            raw_answer = response.get("answer", "{}")
            try:
                # Robust JSON parsing
                json_start = raw_answer.find('{')
                json_end = raw_answer.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    clean_json_str = raw_answer[json_start:json_end]
                    result = json.loads(clean_json_str)
                else:
                    raise json.JSONDecodeError("No JSON object found in response", raw_answer, 0)
            except (json.JSONDecodeError, TypeError):
                result = {"reasoning": f"JSON decode error: {raw_answer}", "science topics": []}

        # Determine GPT's classification
        gpt_topics = result.get('science topics', [])
        gpt_label = "non_science" if not gpt_topics or gpt_topics == ["no science topic"] else "science"

        # Store GPT's label for later comparison
        gpt_results[article['filename']] = gpt_label

        analysis_results.append({
            'filename': article['filename'],
            'original_label': article['original_label'],
            'gpt_label': gpt_label,
            'gpt_science_topics': gpt_topics,
            'gpt_reasoning': result.get('reasoning', 'N/A'),
        })
    
    # --- MODIFIED: Build y_true and y_pred by comparing against human labels ---
    print("\nAligning GPT results with human reviews for evaluation...")
    for filename, human_label in human_labels.items():
        if filename in gpt_results:
            y_true.append(human_label)
            y_pred.append(gpt_results[filename])
        else:
            print(f"Warning: Human-reviewed article '{filename}' not found in GPT results. Skipping from evaluation.")

    # --- Save detailed results to JSON ---
    output_data = {
        'summary': {
            'random_seed': args.seed,
            'total_articles_processed': len(all_articles),
            'total_articles_evaluated': len(y_true),
            'model': args.model,
        },
        'article_analysis': analysis_results
    }
    
    output_filename = f"gpt_classifier_evaluation_seed{args.seed}.json"
    print(f"\nSaving detailed results to {output_filename}...")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print("Results saved successfully.")

    # --- Performance Evaluation ---
    print("\n" + "="*60)
    print("         GPT CLASSIFIER PERFORMANCE REPORT")
    print("="*60)
    print(f"Compared GPT labels against HUMAN labels for {len(y_true)} articles.\n")
    
    labels = sorted(list(set(y_true)))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    print("Confusion Matrix:")
    print(" " * 12 + " ".join([f"{l:<12}" for l in labels]) + " (Predicted)")
    for i, row in enumerate(cm):
        print(f"{labels[i]:<12}" + " ".join([f"{val:<12}" for val in row]))
    print("(Actual)\n")
    
    print("Classification Report:")
    print(classification_report(y_true, y_pred, labels=labels))
    
    print(f"Overall Accuracy: {accuracy_score(y_true, y_pred):.2%}")
    print("="*60)

    # --- ADDED: Copy disagreed articles to subfolders for review ---
    print("\n--- Starting Disagreement Analysis & File Copy ---")
    
    disagreements_base_path = os.path.join(base_dir, "classification_review", "disagreements")
    human_sci_path = os.path.join(disagreements_base_path, "human_sci_gpt_non")
    human_non_path = os.path.join(disagreements_base_path, "human_non_gpt_sci")

    # Create directories, clearing them first if they exist
    shutil.rmtree(disagreements_base_path, ignore_errors=True)
    os.makedirs(human_sci_path, exist_ok=True)
    os.makedirs(human_non_path, exist_ok=True)
    print(f"Created disagreement folders in: {disagreements_base_path}")

    disagreements = {'human_sci_gpt_non': 0, 'human_non_gpt_sci': 0}
    for filename, human_label in human_labels.items():
        gpt_label = gpt_results.get(filename)
        
        # Check for disagreement
        if gpt_label and human_label != gpt_label:
            source_file = os.path.join(sample_folder, filename)
            if not os.path.exists(source_file):
                print(f"Warning: Source article '{filename}' not found for copying.")
                continue

            # Copy to the appropriate folder
            if human_label == "science" and gpt_label == "non_science":
                shutil.copy(source_file, human_sci_path)
                disagreements['human_sci_gpt_non'] += 1
            elif human_label == "non_science" and gpt_label == "science":
                shutil.copy(source_file, human_non_path)
                disagreements['human_non_gpt_sci'] += 1
            
    print("\nDisagreement Summary:")
    print(f"- Human='Science', GPT='Non-Science': {disagreements['human_sci_gpt_non']} articles copied.")
    print(f"- Human='Non-Science', GPT='Science': {disagreements['human_non_gpt_sci']} articles copied.")
    print("--- Analysis Complete ---")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate a GPT-based science article classifier.")
    # --- REMOVED: num-science and num-non-science are no longer needed ---
    parser.add_argument('--seed', type=int, default=42, help="Random seed for sampling reproducibility.")
    parser.add_argument('--batch-size', type=int, default=10, help="Number of parallel requests to send to the LLM.")
    parser.add_argument('--model', type=str, default="gpt-5-mini_2025-08-07", help="The model name to use for classification.")
    # --- REMOVED: output-sample-dir is not needed ---
    
    args = parser.parse_args()
    main(args)