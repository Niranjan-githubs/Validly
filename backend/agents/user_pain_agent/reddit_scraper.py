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
from agents.user_pain_agent.llm_summarizer import select_top_comments_with_llm, save_single_comment_append, load_startup_summary
from agents.competitor_agent.domain import guess_domain_with_llama3
chromedriver_path = r"D:\mahaa_v\chromedriver-win64\chromedriver.exe"

TAVILY_API_KEY = "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"
def get_env_keys(prefix):
    keys = []
    idx = 1
    while True:
        key = os.environ.get(f"{prefix}{idx}")
        if key:
            keys.append(key)
            idx += 1
        else:
            break
    return keys

def tavily_search(query, num_results=10):
    tavily_keys = get_env_keys("TAVILY_API_KEY")
    for t_idx, tavily_key in enumerate(tavily_keys):
        try:
            client = TavilyClient(api_key=tavily_key)
            response = client.search(query=query, max_results=num_results)
            reddit_urls = [item['url'] for item in response.get('results', []) if 'reddit.com/r/' in item['url']]
            return reddit_urls
        except Exception as e:
            if "usage limit" in str(e).lower() or "rate limit" in str(e).lower():
                print(f"⚠️ Tavily key {t_idx+1} rate limited. Trying next key...")
                continue
            print(f"❌ Error during Tavily search: {e}")
    return []

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
    # Use guess_domain_with_llama3 to get the major domain
    import json
    domain_info = guess_domain_with_llama3(json.dumps(startup_data))
    domain1 = domain_info.get('domain_search', 'Unknown')
    domain2 = domain_info.get('major_domain', 'Unknown')
    do = domain1 + " " + domain2
    return do

import os
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../outputs')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def run_user_pain_agent(startup_data: dict) -> list:
    # Clear the output file at the start of each run
    output_file = os.path.join(OUTPUT_DIR, "pain_points_llm.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([], f)

    startup_data11 = startup_data
    # Get the domain name dynamically
    domain_name = get_domain_name_from_startup(startup_data)
    query = f"site.reddit.com list {domain_name} users worst experience"
    num_results = 10
    urls = tavily_search(query, num_results=num_results)
    print(f"Found {len(urls)} Reddit URLs.")
    # Use startup_data for keywords if available
    keywords = startup_data11.get('keywords', []) if startup_data11 else []

    # Scrape posts in parallel
    # Change to absolute import
    from agents.user_pain_agent.llm_summarizer import select_top_comments_with_llm, save_single_comment_append, load_startup_summary
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time

    def process_comment_llm(comment, startup_summary, keywords, output_file):
        llm_results = select_top_comments_with_llm([comment], '', startup_summary, filename=output_file)
        for llm_comment in llm_results:
            save_single_comment_append(llm_comment, keywords, filename=output_file)

    def chunked_iterable(iterable, size):
        for i in range(0, len(iterable), size):
            yield iterable[i:i+size]

    # Use startup_data as summary for LLM
    startup_summary = startup_data11 if startup_data11 else {}

    with ThreadPoolExecutor(max_workers=len(urls) if urls else 1) as post_executor:
        future_to_url = {post_executor.submit(scrape_reddit_post, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                comments = future.result()
                if comments:
                    # LLM parallelization: at most 4 jobs in parallel, use as_completed
                    llm_executor = ThreadPoolExecutor(max_workers=4)
                    llm_futures = []
                    for comment in comments:
                        llm_futures.append(llm_executor.submit(process_comment_llm, comment, startup_summary, keywords, output_file))
                        while len(llm_futures) >= 4:
                            for fut in as_completed(llm_futures, timeout=None):
                                try:
                                    fut.result()
                                except Exception as e:
                                    print(f"⚠️ Error in LLM evaluation: {e}")
                                llm_futures.remove(fut)
                                break  # Only remove one completed future, then continue
                        # Check if we've reached 10 valid comments in the output file
                        try:
                            with open(output_file, "r", encoding="utf-8") as f:
                                current_comments = json.load(f)
                                if isinstance(current_comments, list) and len(current_comments) >= 7:
                                    print(f"Saved valid comments in {output_file}.")
                                    return current_comments
                        except Exception:
                            pass
                    # Wait for any remaining LLM jobs to finish
                    for fut in as_completed(llm_futures):
                        try:
                            fut.result()
                        except Exception as e:
                            print(f"⚠️ Error in LLM evaluation: {e}")
                        # Check if we've reached 10 valid comments in the output file
                        try:
                            with open(output_file, "r", encoding="utf-8") as f:
                                current_comments = json.load(f)
                                if isinstance(current_comments, list) and len(current_comments) >= 7:
                                    print(f" Saved valid comments in {output_file}.")
                                    return current_comments
                        except Exception:
                            pass
            except Exception as e:
                print(f"Error scraping {url}: {e}")
    print(f"Done. Data saved to {output_file}")
    # Load and return the pain points
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            pain_points = json.load(f)
    except Exception:
        pain_points = []
    return pain_points

if __name__ == "__main__":
    # For standalone testing
    # You can load a startup_summary.json or pass an empty dict
    try:
        with open("D:/mahaa_v/outputs/startup_summary.json", "r", encoding="utf-8") as f:
            startup_data = json.load(f)
    except Exception:
        startup_data = {}
    run_user_pain_agent(startup_data) 