import json, re

import yaml
from pathlib import Path
import spacy

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")



# Load the config file
root_dir = Path(__file__).resolve().parent.parent
config_path = root_dir / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Access paths from the config file
data_dir = root_dir / config['paths']['data_dir']
model_dir = root_dir / config['paths']['models_dir']
output_dir = root_dir / config['paths']['output_dir']

#

topic = "putin"
source = "google_news"

sample_input_file_path = Path.joinpath(data_dir, f"event_detected/{topic}/{source}.json")
sample_output_file_path = Path.joinpath(data_dir, f"decontextualized/{topic}/{source}.jsonl")

with open(sample_input_file_path, 'r') as f:
    input_dict = json.loads(f.read())

with open(sample_output_file_path, "r") as f:
    for line in f.readlines():
        article_uid, article = list(json.loads(line).items())[0]
        sentences_decon = [element for element in article.split('\n\n') if element.strip()]
        remove_list_numbers_article = re.sub(r'\d+\.\s*', "", article)
        doc_decon = nlp(remove_list_numbers_article)
        sentences_decon = [sent.text for sent in doc_decon.sents]

        doc_orig = nlp(input_dict[article_uid])
        sentences_orig = [sent.text for sent in doc_orig.sents]


        if len(sentences_orig) == len(sentences_decon):
            for o, d in zip(sentences_orig, sentences_decon):
                # print(o)
                # print(d)
                # print("********************")
                pass
        else:
            print(f"not match in uid: {article_uid}")
            print(len(sentences_orig))
            print(len(sentences_decon))
            for o, d in zip(sentences_orig, sentences_decon):
                print(o)
                print(d)
                print("********************")
            break


