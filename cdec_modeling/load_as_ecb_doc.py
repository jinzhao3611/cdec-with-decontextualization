import json
from collections import defaultdict

from data_path import DECONT_ARTICLE_PATH, GVC_PATH
from cdec_modeling import KEYWORD, SOURCE


class ECBDoc:

    def __init__(self):
        self.tokens = []
        self.sentences = {}
        self.topic = -1
        self.doc_id = 0
        self.doc_name = ''
        self.mentions = {}
        self.mention2token = {}
        self.mentions_type = {}
        self.token2mention = {}
        self.token2sentence = {}
        self.coref_mention = {}
        self.mention2cluster_id = {}
        self.cluster_head = []
        self.cluster_type = {}
        self.cluster_instance_id = {}
        self.clusters = {}

    def set_doc_info(self, doc_id, name):
        self.doc_id = doc_id
        self.doc_name = name


class Sentence:

    def __init__(self, topic, doc_id):
        self.topic = topic
        self.doc_id = doc_id
        self.tokens = []
        self.events = []
        self.entities = []
        self.mapped_tokens = []
        self.event_idx_mapping = {}


class Event:

    def __init__(self, topic, doc_id, sen_id, start_offset, end_offset, token_start_idx, token_end_idx):
        self.topic = topic
        self.doc_id = doc_id
        self.sen_id = sen_id
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.token_start_idx = token_start_idx
        self.token_end_idx = token_end_idx

        self.arg0 = (-1, -1)
        self.arg1 = (-1, -1)
        self.time = (-1, -1)
        self.loc = (-1, -1)

        self.gold_cluster = '_'.join(['Singleton', doc_id, str(token_start_idx),
                                      str(token_end_idx)])  # Will be overwritten if belongs to a cluster
        self.cd_coref_chain = -1

        self.mention_id = self.doc_id + "#" + '_'.join(
            [str(sen_id + 1), str(self.start_offset),
             str(self.end_offset)])  # adapted to the framing task naming system

        self.lemma = None


def load_parsed_json(json_file: str):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data


def strip_event_suffix(sentence: str):
    return sentence.replace("_EVENT", "")


def prepare_ecb_docs(topic: str, source: str, *, use_decont: bool):
    parsed_json_path = DECONT_ARTICLE_PATH / topic / f"manual_change_event_mapped_pped_{topic}_{source}_decont.json"
    topic = f"{topic}_{source}"  # use full topic in the sentence and event object
    docs = load_parsed_json(parsed_json_path)
    all_docs = dict()
    for doc_id in docs:
        doc_dict = docs[doc_id]

        doc = ECBDoc()
        doc.set_doc_info(doc_id, doc_id)  # set doc_id and doc_name the same

        if use_decont:
            sentences = doc_dict["decont_sents"]
            event_loc_idx = 2
            mapped_event_loc_idx = 1
            mapped_sentences = doc_dict["ori_sents"]
        else:
            sentences = doc_dict["ori_sents"]
            event_loc_idx = 1
            mapped_event_loc_idx = 2
            mapped_sentences = doc_dict["decont_sents"]

        event_info = doc_dict["event_info"]
        mentions = []
        for sent_idx, sent_events in enumerate(event_info):
            for event in sent_events["events"]:
                start_offset = event[event_loc_idx]
                end_offset = event[event_loc_idx]
                mentions.append([sent_idx, start_offset, end_offset])

        global_tok_idx = 0
        for i, sent in enumerate(sentences):
            doc.sentences[i] = Sentence(topic, doc.doc_name)
            sent = strip_event_suffix(sent)
            sent = sent.split()
            for j, token in enumerate(sent):
                doc.tokens.append(token)
                doc.sentences[i].tokens.append((token, j))
                doc.token2sentence[global_tok_idx] = (i, j)
                global_tok_idx += 1
            sent_events = event_info[i]["events"]
            event_idx_mapping = {
                (e[event_loc_idx], e[event_loc_idx]): (e[mapped_event_loc_idx], e[mapped_event_loc_idx]) for e in
                sent_events}
            doc.sentences[i].mapped_tokens = strip_event_suffix(mapped_sentences[i]).split()
            doc.sentences[i].event_idx_mapping = event_idx_mapping
        token2sentence_inv = {v: k for k, v in doc.token2sentence.items()}

        for mention_id, mention in enumerate(mentions):
            doc.mention2token[mention_id] = []
            if mention[1] == "":
                # no mapping event in the decont sentence
                continue
            sent_idx, start_offset, end_offset = [int(i) for i in mention]
            for i in range(start_offset, end_offset + 1):
                t_id = token2sentence_inv[(sent_idx, i)]
                doc.mention2token[mention_id].append(t_id)
                doc.token2mention[t_id] = mention_id
            doc.mentions_type[mention_id] = "event"  # for now, all mentions are events
            event = Event(topic, doc.doc_name, sent_idx, start_offset, end_offset, doc.mention2token[mention_id][0],
                          doc.mention2token[mention_id][-1])
            doc.sentences[sent_idx].events.append(event)
            doc.mentions[mention_id] = event
        all_docs[doc_id] = doc

        # print(doc.mentions[8].__dict__)
        # print(doc.sentences[11].events[1].__dict__)
        # print(doc.mention2token[3])
        #
        # print(doc_id)
        # print(doc.tokens)
        # print(doc.tokens[doc.mention2token[21][0]])
        # print(doc.token2sentence)
        # print(doc.sentences[17].tokens)
        # break
    return all_docs


