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

topic = "putin"
source = "google_news2"

with open(Path.joinpath(data_dir, f"decont_articles/{topic}/manual_change_event_mapped_pped_{topic}_{source}_decont.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

num_sentences = 0
num_events = 0
num_articles = 0
num_tokens_original = 0
num_tokens_decont = 0


for article_uid in data:
    num_articles += 1
    decont_sentences = data[article_uid]["decont_sents"]
    original_sentences = data[article_uid]["ori_sents"]
    num_sentences += len(decont_sentences)

    for sent_text in decont_sentences:
        num_tokens_decont += len(sent_text.split())

    for sent_text in original_sentences:
        num_tokens_original += len(sent_text.split())

    # Go through each sentence
    for sentence_id, sentence_wz_info in enumerate(data[article_uid]["event_info"]):
        for e in sentence_wz_info["events"]:
            num_events += 1
            # Iterate over tokens to find events
            trigger = e[0].replace('_EVENT', '')

print(f"num_articles: {num_articles}\nnum_sentences:{num_sentences}\nnum_events: {num_events}\nnum_tokens_original: {num_tokens_original}\nnum_tokens_decontext:{num_tokens_decont}")
