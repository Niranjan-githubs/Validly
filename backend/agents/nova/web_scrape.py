# web_scraper.py

import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time

def extract_text_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except Exception as e:
        print(f"[newspaper3k failed] Falling back to bs4 for {url}: {e}")
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all("p")
            return "\n".join([p.get_text() for p in paragraphs if p.get_text()])
        except Exception as e:
            print(f"[bs4 also failed] Could not extract content from {url}: {e}")
            return None

def extract_all_articles(search_results):
    extracted_data = {}

    for query, articles in search_results.items():
        extracted_data[query] = []
        for article in articles:
            url = article['url']
            print(f"Extracting: {url}")
            text = extract_text_from_url(url)
            if text:
                extracted_data[query].append({
                    "url": url,
                    "title": article.get("title"),
                    "score": article.get("score"),
                    "extracted_text": text
                })
            time.sleep(1)  # to be polite to servers

    return extracted_data
