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

def file_saver(papers, args):
    with open(f"{args.target}_papers.json", 'w') as file:
        json.dump(papers, file)

    with open(f"{args.target}_papers.tsv", 'w') as file:
        file.write("Title\tAbstract\n")
        for paper in papers:
            file.write(f"{paper['title']}\t{paper['abstract']}\n")

def fetch_paper_details(paper_url):
    paper_response = requests.get(paper_url)
    paper_soup = BeautifulSoup(paper_response.content, 'html.parser')

    title = paper_soup.find('div', id='papertitle').text.strip()
    abstract = paper_soup.find('div', id='abstract').text.strip()

    return {'title': title, 'abstract': abstract}

def get_paper_details(main_url, args, papers=None, file_saver=None):
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    netloc = urllib.parse.urlparse(main_url).netloc

    papers = [] if papers is None else papers
    paper_links = soup.find_all('dt', class_='ptitle')
    paper_urls = [f"https://{netloc}{link.a['href']}" for link in paper_links]

    # check if we already have some papers
    paper_titles = [link.a.text.strip() for link in paper_links]
    exists_titles = set([paper['title'] for paper in papers])
    # skip papers that have already been scraped
    paper_urls = [url for url, title in zip(paper_urls, paper_titles) if title not in exists_titles]
    print(f"Scraping {len(paper_urls)} papers")

    # Thread safety for appending to list
    append_lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_paper_details, url) for url in paper_urls]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Scraping papers"):
            try:
                paper = future.result()
                with append_lock:
                    papers.append(paper)
                    if file_saver is not None:
                        file_saver(papers, args)
            except Exception as e:
                print(f"Error fetching a paper: {e}")

    if file_saver is not None:
        file_saver(papers, args)

    return papers

if __name__ == "__main__":
    args = parse_args()
    # load existing papers
    try:
        with open(f"{args.target}_papers.json", 'r') as file:
            papers = json.load(file)
    except:
        papers = []
    papers = get_paper_details(TARGET_URL[args.target], args, papers, file_saver)