def prepare_gvc_as_ecb_docs():
    with open(GVC_PATH / 'gvc_test.json', 'r') as f:
        test_data = json.load(f)
    docs = test_data['docs']
    clusters = test_data['clusters']
    subtopic_mapping = test_data['subtopics']

    doc_id2mentions = defaultdict(list)

    for cluster_id in clusters:
        cluster = clusters[cluster_id]
        for event_id in cluster:
            doc_id, comps = event_id.split('#')
            doc_id2mentions[doc_id].append(event_id)
    all_docs = dict()

    for doc_id in docs:

        doc = ECBDoc()
        doc.set_doc_info(doc_id, doc_id)
        sentences = docs[doc_id]
        global_tok_idx = 0
        for i, sent in enumerate(sentences):
            doc.sentences[i] = Sentence("gvc", doc.doc_name)
            for j, token in enumerate(sent):
                doc.tokens.append(token)
                doc.sentences[i].tokens.append((token, j))
                doc.token2sentence[global_tok_idx] = (i, j)
                global_tok_idx += 1
        token2sentence_inv = {v: k for k, v in doc.token2sentence.items()}
        mentions = doc_id2mentions[doc_id]
        for mention_id, mention in enumerate(mentions):
            doc.mention2token[mention_id] = []
            doc_id, comps = mention.split('#')

            sent_idx, start_offset, end_offset = comps.split('_')
            sent_idx = int(sent_idx) - 1
            start_offset = int(start_offset)
            end_offset = int(end_offset)
            for i in range(start_offset, end_offset + 1):
                t_id = token2sentence_inv[(sent_idx, i)]
                doc.mention2token[mention_id].append(t_id)
                doc.token2mention[t_id] = mention_id
            doc.mentions_type[mention_id] = "event"  # for now, all mentions are events
            event = Event("gvc", doc.doc_name, sent_idx, start_offset, end_offset, doc.mention2token[mention_id][0],
                          doc.mention2token[mention_id][-1])
            doc.sentences[sent_idx].events.append(event)
            doc.mentions[mention_id] = event
        all_docs[doc_id] = doc
    return all_docs


if __name__ == '__main__':
    all_docs = prepare_ecb_docs(KEYWORD.rh, SOURCE.fd, use_decont=True)
    print(all_docs["02_00_36"].sentences[1].events[0].__dict__)
    print(list(all_docs.keys()))

    # docs = prepare_gvc_as_ecb_docs()
    # print(list(docs.keys()))
    #
    # doc = docs["76889e35ee06404b5a5d8bd5083c2e60"]
    # for mid in doc.mentions:
    #     print(doc.mentions[mid].__dict__)
    # print(doc.sentences[0].events[1].__dict__)

