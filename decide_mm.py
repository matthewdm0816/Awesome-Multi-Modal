# Invoke GPT to decide a paper is related to a topic
import os
os.environ["ALL_PROXY"] = "http://localhost:7890"

import json
from argparse import ArgumentParser
from tqdm.auto import tqdm
import json
import openai
from openai.error import RateLimitError, APIConnectionError
import time
openai.api_key = os.getenv("OPENAI_API_KEY")

TARGET_DB = {
    "cvpr23": "cvpr23_papers.json",
    "iccv23": "iccv23_papers.json", 
}

SYSTEM = "gpt-4-1106-preview"
SYSTEM_PROMPT = "You are a professional researcher in computer science, and major in computer vision, natural language processing and multi-modal learning. You are reading a paper and want to decide if it is related to a topic."
PROMPT = open("prompt2.txt", "r").read()

# SUPERTOPIC = "Multi-Modal and Vision-Language Learning"
# TOPICS = [
#     "Visual Question Answering/VQA",
#     "Visual Dialog",
#     "Image Captioning/Video Captioning/Scene Captioning",
#     "Visual Grounding",
#     "Vision-Language Navigation",
#     "Vision-Language Representation Learning/Pretraining",
#     "Visual Commonsense Reasoning",
#     "Few-shot/Zero-shot Vision-Language Learning",
#     "Cross-modal Retrieval",
#     "Other Multi-modal Learning",
# ]

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--target", type=str, default="cvpr23")
    args = parser.parse_args()
    return args

def load_papers(args):
    with open(TARGET_DB[args.target], 'r') as file:
        papers = json.load(file)
    return papers

def robust_query(max_retry=3, **query_kwargs):
    for r in range(max_retry):
        try:
            response = openai.ChatCompletion.create(
                **query_kwargs
            )
            return response
        except RateLimitError as e:
            print("RateLimitError, retrying...") # 40K tokens per min
            if r < 10:
                time.sleep(30)
                continue
        except APIConnectionError as e:
            print("APIConnectionError, retrying...")
            if r < 10:
                time.sleep(2 ** r)
                continue
        except Exception as e:
            print(e)
            print("Unknown error, retrying...")
            if r < 10:
                time.sleep(2 ** r)
                continue
    raise RateLimitError(f"Reached {max_retry} times retry, aborting...")

def dialog(role: str, content: str):
    return {
        "role": role,
        "content": content
    }

def decide(paper):
    chat_history = []
    chat_history.append(dialog("system", SYSTEM_PROMPT))
    chat_history.append(dialog("user", PROMPT.format(title=paper['title'], abstract=paper['abstract'])))
    # print(chat_history[-1]['content'])
    # exit(0)

    response = robust_query(
        model=SYSTEM,
        messages=chat_history,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    response = response.choices[0]["message"]["content"]
    print(paper['title'], response)
    response = response.split("RESULT")[-1].strip().split("]")[-1].strip()
    return response

if __name__ == "__main__":
    args = parse_args()
    papers = load_papers(args)
    print(f"Loaded {len(papers)} papers")

    for paper in tqdm(papers):
        if 'decision' in paper and paper['decision'] != "":
            continue
        paper['decision'] = decide(paper)
        # time.sleep(1)

        with open(f"{args.target}_papers.json", 'w') as file:
            json.dump(papers, file)

