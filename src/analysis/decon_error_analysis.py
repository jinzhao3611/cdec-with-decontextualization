import pandas as pd
import os, yaml, re, csv
from pathlib import Path
from collections import defaultdict, Counter
import tqdm

# Load the config file
root_dir = Path(__file__).resolve().parent.parent
config_path = root_dir / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Access paths from the config file
data_dir = root_dir / config['paths']['data_dir']
model_dir = root_dir / config['paths']['models_dir']
output_dir = root_dir / config['paths']['output_dir']


topic = "hk"
decont_error = set()
with open(Path.joinpath(output_dir, f"error_files/decont/{topic}_decont_on_test_errors.txt")) as f:
    for line in f.readlines():
        uid1, sent1, uid2, sent2, pred, true = line.split('\t')
        decont_error.add(f'{uid1}\t{uid2}')

ori_error = set()
with open(Path.joinpath(output_dir, f"error_files/decont/{topic}_ori_on_test_errors.txt")) as f:
    for line in f.readlines():
        uid1, sent1, uid2, sent2, pred, true = line.split('\t')
        ori_error.add(f'{uid1}\t{uid2}')


# print(decont_error - ori_error)
improved_because_of_decont = ori_error - decont_error
worsened_because_of_decont = decont_error - ori_error
# print(improved_because_of_decont)
# print(len(improved_because_of_decont))
print(worsened_because_of_decont)
print(len(worsened_because_of_decont))



