import json
import re
from collections import defaultdict
from pathlib import Path
from data_path import DECONT_ARTICLE_PATH, ARTICLE_PATH


def add_event_uid(article: str):
    event_count = 1
    article_lst = article.split("\n")
    new_sents = []
    for sent in article_lst:
        tokens = sent.strip().split()
        for i, token in enumerate(tokens):
            if token.endswith("_EVENT"):
                tokens[i] = f"{token}-{event_count}"
                event_count += 1
        new_sents.append(" ".join(tokens))
    return "\n".join(new_sents)


def add_event_uid2file(article_json_file):
    with open(article_json_file, "r") as f:
        article_dict = json.load(f)
    new_dict = dict()

    for uid in article_dict:
        article = article_dict[uid]
        new_article = add_event_uid(article)
        new_dict[uid] = new_article
    out_f = open(Path(article_json_file).parent / (Path(article_json_file).stem + "_event_uid.json"), "w")
    json.dump(new_dict, out_f, indent=2)
    out_f.close()


def split_str2list(output_res: str):
    pattern = re.compile(r'(?=\[\d+\])')

    output_res = " ".join(output_res.split())
    pred_segs = pattern.split(output_res)
    pred_segs = [p.strip() for p in pred_segs if p.strip() and p.strip().startswith("[")]
    final_dict = dict()
    for seg in pred_segs:
        sid, text = seg.split(" ", 1)
        sid = int(sid[1:-1]) - 1
        final_dict[sid] = text
    return final_dict


def append_space_to_event_words(input_string):
    # Define the regex pattern to match words ending with _EVENT
    pattern = r'(\b\w+_EVENT\b)'

    # Use re.sub to replace each occurrence with itself followed by a space
    result_string = re.sub(pattern, r'\1 ', input_string)

    return " ".join(result_string.strip().split())


def process_gpt_res(ori_article_json_file, gpt_res_jsonl_file: str, fill: bool):
    with open(ori_article_json_file, "r") as f:
        ori_dict = json.load(f)
    out_f = open(Path(gpt_res_jsonl_file).parent / f"pped_{Path(gpt_res_jsonl_file).stem}.jsonl", "w")

    with open(gpt_res_jsonl_file, "r") as f:
        for line in f:
            line_dict = json.loads(line)
            for k in line_dict:
                ori_sentences = ori_dict[k].split("\n")
                res_str = line_dict[k]
                decont_res = split_str2list(res_str)
                decont_res_len = len(decont_res)
                if fill:
                    missing_ids = []
                    if len(ori_sentences) != decont_res_len:
                        for ori_id, ori_sent in enumerate(ori_sentences):
                            if ori_id not in decont_res:
                                decont_res[ori_id] = ori_sent
                                missing_ids.append(ori_id)
                        print(f"article {k} has different number of sentences: "
                              f"ori={len(ori_sentences)}, decont={decont_res_len}. "
                              f"Filled in original sentences with ids (0-indexed): {missing_ids}")
                    assert len(ori_sentences) == len(decont_res)
                    decont_sentences = [append_space_to_event_words(decont_res[i]) for i in range(len(ori_sentences))]
                else:
                    decont_sentences = list(append_space_to_event_words(d) for d in decont_res.values())
                ori_sentences = [append_space_to_event_words(s) for s in ori_sentences]

                out_f.write(json.dumps({k: {"decont_sents": decont_sentences, "ori_sents": ori_sentences}}) + "\n")
    out_f.close()


def extract_words_with_offsets(input_string):
    # Define the regex pattern to match words ending with _EVENT
    pattern = r'\b\w+_EVENT\b'

    # Use re.finditer to get match objects, which include offsets
    matches = re.finditer(pattern, input_string)

    # Collect words with their offsets
    results = [(match.start(), match.group()) for match in matches]

    return results


def extract_event_from_sent(sent: str, use_char_offset=False):
    if use_char_offset:
        event_tokens = extract_words_with_offsets(sent)
    else:
        event_tokens = [(i, token) for i, token in enumerate(sent.split()) if token.endswith("_EVENT")]
    event2idx = defaultdict(list)

    for i, token in event_tokens:
        event2idx[token].append(i)
    return event_tokens, event2idx


