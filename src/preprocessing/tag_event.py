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

def tag_event(topic, source):
    articles_wz_tagged_event = {}
    with open(data_dir.joinpath(f"articles_original/{topic}/{source}.json"), "r") as f:
        articles = json.load(f)
    for article_id in articles:
        sentences = articles[article_id]["sentences"]
        for event in articles[article_id]["events"]:
            sent_id, token_start, token_end = [int(item) for item in event['event_loc'].split("_")]
            sentences[sent_id-1][token_start] = sentences[sent_id-1][token_start] + "_EVENT"
        articles_wz_tagged_event[article_id] = '\n'.join([' '.join(sent) for sent in sentences])

    with open(data_dir.joinpath(f"event_detected/{topic}/{source}.json"), "w") as f:
        json.dump(articles_wz_tagged_event, f, indent=2)


if __name__ == '__main__':
    topic = "rittenhouse"
    source = "federalist"
    tag_event(topic, source)