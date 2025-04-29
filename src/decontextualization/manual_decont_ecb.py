import json
from data_path import ECB_TEST_PATH

# EQ_09 = ("The 2009 Indonesia earthquake occurred on September 30, 2009, with a magnitude of 7.6 and struck the "
#          "western coast of Sumatra, near the city of Padang.")
#
# EQ_13 = ("The 2013 Aceh earthquake struck the Indonesian province of Aceh, located on the northern tip of Sumatra, "
#          "on July 2, 2013. This earthquake had a magnitude of 6.1.")


# EQ_09 = ("The earthquake occurred on September 30, 2009, with a magnitude of 7.6 and struck the "
#          "western coast of Sumatra, near the city of Padang.")
#
# EQ_13 = "This earthquake struck the Indonesian province of Aceh, on July 2, 2013, with a magnitude of 6.1."

EQ_09 = "Earthquake happened in Papua in 2009:"

EQ_13 = "Earthquake happened in Aceh in 2013:"

AC_06 = "AMD acquires ATI in 2006:"

AC_12 = "AMD acquires Seamicro in 2012:"

SOMA_09 = "Earthquake happened in 2009:"

SOMA_13 = "Earthquake happened in 2013:"

kept_topics = ["37", "38", "43"]

topic2prefix = {
    "37": [EQ_09, EQ_13],
    "38": [SOMA_09, SOMA_13],
    "43": [AC_06, AC_12],
}


def decont_sentences():
    with open(ECB_TEST_PATH / "ecb+full.json", "r") as f:
        ecb_data = json.load(f)
    event_dict = dict()
    for topic in ecb_data:
        if topic not in kept_topics:
            continue
        docs = ecb_data[topic]
        for doc_id in docs:
            if doc_id.endswith("ecb.xml"):
                prefix = topic2prefix[topic][0].split()
                prefix_len = len(prefix)
            else:
                prefix = topic2prefix[topic][1].split()
                prefix_len = len(prefix)
            for sent_id, sent in enumerate(docs[doc_id]):
                tokens = sent["tokens"]
                events = sent["events"]
                for start, end in events:
                    ori_event_id = f"{doc_id.split('.')[0]}_{sent_id}_{start}_{end}"
                    new_start = start + prefix_len
                    new_end = end + prefix_len
                    new_tokens = prefix + tokens
                    event_dict[ori_event_id] = (new_start, new_end, new_tokens)
    return event_dict


def replace_ecb_test_sents(event_dict):
    all_lines = []
    with open(ECB_TEST_PATH / "pairs_all_no_args.test", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().split('\t')
            assert len(line) == 25
            event_id_1 = line[0].strip()
            # text_a = line[2].strip()
            # span_a_left = int(line[3].strip())
            # span_a_right = int(line[4].strip())
            if event_id_1 in event_dict:
                new_start, new_end, new_tokens = event_dict[event_id_1]
                line[2] = " ".join(new_tokens)
                line[3] = str(new_start)
                line[4] = str(new_end)

            event_id_2 = line[1].strip()
            # text_b = line[13].strip()
            # span_b_left = int(line[14].strip())
            # span_b_right = int(line[15].strip())
            if event_id_2 in event_dict:
                new_start, new_end, new_tokens = event_dict[event_id_2]
                line[13] = " ".join(new_tokens)
                line[14] = str(new_start)
                line[15] = str(new_end)

            all_lines.append("\t".join(line))
    with open(ECB_TEST_PATH / "pairs_all_no_args_manual_decont.test", "w", encoding="utf-8") as f:
        for line in all_lines:
            f.write(line + "\n")


if __name__ == '__main__':
    event_dict = decont_sentences()
    replace_ecb_test_sents(event_dict)
