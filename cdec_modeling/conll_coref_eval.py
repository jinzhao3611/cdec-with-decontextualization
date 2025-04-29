
from evaluate import load
from data_path import DECONT_ARTICLE_PATH


def load_conll_file(conll_file):
    lines = []
    with open(conll_file, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            lines.append(line.strip())
    return lines


def get_conll_score(gold_conll, pred_conll):
    gold_lines = load_conll_file(gold_conll)
    pred_lines = load_conll_file(pred_conll)
    assert len(gold_lines) == len(pred_lines)
    coval = load('coval')
    results = coval.compute(predictions=[pred_lines], references=[gold_lines])
    print(results["conll_score"])
    print(results)

    """
    {'mentions/recall': 1.0, 'mentions/precision': 1.0, 'mentions/f1': 1.0, 'muc/recall': 0.8974358974358975, 'muc/precision': 0.8421559191530318, 'muc/f1': 0.8689175769612711, 'bcub/recall': 0.8764061521528818, 'bcub/precision': 0.8288264115409727, 'bcub/f1': 0.8519524921196796, 'ceafe/recall': 0.7795629839747692, 'ceafe/precision': 0.8468936600535617, 'ceafe/f1': 0.8118346728327157, 'lea/recall': 0.7619294749704532, 'lea/precision': 0.7442020094447233, 'lea/f1': 0.7529614143194796, 'conll_score': 84.4234913971222}

    """


def reorder_conll(ref_conll, new_conll):
    gold_lines = load_conll_file(new_conll)
    ref_lines = load_conll_file(ref_conll)
    gold_line_dict = {l.split("\t")[0]: l.split("\t")[1] for l in gold_lines}
    new_gold_lines = []
    for l in ref_lines:
        line_id, _ = l.split("\t")
        new_gold_lines.append(f"{line_id}\t{gold_line_dict[line_id]}")
    with open(new_conll.parent / (new_conll.stem + "_reorder.conll"), "w") as f:
        for line in new_gold_lines:
            f.write(line + "\n")


if __name__ == '__main__':
    # ref_conll = project_path / "data/preprocessed/gold/test_events_corpus_level_clean_reorder.conll"
    # new_conll = project_path / "test_scores_lr_2024_test_dist_from_roberta1e-06.conll"
    # reorder_conll(ref_conll, new_conll)
    gold_conll = DECONT_ARTICLE_PATH / "CD_test_event_mention_based_0.8_0.5.response_conll"
    pred_conll = DECONT_ARTICLE_PATH / "CD_test_event_mention_based_0.8_0.5old.response_conll"
    get_conll_score(gold_conll, pred_conll)
