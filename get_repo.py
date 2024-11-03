import requests
from bs4 import BeautifulSoup
import json
from argparse import ArgumentParser
from tqdm.auto import tqdm
import urllib
import urllib.parse

TARGET_URL = {
    "cvpr23": "https://openaccess.thecvf.com/CVPR2023?day=all",
    "iccv23": "https://openaccess.thecvf.com/ICCV2023?day=all", # TODO
}

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--target", type=str, default="cvpr23")
    args = parser.parse_args()
    return args

def file_saver(papers):
    with open(f"{args.target}_papers.json", 'w') as file:
        json.dump(papers, file)

    # save a TSV file
    with open(f"{args.target}_papers.tsv", 'w') as file:
        # write header
        file.write(f"Title\tAbstract\n")
        for paper in papers:
            file.write(f"{paper['title']}\t{paper['abstract']}\n")

def get_paper_details(main_url, file_saver=None):
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    netloc = urllib.parse.urlparse(main_url).netloc

    papers = []
    # Find all links to individual papers
    paper_links = soup.find_all('dt', class_='ptitle')

    for link in tqdm(paper_links, desc="Scraping papers"):
        # print(link)
        # paper_url = main_url + link.a['href']
        
        paper_url = f"https://{netloc}{link.a['href']}"
        print(paper_url)
        paper_response = requests.get(paper_url)
        paper_soup = BeautifulSoup(paper_response.content, 'html.parser')

        title = paper_soup.find('div', id='papertitle').text.strip()
        abstract = paper_soup.find('div', id='abstract').text.strip()

        papers.append({'title': title, 'abstract': abstract})

        if file_saver is not None:
            file_saver(papers)

    return papers

if __name__ == "__main__":
    args = parse_args()
    papers = get_paper_details(TARGET_URL[args.target], file_saver)



