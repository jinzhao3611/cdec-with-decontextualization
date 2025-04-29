import json, os
import re
from typing import List, Tuple, Any, Dict
import spacy

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


# Load English tokenizer, tagger, parser, NER, and word vectors
nlp = spacy.load("en_core_web_sm")

def to_mdp_input(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as input_file, open(output_file_path, 'w') as output_file:
        for line in input_file:
            data = json.loads(line)  # Parse the JSON data
            if data["language"] == "English":
                paragraph = data["content"].strip()
            else:
                paragraph = data["translation"].strip()
            uid = data["uid"]
            doc = nlp(paragraph)
            tokenized_paragraph = f"""filename:<doc id={uid}>:SNT_LIST\n2019-11-08 06:33:49+00:00\n"""
            for sent in doc.sents:
                tokenized_paragraph += " ".join([token.text.strip() for token in sent]) + "\n"
            output_file.write(tokenized_paragraph + "\n\n")



if __name__ == '__main__':
    topic = "rittenhouse"
    source = "federalist"

    to_mdp_input(input_file_path=Path.joinpath(data_dir, f"raw_data_data_preprocessed/{topic}/{source}.jsonl"), output_file_path=Path.joinpath(data_dir, f"mdp_input/{topic}_{source}.txt"))