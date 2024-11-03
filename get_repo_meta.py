import requests
from bs4 import BeautifulSoup
import json
from argparse import ArgumentParser
from tqdm.auto import tqdm
import urllib.parse
import concurrent.futures
import threading

TARGET_URL = {
    "cvpr23": "https://openaccess.thecvf.com/CVPR2023?day=all",
    "iccv23": "https://openaccess.thecvf.com/ICCV2023?day=all", 
}

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--target", type=str, default="cvpr23")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    # load existing papers
    with open(f"{args.target}_papers.json", 'r') as file:
        papers = json.load(file)

    main_url = TARGET_URL[args.target]
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    netloc = urllib.parse.urlparse(main_url).netloc

    paper_links = soup.find_all('dt', class_='ptitle')
    paper_urls = [f"https://{netloc}{link.a['href']}" for link in paper_links]
    paper_titles = [link.a.text.strip() for link in paper_links]

    title_to_paper = {paper['title']: paper for paper in papers}

    # add url metadata to existing papers
    for title, url in zip(paper_titles, paper_urls):
        if title in title_to_paper:
            title_to_paper[title]['url'] = url

    # save papers
    with open(f"{args.target}_papers_withurl.json", 'w') as file:
        json.dump(papers, file)
        