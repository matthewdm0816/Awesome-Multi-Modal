# Filter all MM papers from the CVPR/ICCV papers and run this script to get the results.
import os
import json
from argparse import ArgumentParser
from tqdm.auto import tqdm
import json
import time
import re
from collections import defaultdict
import csv

TARGET_DB = {
    "cvpr23": "cvpr23_papers_withurl.json",
    "iccv23": "iccv23_papers_withurl.json", 
}

# pattern to match yes
yes_pattern = re.compile(r"yes", re.IGNORECASE)

def parse_decision(decision):
    is_mm = False
    if re.search(yes_pattern, decision):
        is_mm = True
    else:
        return False, None
    
    # find the category after "yes"
    category = None
    category_pattern = re.compile(r"yes, (.*)", re.IGNORECASE)
    match = re.search(category_pattern, decision)
    if match:
        category = match.group(1).lower()
        category = re.split(r'(and)|(,)', category, flags=re.IGNORECASE)
        category = [c.strip() for c in category if c is not None and c.strip() != 'and' and c.strip() != ',']
    else:
        print(f"Warning: cannot find category for {decision}")

    return is_mm, category

if __name__ == "__main__":
    papers = []
    for data, filename in TARGET_DB.items():
        with open(filename, 'r') as file:
            papers.extend(json.load(file))

    mm_papers = []
    category_to_papers = defaultdict(list)

    for paper in tqdm(papers):
        if 'decision' in paper:
            is_mm, category = parse_decision(paper['decision'])
            if is_mm:
                for cat in category:
                    category_to_papers[cat].append(paper)
                paper['category'] = category
                # category_to_papers[category].append(paper)
                mm_papers.append(paper)

    print(f"Found {len(mm_papers)} MM papers")
    for category, papers in category_to_papers.items():
        print(f"{category}: {len(papers)}")


    for category, papers in category_to_papers.items():
        with open(f"{category.replace('/', ' or ')}_papers.json", 'w') as file:
            json.dump(papers, file, indent=2)

        with open(f"{category.replace('/', ' or ')}_papers.csv", 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'abstract', 'url'])
            writer.writeheader()
            for paper in papers:
                writer.writerow({'title': paper['title'], 'abstract': paper['abstract'], 'url': paper['url']})



        
        

    
            


