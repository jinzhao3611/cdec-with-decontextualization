# convert ecb+ test split to the format of source articles for GPT decontextualization

import json
from data_path import ECB_TEST_PATH


def append_event_suffix(tokens: list, event_indices: list):
    suffix = "_EVENT"
    for idx_start, idx_end in event_indices:
        tokens[idx_end] += suffix

        # for i in range(idx_start, idx_end + 1):
        #     tokens[i] += suffix
    return tokens


if __name__ == '__main__':
    with open(ECB_TEST_PATH / "ecb+full.json", "r") as f:
        ecb_data = json.load(f)
    out_dict = dict()
    kept_topics = ["37", "38", "43"]
    for topic in ecb_data:
        if topic not in kept_topics:
            continue
        docs = ecb_data[topic]
        for doc_id in docs:
            all_sents = []
            for sent in docs[doc_id]:
                tokens = sent["tokens"]
                events = sent["events"]
                marked_tokens = append_event_suffix(tokens, events)
                all_sents.append(" ".join(marked_tokens))
            sents_text = "\n".join(all_sents)
            out_dict[doc_id] = sents_text
    with open(ECB_TEST_PATH / f"ecb+full_marked_event_{'_'.join(kept_topics)}.json", "w") as f:
        json.dump(out_dict, f, indent=2)
