import os
import sys
import re

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

def parse_clusters_file(file_path):
    """Parse the clusters_summary.txt file and return cluster data"""
    clusters = []
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split by cluster headers
    cluster_sections = re.split(r'--- CLUSTER (\d+) ---', content)[1:]  # Skip first empty element
    
    # Process pairs of (cluster_id, cluster_content)
    for i in range(0, len(cluster_sections), 2):
        cluster_id = int(cluster_sections[i])
        cluster_content = cluster_sections[i + 1].strip()
        
        # Extract cluster topic
        topic_match = re.search(r'Topic: (.*)', cluster_content)
        cluster_topic = topic_match.group(1) if topic_match else "N/A"

        # Extract coherence score
        coherence_match = re.search(r'GPT Coherence Score: (\d+)/10', cluster_content)
        coherence_score = coherence_match.group(1) if coherence_match else "N/A"
        
        # Extract distortion
        distortion_match = re.search(r'Distortion: ([\d.]+)', cluster_content)
        distortion = distortion_match.group(1) if distortion_match else "N/A"
        
        # Extract opinions
        opinions_section = re.search(r'Opinions:\s*(.*)', cluster_content, re.DOTALL)
        opinions = []
        if opinions_section:
            opinion_lines = opinions_section.group(1).strip().split('\n')
            opinions = [line.strip('- ').strip() for line in opinion_lines if line.strip().startswith('-')]
        
        clusters.append({
            'id': cluster_id,
            'topic': cluster_topic,
            'coherence_score': coherence_score,
            'distortion': distortion,
            'opinions': opinions
        })
    
    return clusters

# Parse cluster data
clusters_data = parse_clusters_file('__demo/cluster1/clusters_topics.txt')

#create the demo.json file from scratch
#root block are tabs
root=Tabs()
demo = ReviewJSON(root)

# Create tabs for each cluster
for cluster in clusters_data:
    col=Column()
    #add a nested side-by-side Column
    nestedCol=Column()
    
    # Create cluster description with real data
    cluster_description = [
        f"Cluster {cluster['id']}",
        f"Topic: {cluster['topic']}",
        f"GPT Coherence Score: {cluster['coherence_score']}/10",
        f"Distortion: {cluster['distortion']}"
    ]
    
    nestedCol.add_column([
        Text(title="Cluster Description", titleSize=4, body=cluster_description, scrollable=True)
    ])
    
    # Use opinions instead of article titles
    nestedCol.add_column([
        Text(title="Opinions", titleSize=4, body=cluster['opinions'], scrollable=True, is_table=True),
    ])
    
    options=[
        MultiRowOption(label="No",value ="no",color="danger"),
        MultiRowOption(label="Yes",value ="yes",color="success")
    ]
    multi=MultiRowChecked(rowLabel="Question",id={1:"appropriate"},options=options)
    multi.add_row(id={cluster['id']:"cluster"},text="Is this cluster appropriate?")
    col.add_column([nestedCol, multi])
    root.add_tab(tabName=str(cluster['id']),block=col)

#now we create the JSON
json=demo.get_json()

#save demo json
with open(os.path.join("__demo","cluster1","demo.json"), 'w') as f:
    f.write(json)

#now we create the HTML files
review=Review(targetFolder="__demo/cluster1",block=json,evalTitle="cluster1", serverURL="https://www.kv.econlabs.org/")

# Change to the correct directory for the Review class to find the template
os.chdir(os.path.dirname(os.path.abspath(__file__)))
review.create(reviewers=["reviewer1","reviewer2"])