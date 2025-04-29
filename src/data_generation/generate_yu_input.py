import yaml, json
from pathlib import Path
from typing import List, Tuple, Any
import pandas as pd
from collections import Counter

# Load the config file
root_dir = Path(__file__).resolve().parent.parent
config_path = root_dir / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Access paths from the config file
data_dir = root_dir / config['paths']['data_dir']
model_dir = root_dir / config['paths']['models_dir']
output_dir = root_dir / config['paths']['output_dir']

def get_sentences_given_condition(event_type:str, cluster_number:int) -> List[Tuple[List[str], int, int, str]]:
    df = pd.read_csv(Path.joinpath(output_dir, f"article_clusters/{topic}/{source}.csv"))

    # Convert the DataFrame into a dictionary where the Cluster is the key, and the Article is the value
    # We will group the articles_original by Cluster since multiple articles_original can belong to the same cluster.
    cluster_dict = df.groupby('Cluster')['Article'].apply(list).to_dict()
    # Now cluster_dict will have clusters as keys and lists of articles_original as values
    # print(cluster_dict)

    # find all the sentences in one lemma cluster
    with open(Path.joinpath(data_dir, f"articles_decontext/{topic}/{source}.json"), "r") as f:
        articles = json.load(f)

    result = []
    for article_id in articles:
        for event in articles[article_id]["events"]:
            if event['event_type'] == event_type and article_id in cluster_dict[cluster_number]:
                try:
                    sent_id, token_start, token_end = [int(item) for item in event['event_loc'].split("_")]
                except ValueError as e:
                    print(f"Error processing event_loc: {event['event_loc']}")
                    raise e  # Optionally re-raise the exception after logging
                sentence = articles[article_id]["decont_sentences"][sent_id-1]
                event_uid = f"{article_id}#{event['event_loc']}"
                result.append((sentence, token_start, token_end, event_uid))
    return result

def pair_up(sentences: List[Any]) -> List[Tuple[Any, Any]]:
    # turn a list into a list of pairs
    pairs = []
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            pairs.append((sentences[i], sentences[j]))
    return pairs

def generate_yu_input(event_type:str, cluster_number:int) -> None:
    sentences_wz_info = get_sentences_given_condition(event_type, cluster_number)
    # event_uids_in_sentences_wz_info = [ele[3] for ele in sentences_wz_info]
    # print(event_uids_in_sentences_wz_info)
    #
    # # Count occurrences of each element
    # counts = Counter(event_uids_in_sentences_wz_info)
    # # Find and print elements that appear more than once
    # duplicates = [item for item, count in counts.items() if count > 1]
    #
    # num_duplicate = len(duplicates)
    # print(f"number of duplicated pairs: {num_duplicate}\n")
    # print(f"Duplicates found: {duplicates}")


    pairs = pair_up(sentences_wz_info)
    with open(Path.joinpath(data_dir, f"yu_input/{topic}/{source}/{event_type}_{cluster_number}.txt"), "w") as outfile:
        for pair in pairs:
            event_uid1 = pair[0][3]
            sent1 = " ".join(pair[0][0])
            loc1 = f"{pair[0][1]}\t{pair[0][2]}\t-1\t-1\t-1\t-1\t-1\t-1\t-1\t-1"
            event_uid2 = pair[1][3]
            sent2 = " ".join(pair[1][0])
            loc2 = f"{pair[1][1]}\t{pair[1][2]}\t-1\t-1\t-1\t-1\t-1\t-1\t-1\t-1"
            outfile.write(f"{event_uid1}\t{event_uid2}\t{sent1}\t{loc1}\t{sent2}\t{loc2}\t0\n")

if __name__ == '__main__':
    topic = "putin"
    source = "google_news2"
    cluster_num = 10

    event_types = ["ACTION", "ASPECTUAL", "COPULA", "MENTAL", "REPORT"]
    cluster_numbers = list(range(cluster_num))
    for cluster_number in cluster_numbers:
        for event_type in event_types:
            generate_yu_input(event_type, cluster_number)