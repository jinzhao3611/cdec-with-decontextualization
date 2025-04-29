import pandas as pd
import os, yaml, re, csv
from pathlib import Path
from collections import defaultdict

# Load the config file
root_dir = Path(__file__).resolve().parent.parent
config_path = root_dir / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Access paths from the config file
data_dir = root_dir / config['paths']['data_dir']
model_dir = root_dir / config['paths']['models_dir']
output_dir = root_dir / config['paths']['output_dir']


def read_annotated_data(topic, source):
    to_analyze_annotation_folder_path = Path.joinpath(data_dir, f"annotation/annotated/{topic}/{source}")

    # Create an empty list to store the DataFrames
    dataframes = []

    # Loop through each file in the folder
    for file_name in os.listdir(to_analyze_annotation_folder_path):
        if file_name.endswith(".xlsx"):  # Check if the file is an Excel file
            file_path = os.path.join(to_analyze_annotation_folder_path, file_name)

            # Read the Excel file
            all_data = pd.read_excel(file_path)

            # Append the DataFrame to the list
            dataframes.append(all_data)

    # If you want to concatenate all dataframes into one
    all_data = pd.concat(dataframes, ignore_index=True)
    return all_data

def create_additional_putin_decont_train_pairs():
    topic = "putin"
    source = "google_news2"
    all_data = read_annotated_data(topic, source)
    # Assuming your dataframe is named df
    filtered_df = all_data[
        (all_data['relation'] == 1) &(
                (all_data['event1'].str.contains('elections_EVENT')) |
                (all_data['event1'].str.contains('election_EVENT')) |
                (all_data['event2'].str.contains('elections_EVENT')) |
                (all_data['event2'].str.contains('election_EVENT'))
        )

        ]

    pos_df = filtered_df.copy()
    neg_df = filtered_df.copy()
    #2. add "in 2024" after all the event
    pos_df.loc[:, 'event1'] = pos_df['event1'].str.replace('in 2024', '').str.replace('in 2018', '').str.replace('_EVENT', '_EVENT in 2024').str.replace(r'\s+', ' ', regex=True).str.strip()
    pos_df.loc[:, 'event2'] = pos_df['event2'].str.replace('in 2024', '').str.replace('in 2018', '').str.replace('_EVENT', '_EVENT in 2024').str.replace(r'\s+', ' ', regex=True).str.strip()

    #3. add "in 2018" after event1, and "in 2014" after event2, and tag label 8  (1311 samples)
    neg_df.loc[:, 'event1'] = pos_df['event1'].str.replace('in 2024', '').str.replace('in 2018', '').str.replace('_EVENT', '_EVENT in 2018').str.replace(r'\s+', ' ', regex=True).str.strip()
    neg_df.loc[:, 'event2'] = pos_df['event2'].str.replace('in 2024', '').str.replace('in 2018', '').str.replace('_EVENT', '_EVENT in 2024').str.replace(r'\s+', ' ', regex=True).str.strip()
    neg_df.loc[:, 'relation'] = 8

    pos_df[['event1_uid', 'event1', 'event2_uid', 'event2', 'relation']].to_csv(Path.joinpath(output_dir, f"train_prep/additional_decont_train_pairs/added_time/{topic}_{source}_pos_added_time.csv"), index=False)
    neg_df[['event1_uid', 'event1', 'event2_uid', 'event2', 'relation']].to_csv(Path.joinpath(output_dir, f"train_prep/additional_decont_train_pairs/added_time/{topic}_{source}_neg_added_time.csv"), index=False)


def create_additional_hong_kong_decont_train_pairs():
    # split_hong_kong_csv()
    # add_hong_kong_time_df9_pos()
    add_hong_kong_time_df13_neg()



def split_hong_kong_csv():
    topic = "hong_kong"
    source = "china_daily"
    all_data = read_annotated_data(topic, source)

    df9_pos = all_data[(all_data['relation'] == 9)]
    df9_pos.loc[:, 'relation'] = 1

    df9_neg = all_data[(all_data['relation'] == 9)]
    df9_neg.loc[:, 'relation'] = 8


    df13_neg = all_data[(all_data['relation'] == 13)]
    df13_neg.loc[:, 'relation'] = 8


    df9_pos[['event1_uid', 'event1', 'event2_uid', 'event2', 'relation']].to_csv(
        Path.joinpath(output_dir, f"train_prep/additional_decont_train_pairs/{topic}_{source}_df9_pos.csv"), index=False)
    df9_neg[['event1_uid', 'event1', 'event2_uid', 'event2', 'relation']].to_csv(
        Path.joinpath(output_dir, f"train_prep/additional_decont_train_pairs/{topic}_{source}_df9_neg.csv"), index=False)
    df13_neg[['event1_uid', 'event1', 'event2_uid', 'event2', 'relation']].to_csv(
        Path.joinpath(output_dir, f"train_prep/additional_decont_train_pairs/{topic}_{source}_df13_neg.csv"), index=False)

    # for df9, add different time to the event lacking, and tag 0; add same time to the event lacking, and tag 1;
    # for df13, add different time to event lacking ,and tag 0