def map_events(pped_decont_jsonl_file: str):
    missing_count = 0
    multi_count = 0
    total_count = 0
    all_doc_dict = dict()
    with open(pped_decont_jsonl_file, "r") as f:
        for line in f:
            line_dict = json.loads(line)
            for k in line_dict:
                event_info_list = []
                decont_sents = line_dict[k]["decont_sents"]
                ori_sents = line_dict[k]["ori_sents"]
                for sent_idx, (decont_sent, ori_sent) in enumerate(zip(decont_sents, ori_sents)):
                    event_info_dict = dict()
                    event_info_dict["ori_sent"] = ori_sent
                    event_info_dict["decont_sent"] = decont_sent
                    event_info_dict["events"] = []

                    decont_event_tokens, decont_event2idx = extract_event_from_sent(decont_sent)
                    ori_event_tokens, ori_event2idx = extract_event_from_sent(ori_sent)

                    for ori_event_token in ori_event2idx:
                        ori_event_indices = ori_event2idx[ori_event_token]
                        ori_event_indices = [str(idx) for idx in ori_event_indices]

                        decont_event_indices = decont_event2idx.get(ori_event_token, [])
                        decont_event_indices = [str(idx) for idx in decont_event_indices]

                        if not decont_event_indices:
                            for idx in ori_event_indices:
                                event_info = [ori_event_token, idx, ""]
                                total_count += 1
                                missing_count += 1
                                event_info_dict["events"].append(event_info)
                        elif len(decont_event_indices) == len(ori_event_indices):
                            for i, idx in enumerate(ori_event_indices):
                                event_info = [ori_event_token, idx, decont_event_indices[i], "SINGLEMAPPING"]
                                event_info_dict["events"].append(event_info)
                                total_count += 1
                        else:
                            for idx in ori_event_indices:
                                event_info = [ori_event_token, idx, "-".join(decont_event_indices), "MULTIMAPPING"]
                                event_info_dict["events"].append(event_info)
                                total_count += 1
                                multi_count += 1

                    # for ori_event_idx, ori_event_token in ori_event_tokens:
                    #     event_info = [ori_event_token, ori_event_idx]
                    #
                    #     decont_event_indices = decont_event2idx.get(ori_event_token, [])
                    #     decont_event_indices = [str(idx) for idx in decont_event_indices]
                    #
                    #     total_count += 1
                    #     if not decont_event_indices:
                    #         missing_count += 1
                    #         event_info.append("")
                    #
                    #     elif len(decont_event_indices) > 1:
                    #
                    #         multi_count += 1
                    #         event_info.append("-".join(decont_event_indices))
                    #         event_info.append("MULTIMAPPING")
                    #     else:
                    #         event_info.append("-".join(decont_event_indices))
                    #         event_info.append("SINGLEMAPPING")
                    #     event_info_dict["events"].append(event_info)

                    event_info_list.append(event_info_dict)
                line_dict[k]["event_info"] = event_info_list
            all_doc_dict[k] = line_dict[k]
    print(f"Total event tokens: {total_count}, missing event tokens: {missing_count}, "
          f"multi-mapped event tokens: {multi_count}")
    with open(Path(pped_decont_jsonl_file).parent / f"event_mapped_{Path(pped_decont_jsonl_file).stem}.json",
              "w") as out_f:
        json.dump(all_doc_dict, out_f, indent=2)


if __name__ == '__main__':
    ori_article_json_file = ARTICLE_PATH / "ecb+full_marked_event_37_38.json"
    gpt_res_jsonl_file = DECONT_ARTICLE_PATH / "ecb" / "ecb+full_marked_event_37_38_decont_v2.jsonl"
    process_gpt_res(ori_article_json_file, gpt_res_jsonl_file, fill=True)

    # pped_decont_jsonl_file = DECONT_ARTICLE_PATH / "shifa" / "pped_shifa_israel_national_news_decont.jsonl"
    # map_events(pped_decont_jsonl_file)
