import pandas as pd
import os, yaml, re, csv
from pathlib import Path
from collections import defaultdict, Counter
import tqdm

# Load the config file
root_dir = Path(__file__).resolve().parent.parent
config_path = root_dir / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Access paths from the config file
data_dir = root_dir / config['paths']['data_dir']
model_dir = root_dir / config['paths']['models_dir']
output_dir = root_dir / config['paths']['output_dir']

quake_list37 = ['quakes', 'earthquakes', 'earthquake', 'quake', '6 . 1 - magnitude quake', '6 . 1 - magnitude earthquake',
              '6 . 1 magnitude earthquake', 'Magnitude - 6 . 1 quake', 'magnitude - 6 . 1 earthquake', 'Earthquake',
              'Indonesia quake', 'Indonesia earthquake', '6 . 1 magnitude quake', 'tremors', 'tremor', 'temblors', ]

quake_list38 = ['Magnitude 4 . 6 Earthquake', 'earthquake', 'quake', '4 . 6 magnitude quake', '4 - Plus Earthquake',
                'Lake County earthquake', '4 . 6 - Magnitude Earthquake', '4 . 6 quake', '4 . 4 quake', '4 . 6 - magnitude earthquake',
                'magnitude 4 . 6 earthquake', '4 . 6 earthquake', 'California Earthquake', 'California earthquake', 'temblor']
quake_list = quake_list38 + quake_list37

def check_error_file():
    file_path = Path.joinpath(output_dir, "error_files/test_scores_lr_cdecbm_no_args1e-06_errors.txt")
    with open(file_path, "r") as f:
        for line in tqdm.tqdm(f, desc="Processing test pairs"):
            comps = line.strip().split("\t")
            eid1, sent1, eid2, sent2, pred, gold = comps
            if eid1.startswith("37") and "quake" in sent1 and "quake" in sent2 and gold=="0":
                print(eid1, eid2)
                print(sent1, sent2)
                # print(pred)
                # print(gold)

def check_test_file():
    count = 0
    input_file_path = Path.joinpath(output_dir, "train_prep/ecb_test_added_time/pairs_all_no_args.test")
    output_file_path = Path.joinpath(output_dir, "train_prep/ecb_test_added_time/pairs_all_no_args_added_time.test")

    with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
        with open(input_file_path, "r") as f:
            for line in tqdm.tqdm(f, desc="Processing test pairs"):
                comps = line.strip().split("\t")
                eid1, eid2 = comps[0], comps[1]
                sent1, sent2 = comps[2], comps[13]
                gold = comps[24]
                tokens1 = sent1.split()
                tokens2 = sent2.split()
                e_start1, e_end1 = map(int, comps[3:5])
                e_start2, e_end2 = map(int, comps[14:16])
                trigger1 = " ".join(tokens1[e_start1:e_end1 + 1])
                trigger2 = " ".join(tokens2[e_start2:e_end2 + 1])

                if line.startswith("37") and "plus" not in line:
                    if trigger1 in quake_list and trigger2 in quake_list and gold == "1":
                        tokens1[e_end1+1: e_end1+1] = ["in", "2009"]
                        tokens2[e_end2+1: e_end2+1] = ["in", "2009"]
                        new_comps = [eid1, eid2, " ".join(tokens1), str(e_start1), str(e_end1), '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1',
                                     " ".join(tokens2), str(e_start2), str(e_end2), '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1', gold]
                        print(f"{eid1}\t{eid2}")
                        new_line = "\t".join(new_comps)
                        outfile.write(new_line + '\n')
                        count += 1
                    else:
                        outfile.write(line)


                elif line.startswith("37") and "plus" in line:
                    if trigger1 in quake_list and trigger2 in quake_list and gold == "1":
                        tokens1[e_end1+1: e_end1+1] = ["in", "2013"]
                        tokens2[e_end2+1: e_end2+1] = ["in", "2013"]
                        new_comps = [eid1, eid2, " ".join(tokens1), str(e_start1), str(e_end1), '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1',
                                     " ".join(tokens2), str(e_start2), str(e_end2), '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1', gold]
                        print(f"{eid1}\t{eid2}")
                        new_line = "\t".join(new_comps)
                        outfile.write(new_line + '\n')
                        count += 1
                    else:
                        outfile.write(line)

                elif line.startswith("38") and "plus" not in line:
                    if trigger1 in quake_list and trigger2 in quake_list and gold == "1":
                        tokens1[e_end1+1: e_end1+1] = ["in", "2009"]
                        tokens2[e_end2+1: e_end2+1] = ["in", "2009"]
                        new_comps = [eid1, eid2, " ".join(tokens1), str(e_start1), str(e_end1), '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1',
                                     " ".join(tokens2), str(e_start2), str(e_end2), '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1', gold]
                        print(f"{eid1}\t{eid2}")
                        new_line = "\t".join(new_comps)
                        outfile.write(new_line + '\n')
                        count += 1
                    else:
                        outfile.write(line)

                elif line.startswith("38") and "plus" in line:
                    if trigger1 in quake_list and trigger2 in quake_list and gold == "1":
                        tokens1[e_end1+1: e_end1+1] = ["in", "2013"]
                        tokens2[e_end2+1: e_end2+1] = ["in", "2013"]
                        new_comps = [eid1, eid2, " ".join(tokens1), str(e_start1), str(e_end1), '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1',
                                     " ".join(tokens2), str(e_start2), str(e_end2), '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1', gold]
                        print(f"{eid1}\t{eid2}")
                        print(new_comps)

                        new_line = "\t".join(new_comps)
                        outfile.write(new_line + '\n')
                        count += 1
                    else:
                        outfile.write(line)

                else:
                    outfile.write(line)

            print(count)










if __name__ == '__main__':
    # check_error_file()
    check_test_file()