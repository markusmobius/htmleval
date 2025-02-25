import json
from src.utils.load_sample import *
from src.prompts.json_to_html import *

def find_matched_articles_info(uids, articles):
    '''Uses the uids of the articles in the event to find the articles in the sampled articles'''
    matched_articles = []
    for article in articles:
        if article.uid in uids:
            matched_articles.append(article)
    return matched_articles

def get_uids(event):
    '''Returns the uids of the articles in the event'''
    uids = []
    for article in event['articles']:
        uids.append(article[1])
    return uids

def get_actions_dict(event):
    actions = set([x['corresponding_cluster'] for x in event['classified_fragments']])
    actions_and_their_fragments = {}
    for action in actions:
        actions_and_their_fragments[action] = [x['fragment'] for x in event['classified_fragments'] if x['corresponding_cluster'] == action]
    return actions_and_their_fragments

def return_text(event, article_pool):
    articles_to_match_uids = [article[1] for article in event['articles']]
    article_texts = []
    article_texts.append(json.loads(event['label'])['one sentence summary'])
    for article in article_pool.articles:
        if article.uid in articles_to_match_uids:
            article_dict = {}
            article_dict['uid'] = article.uid
            article_dict['text'] = article.get_clean_text(config_file_path = "evaluations\config_evaluation_90articles_2024_10_30_events_part_1.json")
            article_dict['publisher'] = article.meta['publisher']
            article_texts.append(article_dict)
    return article_texts

def create_list_of_actions(classified_fragment_for_single_event):
    list_of_dicts = []

    dictionary = {}
    set_of_actions = set([(entry['action'], entry['actor']) for entry in classified_fragment_for_single_event])
    for entry in set_of_actions:
        action = entry[0]
        actor = entry[1]
        dictionary['action'] = action
        dictionary['actor'] = actor
        dictionary['arguments'] = []
        ## Go through all the elements in classified_fragment_for_single_event, check which have action == action. Create a set of their 'arguments'. Then go through the resulting set and create a dictionary with 'argument' and 'sentences' for each argument.
        list_of_arguments = set([element['argument'] for element in classified_fragment_for_single_event if element['action'] == action])

        for argument in list_of_arguments:
            dictionary['arguments'].append({"argument": argument, "sentences": [element['sentences'] for element in classified_fragment_for_single_event if element['action'] == action and element['argument'] == argument][0]})
        list_of_dicts.append(dictionary)
    return list_of_dicts

def create_list_of_all_actions(classified_fragments):
    ## creates flattened list of all actions for all events
    list_of_all_actions = []
    for classified_fragment in classified_fragments:
        list_of_all_actions += create_list_of_actions(classified_fragment)
    return list_of_all_actions