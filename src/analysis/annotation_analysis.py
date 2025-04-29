import pandas as pd
import os, yaml
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

topic = "rittenhouse"
source = "federalist"
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

# Display the first few rows of the combined data
# print(all_data.head())

num_rows = all_data.shape[0]

print(f"Number of rows: {num_rows}")

# Distribution of values in the 'relation' column
relation_distribution = all_data['relation'].value_counts()

print("Distribution of 'relation' column:")
print(relation_distribution)



