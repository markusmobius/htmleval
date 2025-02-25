
import json

def escape_html_special_chars(text):
    """
    Escape special characters for HTML.
    
    :param text: The text to escape.
    :return: Escaped text.
    """
    special_chars = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        "_": ' ',
    }
    for char, escape in special_chars.items():
        text = text.replace(char, escape)
    return text

def capitalize_title(title):
    """
    Capitalize each word in the title.
    
    :param title: The title to capitalize.
    :return: Capitalized title.
    """
    return ' '.join(word.capitalize() for word in title.split())

def json_to_html(json_data, prompt_path, prompt_name, viewer_type=None, save = True):
    """
    Convert JSON data to formatted HTML string.
    
    :param json_data: JSON data containing an array of dictionaries.
    :param viewer_type: Type of viewer ("human" or "gpt") to filter content.
    :return: Formatted HTML string.
    """
    html_output = [f"<h3>{capitalize_title(escape_html_special_chars(prompt_name))}</h3>"]
    
    for index, item in enumerate(json_data):
        # Check for filter and skip if it doesn't match the viewer_type
        if 'filter' in item and item['filter'] != viewer_type:
            continue

        # Check if dealing with examples:
        if item['type'] == 'examples':
            examples = []
            for i, example in enumerate(item['content']):
                example = escape_html_special_chars(example)
                examples.append(f"<li><i>{example}</i></li>")
            text_to_add = ["<ul>"] + examples + ["</ul>"]
            text_to_add = " ".join(text_to_add)
        else:
            text_to_add = "<br>".join([escape_html_special_chars(part) for part in item['content']])
        
        html_output.append(text_to_add)

    # Save HTML Prompt
    if save == True:
        with open(f'{prompt_path}.html', 'w') as file:
            file.write("\n".join(html_output))
    
    return "\n".join(html_output)