def find_date(text):
    # Define a regex pattern for common date formats (e.g., 2023-09-15, 15/09/2023, September 15, 2023, etc.)
    date_pattern = r'\b(From\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\s+to\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}' \
                   r'|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?' \
                   r'|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}(?:,\s+\d{4})?' \
                   r'|(?:January|February|March|April|May|June|July|August|September|October|November|December)' \
                   r'|\b\d{1,2}(st|nd|rd|th)\b' \
                   r'|national day|labor day)\b'
    matches = re.findall(date_pattern, text, re.IGNORECASE)
    dates = []
    for date in matches:
        dates.append(date[0])
    return dates

def get_date_phrase(dates):
    if len(dates) == 0:
        return ""
    elif len(dates) == 1:
        if len(dates[0].split()) == 1:
            return "In " + dates[0] + " "
        else:
            return "On " + dates[0] + " "
    elif len(dates) == 2:
         return "From " + dates[0] + " to " + dates[1] + " "
    else:
        print("Something wrong: There are three times in one sentence: ", dates)

def lowercase_first_letter(sentence):
    if sentence:
        return sentence[0].lower() + sentence[1:]
    return sentence

def add_hong_kong_time_df9_pos():
    topic = 'hong_kong'
    source = 'china_daily'
    input_file = Path.joinpath(output_dir, f"train_prep/additional_decont_train_pairs/{topic}_{source}_df9_pos.csv")
    output_file = Path.joinpath(output_dir,
                                f"train_prep/additional_decont_train_pairs/added_time/{topic}_{source}_df9_pos_added_time.csv")

    pos_pair_data = []
    # Read the file
    with open(input_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # skip the header row
        for row in csv_reader:
            uid1, sent1, uid2, sent2, relation = row
            date_phrase1 = get_date_phrase(find_date(sent1))
            date_phrase2 = get_date_phrase(find_date(sent2))

            if date_phrase1 and not date_phrase2:
                sent2 = date_phrase1 + lowercase_first_letter(sent2)
                pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            elif not date_phrase1 and date_phrase2:
                sent1 = date_phrase2 + lowercase_first_letter(sent1)
                pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            elif not date_phrase1 and not date_phrase2:
                sent1 = "On August 19 " + lowercase_first_letter(sent1)
                sent2 = "On August 19 " + lowercase_first_letter(sent2)
                pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            elif date_phrase1 and date_phrase2:
                print(f"Something wrong: two sentences both have time expression: {row}")
                print(f"here: {date_phrase1}, {date_phrase2}")
            else:
                print(f"what are the other situations:{date_phrase1}, {date_phrase2}")

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        # Create a CSV writer object
        csv_writer = csv.writer(file)
        # Write each row in the data list
        for row in pos_pair_data:
            csv_writer.writerow(row)

def add_hong_kong_time_df9_neg():
    topic = 'hong_kong'
    source = 'china_daily'
    input_file = Path.joinpath(output_dir, f"train_prep/additional_decont_train_pairs/{topic}_{source}_df9_neg.csv")
    output_file = Path.joinpath(output_dir,
                                f"train_prep/additional_decont_train_pairs/added_time/{topic}_{source}_df9_neg_added_time.csv")

    pos_pair_data = []
    # Read the file
    with open(input_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # skip the header row
        for row in csv_reader:
            uid1, sent1, uid2, sent2, relation = row
            date_phrase1 = get_date_phrase(find_date(sent1))
            date_phrase2 = get_date_phrase(find_date(sent2))

            if date_phrase1 and not date_phrase2:
                sent2 = "On August 19 " + lowercase_first_letter(sent2)
                pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            elif not date_phrase1 and date_phrase2:
                sent1 = "On August 19" + lowercase_first_letter(sent1)
                pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            elif not date_phrase1 and not date_phrase2:
                sent1 = "On July 19 " + lowercase_first_letter(sent1)
                sent2 = "On August 19 " + lowercase_first_letter(sent2)
                pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            elif date_phrase1 and date_phrase2:
                print(f"Something wrong: two sentences both have time expression: {row}")
                print(f"here: {date_phrase1}, {date_phrase2}")
                pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            else:
                print(f"what are the other situations:{date_phrase1}, {date_phrase2}")

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        # Create a CSV writer object
        csv_writer = csv.writer(file)
        # Write each row in the data list
        for row in pos_pair_data:
            csv_writer.writerow(row)

def add_hong_kong_time_df13_neg():
    topic = 'hong_kong'
    source = 'china_daily'
    input_file = Path.joinpath(output_dir, f"train_prep/additional_decont_train_pairs/{topic}_{source}_df13_neg.csv")
    output_file = Path.joinpath(output_dir,
                                f"train_prep/additional_decont_train_pairs/added_time/{topic}_{source}_df13_neg_added_time.csv")

    pos_pair_data = []
    # Read the file
    with open(input_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # skip the header row
        for row in csv_reader:
            uid1, sent1, uid2, sent2, relation = row
            date_phrase1 = get_date_phrase(find_date(sent1))
            date_phrase2 = get_date_phrase(find_date(sent2))

            if date_phrase1 and not date_phrase2:
                sent2 = "On August 19 " + lowercase_first_letter(sent2)
                pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            elif not date_phrase1 and date_phrase2:
                sent1 = "On August 19" + lowercase_first_letter(sent1)
                pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            elif not date_phrase1 and not date_phrase2:
                sent1 = "On July 19 " + lowercase_first_letter(sent1)
                sent2 = "On August 19 " + lowercase_first_letter(sent2)
                pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            elif date_phrase1 and date_phrase2:
                print(f"Something wrong: two sentences both have time expression: {row}")
                print(f"here: {date_phrase1}, {date_phrase2}")
                if date_phrase1 != date_phrase2:
                    pos_pair_data.append([uid1, sent1, uid2, sent2, relation])
            else:
                print(f"what are the other situations:{date_phrase1}, {date_phrase2}")

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        # Create a CSV writer object
        csv_writer = csv.writer(file)
        # Write each row in the data list
        for row in pos_pair_data:
            csv_writer.writerow(row)

def generate_additional_train_data():

    with open(Path.joinpath(output_dir, f"train_prep/additional_decont_train_pairs/added_train_data.txt"), "w") as outfile:
        folder_path = Path.joinpath(output_dir, "train_prep/additional_decont_train_pairs/added_time")

        # Iterate through each file in the folder
        for file_name in os.listdir(folder_path):
            # Check if the file is a CSV file
            if file_name.endswith('.csv'):
                # Create the full file path
                file_path = os.path.join(folder_path, file_name)

                # Open and read the CSV file line by line
                with open(file_path, mode='r', encoding='utf-8') as file:
                    csv_reader = csv.reader(file)
                    for row in csv_reader:
                        # Do something with the row, here we just print it
                        event_uid1, sent1_wz_event, event_uid2, sent2_wz_event, relation = row
                        sent1 = append_space_to_event_words(sent1_wz_event).replace("_EVENT", "")
                        event_index1 = extract_event_from_sent(sent1_wz_event)[0][0][0]
                        sent2 = append_space_to_event_words(sent2_wz_event).replace("_EVENT", "")
                        event_index2 = extract_event_from_sent(sent2_wz_event)[0][0][0]

                        labels = {'1': 1, '8':0}

                        loc1 = f"{event_index1}\t{event_index1}\t-1\t-1\t-1\t-1\t-1\t-1\t-1\t-1"

                        loc2 = f"{event_index2}\t{event_index2}\t-1\t-1\t-1\t-1\t-1\t-1\t-1\t-1"
                        outfile.write(f"{sent1}\t{loc1}\t{sent2}\t{loc2}\t{labels[relation]}\n")

def append_space_to_event_words(input_string):
    # Define the regex pattern to match words ending with _EVENT
    pattern = r'(\b\w+_EVENT\b)'

    # Use re.sub to replace each occurrence with itself followed by a space
    result_string = re.sub(pattern, r'\1 ', input_string)

    return " ".join(result_string.strip().split())

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

def run():
    # create_additional_putin_decont_train_pairs()
    # create_additional_hong_kong_decont_train_pairs()
    generate_additional_train_data()

if __name__ == '__main__':
    run()

    # sentence = "On August 19 continuing the protests following an illegal rally that turned violent in Yuen Long, thousands of protesters gathered_EVENT, on Hong Kong Island on Sunday, targeting several locations, including Hong Kong's Golden Bauhinia Square flag-raising venue in Wan Chai."
    # result1 = append_space_to_event_words(sentence)
    # result2 = extract_event_from_sent(result1)
    # print(result1)
    # print(result2[0][0][0])











