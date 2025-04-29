import json
import timeit

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
from gensim.models import KeyedVectors
import pandas as pd

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


# Method 1: Cosine Similarity using TF-IDF
# def cosine_similarity_tfidf(article1, article2):
#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform([article1, article2])
#     return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
#
# # Method 2: Jaccard Similarity
# def jaccard_similarity(article1, article2):
#     words1 = set(article1.lower().split())
#     words2 = set(article2.lower().split())
#     intersection = words1.intersection(words2)
#     union = words1.union(words2)
#     return len(intersection) / len(union)
#
# # Method 3: Word Mover's Distance (WMD)
# def wmd_similarity(article1, article2, model):
#     doc1 = article1.lower().split()
#     doc2 = article2.lower().split()
#     return model.wmdistance(doc1, doc2)

# Method 4: Semantic Similarity using Sentence-BERT
def semantic_similarity_bert(article1, article2, model):
    embedding1 = model.encode(article1, convert_to_tensor=True)
    embedding2 = model.encode(article2, convert_to_tensor=True)
    return util.pytorch_cos_sim(embedding1, embedding2).item()

# Compare two articles_original with all methods
def compare_articles(article1, article2, sbert_model):
    results = {
        # "Cosine Similarity (TF-IDF)": cosine_similarity_tfidf(article1, article2),
        # "Jaccard Similarity": jaccard_similarity(article1, article2),
        # "Word Mover's Distance (WMD)": wmd_similarity(article1, article2, w2v_model),
        "Cosine Similarity (TF-IDF)": 0,
        "Jaccard Similarity": 0,
        "Word Mover's Distance (WMD)": 0,
        "Semantic Similarity (BERT)": semantic_similarity_bert(article1, article2, sbert_model)
    }
    return results

# Main function to compare a collection of articles_original
def compare_collection(articles, output_csv):
    # Load required models
    # w2v_model = Word2Vec.load("word2vec.model")  # Load your pre-trained Word2Vec model
    # w2v_model = KeyedVectors.load_word2vec_format(Path.joinpath(model_dir, 'GoogleNews-vectors-negative300.bin'), binary=True)
    sbert_model = SentenceTransformer('all-MiniLM-L6-v2')  # Load pre-trained Sentence-BERT model

    results = []
    # Compare all pairs of articles_original
    n = len(articles)
    for i in range(n):
        for j in range(i + 1, n):
            article1 = articles[i]["content"]
            article2 = articles[j]["content"]
            article1_id = articles[i]['uid']
            article2_id = articles[j]['uid']
            similarities = compare_articles(article1, article2,  sbert_model)
            # Append the result as a dictionary
            result = {
                "Article 1": article1_id,
                "Article 2": article2_id,
            }
            result.update(similarities)  # Add similarity scores to the dictionary
            results.append(result)  # Add the result to the list

            # for method, score in similarities.items():
            #     print(f"{method}: {score:.4f}")
    df = pd.DataFrame(results)

    # Display the DataFrame
    print(df)

    # Optionally, save the DataFrame to a CSV file
    df.to_csv(output_csv, index=False)

def run_toy_example():
    articles = [
        {"content": "This is the first article. ", "uid": "3_1"},
        {"content": "This is the first article. It talks about artificial intelligence and machine learning.",
         "uid": "3_2"},
        {"content": "The second article discusses deep learning and artificial intelligence in great detail.",
         "uid": "3_3"},
        {
            "content": "A completely different topic is discussed in the third article, which focuses on climate change and its effects.",
            "uid": "3_4"},
    ]
    # Compare the articles_original using all four methods
    # output_csv = Path.joinpath(output_dir, "article_similarities/toy.csv")
    output_csv = Path.joinpath(output_dir, "article_similarities/shifa/alarabiya_news.csv")

    compare_collection(articles, output_csv)

def run_alarabiya():
    # this source of this topic is different because it doesn't have decontextualization
    articles_path = Path.joinpath(data_dir, "raw_data/shifa/alarabiya_news.jsonl")
    articles = []
    with open(articles_path, "r") as infile:
        for line in infile:
            article_json_obj = json.loads(line.strip())
            articles.append(article_json_obj)

    output_csv = Path.joinpath(output_dir, "article_similarities/shifa/alarabiya_news.csv")
    compare_collection(articles, output_csv)

def run():
    topic = "putin"
    source = "google_news2"
    articles_path = Path.joinpath(data_dir, f"decont_articles/{topic}/manual_change_event_mapped_pped_{topic}_{source}_decont.json")
    articles = []
    with open(articles_path, "r") as infile:
        data = json.load(infile)
        for article_uid in data:
            articles.append({"uid": article_uid, "content": "\n".join(data[article_uid]['decont_sents'])})

    output_csv = Path.joinpath(output_dir, f"article_similarities/{topic}/{source}.csv")
    compare_collection(articles, output_csv)


if __name__ == '__main__':
    # run_toy_example()
    # Measure execution time
    elapsed_time = timeit.timeit(run, number=1) # run_israel_national_news takes 25min
    print(f"Elapsed time: {elapsed_time} seconds")
    # Elapsed time: 727.1367903270293 seconds



