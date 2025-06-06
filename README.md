# CDEC with Decontextualization

This project includes an annotation pipeline for decontextualizing event mentions in text and annotated data in data folder.

Download the data from [Google Drive](https://drive.google.com/file/d/15kJkNQHB7ZYPC_GyhsMq6F6ZtBLwZM5j/view?usp=sharing). 

## Project Structure

```
src/
├── preprocessing/         # Data preprocessing scripts
│   ├── preprocess.py
│   ├── tag_event.py
│   ├── article_clustering.py
│   └── article_similarity.py
├── decontextualization/   # Decontextualization related scripts
│   ├── decontextualize.py
│   ├── convert2source_format.py
│   ├── decont_gpt.py
│   ├── manual_decont_ecb.py
│   ├── postprocess.py
│   ├── prompts.py
│   └── result_inspect.py
├── analysis/             # Analysis and statistics scripts
│   ├── statistics.py
│   ├── decon_error_analysis.py
│   ├── annotation_analysis.py
│   └── decontextualize_analysis.py
├── utils/               # Utility functions and helper scripts
│   ├── utils.py
│   └── check_duplicates.py
├── data_generation/     # Scripts for generating training data
│   ├── generate_articles_json.py
│   ├── generate_mdp_input.py
│   ├── generate_yu_input.py
│   ├── sample_neg_pairs.py
│   └── additional_decon_train_data.py
└── evaluation/          # Scripts for evaluating results
    └── add_time_ecb_test.py
```

## Directory Descriptions

- `src/preprocessing/`: Contains scripts for data preprocessing, including event tagging, article clustering, and similarity analysis.
- `src/decontextualization/`: Core scripts for the decontextualization process, including GPT-based decontextualization and post-processing.
- `src/analysis/`: Tools for analyzing results and generating statistics about the decontextualization process.
- `src/utils/`: Helper functions and utility scripts used across the project.
- `src/data_generation/`: Scripts for generating training data and various input formats.
- `src/evaluation/`: Scripts for evaluating the performance of the decontextualization system.

## Additional Directories

- `data/`: Contains the datasets and processed data files.
- `config/`: Configuration files for the system.
- `resources/`: Additional resources needed for the system.
- `cdec_modeling/`: Core modeling code for the CDEC system.
- `data_path/`: Path configurations for data access.