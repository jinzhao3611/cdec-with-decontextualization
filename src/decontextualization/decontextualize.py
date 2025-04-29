import yaml
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load the config file
root_dir = Path(__file__).resolve().parent.parent
config_path = root_dir / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Access paths from the config file
data_dir = root_dir / config['paths']['data_dir']
model_dir = root_dir / config['paths']['models_dir']
output_dir = root_dir / config['paths']['output_dir']

#

topic = "shifa"
source = "israel_national_news"

sample_input_file_path = Path.joinpath(data_dir, f"event_detected/{topic}/{source}.json")
sample_output_file_path = Path.joinpath(data_dir, f"decontextualized/{topic}/{source}.json")

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")

prompt = f"""{article}

For each sentence in the above article, can you rewrite each sentence by adding more context from the article, such that the sentence stands alone and provides full information about the containing event. The tagged event should be kept unchanged and tagged in the rewrite."""
