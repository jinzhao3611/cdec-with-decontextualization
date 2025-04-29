import json
from collections import Counter
import pandas as pd

def check_duplicates_in_yu_input(topic, source):
    file_path = f"/Users/jinzhao/schoolwork/cdec_naacl2/data/yu_input/{topic}/{source}/{topic}_{source}.final"

    pair_ids = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            if line.strip():
                event1_uid, event2_uid, _,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_  = line.split("\t")
                pair_ids.append(f"{event1_uid}+{event2_uid}")

    # Count occurrences of each element
    counts = Counter(pair_ids)
    # Find and print elements that appear more than once
    duplicates = [item for item, count in counts.items() if count > 1]

    num_duplicate = len(duplicates)
    total_pairs = len(pair_ids)
    print(f"number of duplicated pairs: {num_duplicate}/{total_pairs}\n")
    # print(f"Duplicates found: {duplicates}")


if __name__ == '__main__':
    topic = "putin"
    source = "google_news2"

    check_duplicates_in_yu_input(topic, source)

