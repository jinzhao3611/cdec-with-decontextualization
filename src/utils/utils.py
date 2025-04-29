import os
import yaml
from pathlib import Path
from typing import List, Tuple, Any, Union
from os import PathLike


# Load the config file
root_dir = Path(__file__).resolve().parent.parent
config_path = root_dir / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Access paths from the config file
data_dir = root_dir / config['paths']['data_dir']
model_dir = root_dir / config['paths']['models_dir']
output_dir = root_dir / config['paths']['output_dir']
resource_dir = root_dir / config['paths']['resources_dir']

def merge_files_in_folder(folder_path: Union[str, PathLike], output_file: Union[str, PathLike]):
    # Open the output file in write mode
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Loop through all files in the folder
        for filename in os.listdir(folder_path):
            if isinstance(filename, str) and filename.endswith('.txt'):  # Only process .txt files
                file_path = os.path.join(folder_path, filename)

                # Open each text file and append its content to the output file
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())  # Append file content
                    outfile.write("\n")  # Add a newline after each file's content for separation

    print(f"All files have been appended to {output_file}")


import os
from pathlib import Path
import pandas as pd


def merge_tsv_files(input_dir: Union[str, Path], output_file: Union[str, Path]):
    # Convert input_dir to a Path object if it's a string
    input_dir = Path(input_dir)

    # List all .tsv files in the directory
    tsv_files = sorted(input_dir.glob("*.tsv"))

    # Check if there are any TSV files
    if not tsv_files:
        print("No TSV files found in the directory.")
        return

    # Initialize a list to store DataFrames
    dataframes = []

    for idx, file in enumerate(tsv_files):
        # Read each TSV file into a DataFrame
        df = pd.read_csv(file, sep='\t')

        # If it's not the first file, remove the header to avoid duplicates
        if idx > 0:
            df.columns = dataframes[0].columns  # Ensure columns are aligned

        # Append the DataFrame to the list
        dataframes.append(df)

    # Concatenate all DataFrames
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Write the concatenated DataFrame to a new TSV file
    merged_df.to_csv(output_file, sep='\t', index=False)

    print(f"Merged {len(tsv_files)} TSV files into {output_file}")


def run_all_sampled_neg_pairs():
    input_directory = Path.joinpath(output_dir, f"train_prep/sampled_neg_pairs")
    output_tsv = Path.joinpath(output_dir, f"train_prep/dumb_neg_pairs.tsv")

    merge_tsv_files(input_directory, output_tsv)



def run_trial_yu_input():
    # Specify the folder path where the text files are located
    folder_path = Path.joinpath(data_dir, f"yu_input/{topic}/{source}")
    # Specify the path to the output file (where all text will be appended)
    output_file = Path.joinpath(data_dir, f'yu_input/{topic}/{source}/{topic}_{source}.final')

    merge_files_in_folder(folder_path, output_file)

if __name__ == '__main__':
    topic = "putin"
    source = "google_news2"

    # run_trial_yu_input()
    run_all_sampled_neg_pairs()

