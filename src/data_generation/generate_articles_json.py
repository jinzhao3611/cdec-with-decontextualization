import json, os
import re
from lemminflect import getLemma
from typing import List, Tuple, Any, Dict


import yaml
from pathlib import Path

# Load the config file
root_dir = Path(__file__).resolve().parent.parent
config_path = root_dir / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Access paths from the config file
data_dir = root_dir / config['paths']['data_dir']
model_dir = root_dir / config['paths']['models_dir']
output_dir = root_dir / config['paths']['output_dir']
resource_dir = root_dir / config['paths']['resources_dir']

def read_word_lists() -> Dict[str,List[str]]:
    folder_path = Path.joinpath(resource_dir, "word_lists")

    # Initialize an empty dictionary to store the word lists
    word_lists_dict = {}

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):  # Only process .txt files
            file_path = os.path.join(folder_path, filename)

            # Read the contents of the file and split into a list of words
            with open(file_path, 'r', encoding='utf-8') as file:
                word_list = file.read().splitlines()  # Assuming one word per line
            # Use the file name (without extension) as the dictionary key
            key = os.path.splitext(filename)[0]
            word_lists_dict[key] = word_list

    # Now you have a dictionary with word lists from all files
    return word_lists_dict

def parse_mdp_output(topic, source):
    word_list_dict = read_word_lists()
    with open(Path.joinpath(data_dir, f"mdp_output/{topic}_{source}.txt"), "r", encoding="utf-8") as f:
        data = f.read()
        segments = data.split("\n\n\n")
        articles = {}
        for seg in segments:
            paragraph, edges = seg.split("EDGE_LIST\n")
            sentences_ = paragraph.strip().split("\n")
            sentences = sentences_[2:]
            paragraph_uid_pattern = r'\d+_\d+_\d+'
            match = re.search(paragraph_uid_pattern, sentences_[0])
            if match:
                paragraph_uid = match.group()
            else:
                print("No uid match found.")
                paragraph_uid = ""
            edge_list = edges.strip().split("\n")
            event_dict_this_paragraph_ = {}
            for edge in edge_list:
                event_id, node, parent_node_id, mod = edge.split("\t")
                # sent count from 1, token count from 0
                sent_id, token_start, token_end =[int(item) for item in event_id.split("_")]
                if sent_id > 0:
                    trigger_word = sentences[sent_id-1].split()[token_start:token_end+1]
                    event_dict_this_paragraph_[event_id] = [node, parent_node_id, mod, trigger_word]
            events = []
            for event_loc in event_dict_this_paragraph_:
                if event_dict_this_paragraph_[event_loc][0] == "Event":
                    if event_dict_this_paragraph_[event_loc][1] == '-3_-3_-3' or event_dict_this_paragraph_[event_loc][1] == '-5_-5_-5':
                        conceiver = ""
                        conceiver_loc = ""
                    else:
                        conceiver = event_dict_this_paragraph_[event_dict_this_paragraph_[event_loc][1]][3]
                        conceiver_loc = event_dict_this_paragraph_[event_loc][1]
                    trigger = event_dict_this_paragraph_[event_loc][3]
                    trigger_lemma = getLemma(trigger[0].lower(), upos='VERB')[0]
                    event_type = "ASPECTUAL" if trigger_lemma in word_list_dict['aspectual'] \
                        else "COPULA" if trigger_lemma in word_list_dict['copula'] \
                        else "MENTAL" if trigger_lemma in word_list_dict['mental'] \
                        else "REPORT" if trigger_lemma in word_list_dict['report'] \
                        else "ACTION"
                    events.append({
                        "trigger": trigger,
                        "lemma": trigger_lemma,
                        "event_loc": event_loc,
                        "mod": event_dict_this_paragraph_[event_loc][2],
                        "conceiver": conceiver,
                        "conceiver_loc": conceiver_loc,
                        "event_type": event_type
                    })

            articles[paragraph_uid] = {
                "events": events,
                "sentences": [sent.split() for sent in sentences]
            }
    with open(Path.joinpath(data_dir, f"articles_original/{topic}/{source}.json"), "w") as f:
        json.dump(articles, f, indent=2)

def parse_decontext_output(topic, source):
    word_list_dict = read_word_lists()
    with open(Path.joinpath(data_dir, f"decont_articles/{topic}/manual_change_event_mapped_pped_{topic}_{source}_decont.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
        articles = {}
        for article_uid in data:
            decont_sentences = data[article_uid]["decont_sents"]

            # List to store the result
            events = []

            # Go through each sentence
            for sentence_id, sentence_wz_info in enumerate(data[article_uid]["event_info"]):
                for e in sentence_wz_info["events"]:
                # Iterate over tokens to find events
                    trigger = e[0].replace('_EVENT', '')
                    if e[2]:
                        event_loc = f"{sentence_id + 1}_{e[2]}_{e[2]}"  # sentence_id starts from 1, token offest starts from 0, End offset is inclusive
                        trigger_lemma = getLemma(trigger.lower(), upos='VERB')[0]
                        event_type = "ASPECTUAL" if trigger_lemma in word_list_dict['aspectual'] \
                            else "COPULA" if trigger_lemma in word_list_dict['copula'] \
                            else "MENTAL" if trigger_lemma in word_list_dict['mental'] \
                            else "REPORT" if trigger_lemma in word_list_dict['report'] \
                            else "ACTION"
                        # Append the result
                        events.append({
                            "trigger": [trigger],
                            "lemma": trigger_lemma,
                            "event_loc": event_loc,
                            "mod": "",
                            "conceiver": "",
                            "conceiver_loc": "",
                            "event_type": event_type
                        })

            articles[article_uid] = {
                "events": events,
                "decont_sentences": [sent.strip().replace("_EVENT", "").split() for sent in decont_sentences]
            }
        with open(Path.joinpath(data_dir, f"articles_decontext/{topic}/{source}.json"), "w") as f:
            json.dump(articles, f, indent=2)



if __name__ == '__main__':
    # parse_mdp_output(topic="rittenhouse", source="google_news")
    topic = "putin"
    source = "google_news2"
    parse_decontext_output(topic=topic, source=source)  # only run this once






