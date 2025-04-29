import json
from data_path import DECONT_ARTICLE_PATH, ARTICLE_PATH


def compare_length(ori_article_json_file, decont_article_jsonl_file):
    decont_dict = dict()
    with open(decont_article_jsonl_file, "r") as f:
        for line in f:
            line_dict = json.loads(line)
            decont_dict.update(line_dict)

    with open(ori_article_json_file, "r") as f:
        ori_dict = json.load(f)

    assert len(decont_dict) == len(ori_dict)
    print(f"article number: {len(decont_dict)}")
    for k in ori_dict:
        ori_sentences = ori_dict[k].split("\n")
        decont_sentences = decont_dict[k]
        if len(ori_sentences) != len(decont_sentences):
            print(k, len(ori_sentences), len(decont_sentences))
            print(
                f"article {k} has different number of sentences: "
                f"ori={len(ori_sentences)}, decont={len(decont_sentences)}.")


if __name__ == '__main__':
    ori_article_json_file = ARTICLE_PATH / "hk_google_news.json"
    decont_article_jsonl_file = DECONT_ARTICLE_PATH / "hk_google_news_decont.jsonl"
    compare_length(ori_article_json_file, decont_article_jsonl_file)
