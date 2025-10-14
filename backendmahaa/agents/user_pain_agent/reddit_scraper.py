from tavily import TavilyClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import os
import subprocess
import contextlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents.user_pain_agent.llm_summarizer import select_top_comments_with_llm
from agents.competitor_agent.domain import guess_domain_with_llama3
chromedriver_path = r"D:\mahaa_v\chromedriver-win64\chromedriver.exe"

TAVILY_API_KEY = "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"
def tavily_search(query, api_key, num_results=10):
    client = TavilyClient(api_key)
    response = client.search(query=query, max_results=num_results)
    reddit_urls = [item['url'] for item in response.get('results', []) if 'reddit.com/r/' in item['url']]
    return reddit_urls

def extract_comment_data(comment_div, post_url):
    # Find author from the <a> tag inside the author-name-meta div
    author = ''
    author_meta_div = comment_div.find('div', class_='flex flex-row items-center overflow-hidden author-name-meta')
    if author_meta_div:
        author_tag = author_meta_div.find('a', class_='truncate font-bold text-neutral-content-strong text-12')
        if author_tag:
            author = author_tag.text.strip()
    # Find comment content (all <p> tags inside the main content div)
    content_div = comment_div.find('div', class_='py-0 xs:mx-xs mx-2xs inline-block max-w-full scalable-text')
    if content_div:
        comment_text = "\n".join(p.get_text(strip=True) for p in content_div.find_all('p'))
    else:
        comment_text = "\n".join(p.get_text(strip=True) for p in comment_div.find_all('p'))
    # Find comment id for permalink
    comment_id = comment_div.get('id')
    if comment_id and comment_id.startswith('t1_'):
        comment_url = post_url.rstrip('/') + '/comment/' + comment_id[3:]
    else:
        comment_url = post_url
    return {
        'url': comment_url,
        'author': author,
        'comment': comment_text
    }

def scrape_reddit_post(url, chromedriver_path=None):
    print(f"🕸️ Scraping with Selenium: {url}")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    try:
        if chromedriver_path:
            service = Service(chromedriver_path, log_path='NUL')
        else:
            service = Service(ChromeDriverManager().install(), log_path='NUL')
        service.creationflags = subprocess.CREATE_NO_WINDOW  # Hide the console window (Windows only)
        with open(os.devnull, 'w') as fnull, contextlib.redirect_stderr(fnull):
            driver = webdriver.Chrome(service=service, options=options)
            try:
                driver.get(url)
                time.sleep(4)
                soup = BeautifulSoup(driver.page_source, "html.parser")
            finally:
                try:
                    driver.quit()
                except Exception as e:
                    print(f"Error quitting driver: {e}")
    except Exception as e:
        return []
    if not soup:
        return []
    # Find all comment divs with class 'md text-14-scalable rounded-2 pb-2xs overflow-hidden'
    comment_divs = soup.find_all('div', class_='md text-14-scalable rounded-2 pb-2xs overflow-hidden')
    comments = []
    for comment_div in comment_divs:
        comment_data = extract_comment_data(comment_div, url)
        comments.append(comment_data)
    return comments

def get_domain_name_from_startup(startup_data):
    import json
    domain_info = guess_domain_with_llama3(json.dumps(startup_data))
    domain2 = domain_info.get('domain_search', 'Unknown')
    domain1 = domain_info.get('major_domain', 'Unknown')
    if domain1 == 'Unknown' and domain2 == 'Unknown':
        return startup_data.get('title', 'Unknown')
    return domain1 + " in " + domain2

def run_user_pain_agent(startup_data: dict) -> list:
    startup_data11 = startup_data
    domain_name = get_domain_name_from_startup(startup_data)
    query = f"site.reddit.com list {domain_name} users worst experience"
    print(query)
    num_results = 10
    urls = tavily_search(query, TAVILY_API_KEY, num_results=num_results)
    domain_parts = [part.strip() for part in domain_name.lower().split("in")]
    print(f"Domain parts for matching: {domain_parts}")

    filtered_urls = []
    for url in urls:
        # Convert URL to lowercase for case-insensitive matching
        url_lower = url.lower()
        
        # Check if any domain part exists in the URL
        if any(domain_part in url_lower for domain_part in domain_parts if domain_part):
            filtered_urls.append(url)
            print(f"URL matched: {url}")
        else:
            print(f"URL filtered out: {url}")
    
    print(f"Filtered to {len(filtered_urls)} URLs after domain matching.")
    
    keywords = startup_data11.get('keywords', []) if startup_data11 else []
    startup_summary = startup_data11 if startup_data11 else {}
    urls = filtered_urls
    for i in urls:
        print(i)
    all_pain_points = []
    with ThreadPoolExecutor(max_workers=len(urls) if urls else 1) as post_executor:
        future_to_url = {post_executor.submit(scrape_reddit_post, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                comments = future.result()
                if comments:
                    llm_executor = ThreadPoolExecutor(max_workers=4)
                    llm_futures = [llm_executor.submit(select_top_comments_with_llm, [comment], '', startup_summary) for comment in comments]
                    for fut in as_completed(llm_futures):
                        try:
                            llm_results = fut.result()
                            if llm_results:
                                all_pain_points.extend(llm_results)
                                if len(all_pain_points) >= 10:
                                    print(f"Saved valid comments in memory.")
                                    return all_pain_points[:10]
                        except Exception as e:
                            print(f"⚠️ Error in LLM evaluation: {e}")
            except Exception as e:
                print(f"Error scraping {url}: {e}")
    print(f"Done. Returning data in memory.")
    # Filter out any pain points with null or empty fields
    required_fields = ['pain_point', 'comment', 'relevance_score', 'url']
    filtered_pain_points = [p for p in all_pain_points if all(p.get(f) not in [None, ""] for f in required_fields)]
    # Sort by relevance_score descending
    sorted_pain_points = sorted(filtered_pain_points, key=lambda x: x.get('relevance_score', 0), reverse=True)
    return sorted_pain_points[:10]

# if __name__ == "__main__":
#     # For standalone testing
#     # You can load a startup_summary.json or pass an empty dict
#     try:
#         with open("D:/mahaa_v/outputs/startup_summary.json", "r", encoding="utf-8") as f:
#             startup_data = json.load(f)
#     except Exception:
#         startup_data = {}
#     user_pain_points = run_user_pain_agent(startup_data) 
#     print(user_pain_points)