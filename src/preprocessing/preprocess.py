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

topic_ids = {
    "putin+election":"00",
    "shifa+raid":"01",
    'al+shifa+hospital+raid':"01",
    'Hong+Kong+protest+july+1':"02",
    'rittenhouse':'03'
}
api_ids = {
    "google_news": "00",
    "aljazeera":"01",
    "the_jerusalem_post": "02",
    "alarabiya_news": "03",
    "israel_national_news": "04",
    "the_times_of_israel": "05",
    "baidu_news":"06",
    "the_paper":"07",
    "yandex_news":"08",
    "federalist":"09"
}

def preprocess(source, topic):
    # Path to the original JSONL file
    input_file_path = Path.joinpath(data_dir, f"raw_data/{topic}/{source}.jsonl")
    # Path to the modified JSONL file
    output_file_path = Path.joinpath(data_dir, f"raw_data_preprocessed/{topic}/{source}.jsonl")

    # Open the input and output files
    with open(input_file_path, 'r', encoding='utf-8') as input_file, open(output_file_path, 'w') as output_file:
        for i, line in enumerate(input_file):
            data = json.loads(line)  # Parse the JSON data
            updated_data = data
            # todo: deduplication, filter out the articles that that only mentioned our topic
            tokens = updated_data.get('content', '').split()
            title = updated_data.get('title', '')
            conditions = [len(tokens) > 30]
            updated_data["uid"] = f"{topic_ids[topic]}_{api_ids[source]}_{str(i)}"

            if all(conditions):  # Replace 'your_field_name' with your actual field name
                json.dump(updated_data, output_file, ensure_ascii=False)  # Write the JSON data to the output file
                output_file.write('\n')  # Write a newline character to separate JSON objects


if __name__ == '__main__':
    # right now the preprocess do nothing but add uid to it
    topic = 'rittenhouse'
    preprocess(source="google_news", topic=topic)