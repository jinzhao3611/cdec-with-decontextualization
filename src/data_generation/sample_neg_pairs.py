import yaml, json, csv
from pathlib import Path
from os import PathLike
from typing import List, Tuple, Any, Union

import random

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend to avoid display issues
import matplotlib.pyplot as plt

# Load the config file
root_dir = Path(__file__).resolve().parent.parent
config_path = root_dir / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Access paths from the config file
data_dir = root_dir / config['paths']['data_dir']
model_dir = root_dir / config['paths']['models_dir']
output_dir = root_dir / config['paths']['output_dir']


def sample_negative_pairs(input_file: Union[str, PathLike], output_file: Union[str, PathLike], lower: float, higher: float, sample_size: int):
    # Create a list to store valid lines
    valid_lines = []

    # Open the input file and read lines
    with open(input_file, 'r') as infile:
        for line in infile:
            # Split the line to extract the distance score (assuming the score is the last element on each line)
            parts = line.strip().split('\t')

            # Make sure there are at least 3 elements (event pair and score) before checking
            if len(parts) > 2:
                try:
                    # Get the distance score (last element) and convert to float
                    score = float(parts[-1])
                    # Check if the score is within the given range
                    if higher > score >= lower:
                        # Add valid line to the list
                        valid_lines.append(line)
                except ValueError:
                    # If conversion to float fails, skip this line
                    continue

    # Sample the specified number of lines (or all valid lines if sample_size is greater than available lines)
    sampled_lines = random.sample(valid_lines, min(sample_size, len(valid_lines)))

    # Write the sampled lines to the output file
    with open(output_file, 'w') as outfile:
        for line in sampled_lines:
            uid1, uid2, score = line.split()
            outfile.write(f"{uid1}\t{uid2}\t0\t{topic}\t{source}\n")

    print(f"Sampled {len(sampled_lines)} results saved to {output_file}")





if __name__ == '__main__':
    pos_count = {"shifa#alarabiya_news": 3265,
                 "shifa#israel_national_news": 3842,
                 "putin#google_news1":5594,
                 "putin#google_news2": 4359,
                 "hong_kong#china_daily": 984,
                 "hong_kong#google_news": 1618,
                 "rittenhouse#google_news": 6136,
                 "rittenhouse#federalist": 796,
                 }
    lower = 0.95
    higher = 1.00

    for topic_source in pos_count:
        topic, source = topic_source.split("#")
        score_file = Path.joinpath(output_dir, f"yu_output/{topic}_{source}_scores.txt")
        sampled_neg_pairs = Path.joinpath(output_dir, f"train_prep/sampled_neg_pairs/{topic}_{source}_dumb_neg_pairs.tsv")
        sample_negative_pairs(score_file, sampled_neg_pairs, lower=lower, higher=higher, sample_size=pos_count[topic_source]*10)

    total_count = 0
    for subtopic in pos_count:
        total_count += pos_count[subtopic]
    print(total_count)


