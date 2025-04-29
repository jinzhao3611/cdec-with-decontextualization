import tqdm
from pathlib import Path
from openai import OpenAI
import json

api_key = ("sk-proj-DQeSpOZrKGvAuV6HV31zxLvQ8Jfuj5e-O_t9Q1qAGNfbDhDyMZ0MgmxBeEeNpO1FihbBhedF-"
           "YT3BlbkFJvqOXcGnQ-XmjtVnKq5GH2JtFD-m9VDEkPc6OSR33U3sKCw5YBqLCut6IN6BHCgn2ePWuFMVtcA")

MODEL_ID = "o1-preview"
client = OpenAI(api_key=api_key)

from decontextualization.prompts import SYSTEM_PROMPT, DECON_RICH_PROMPT
from data_path import ARTICLE_PATH, DECONT_ARTICLE_PATH


def format_article_lst(article: str):
    article_lst = [f"[{i}] {' '.join(k.split())}" for i, k in enumerate(article.split("\n"), 1)]
    return "\n".join(article_lst)


def run_gpt(article: str, flag, system_prompt: str = SYSTEM_PROMPT):
    prompt_str = DECON_RICH_PROMPT.invoke({"article_list": format_article_lst(article)}).to_string()
    if flag:
        print(SYSTEM_PROMPT)
        print(prompt_str)

    msg = {"role": "user", "content": prompt_str}
    if system_prompt:
        sys_msg = {"role": "system", "content": system_prompt}
        messages = [sys_msg, msg]
    else:
        messages = [msg]

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        # temperature=0,
        # max_tokens=256,
        # top_p=1,
        # frequency_penalty=0,
        # presence_penalty=0
    )
    response_txt = response.choices[0].message.content
    return response_txt


def decon_article(article_json_file):
    FLAG = True
    with open(article_json_file, "r") as f:
        article_dict = json.load(f)
    out_f = open(DECONT_ARTICLE_PATH / (Path(article_json_file).stem + "_decont_v1.jsonl"), "w")

    for i, uid in tqdm.tqdm(enumerate(article_dict), "running decontextualization"):
        if i >= 4:
            continue
        article = article_dict[uid]
        res = run_gpt(article, FLAG)
        FLAG = False

        out_f.write(json.dumps({uid: res}) + "\n")
    out_f.close()


if __name__ == '__main__':
    article_json_file = ARTICLE_PATH / "ecb+full_marked_event_37_38.json"
    decon_article(article_json_file)
