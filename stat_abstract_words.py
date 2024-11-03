import json
from tqdm.auto import tqdm

TARGET_DB = {
    "cvpr23": "cvpr23_papers.json",
    "iccv23": "iccv23_papers.json", 
}

total_words = 0
for target, filename in TARGET_DB.items():
    with open(filename, 'r') as file:
        papers = json.load(file)
    
    for paper in tqdm(papers):
        title = paper['title']
        abstract = paper['abstract']
        total_words += len(title.split()) + len(abstract.split())

print(f"Total words: {total_words}")
