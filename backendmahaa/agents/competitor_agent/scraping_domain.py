import requests
import json
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import cloudscraper
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from tavily import TavilyClient
from dotenv import load_dotenv, find_dotenv
import os
import subprocess
import contextlib
from langchain_together import ChatTogether
from langchain_core.messages import SystemMessage, HumanMessage
# Change to absolute import
from agents.competitor_agent.domain import get_domain_and_prompts
load_dotenv(find_dotenv())
import queue


GOOGLE_API_KEY = ""
GOOGLE_CSE_ID = ""
scraper_api = os.environ.get("SCRAPERAPI_KEY")
output_data = []
scraped_sorted = []
chromedriver_path = r"chromedriver-win64\chromedriver.exe"

# 💥 Step 1: Google Search with ScraperAPI
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

# --- API key rotation for Google and Tavily ---
def scraperapi_search(query, google_keys, cse_ids, tavily_keys):
    GOOGLE_API_KEY = google_keys[0]
    GOOGLE_CSE_ID = cse_ids[0]
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    proxies = {"http": f"http://scraperapi:{scraper_api}@proxy-server.scraperapi.com:8001"}
    print(f"🔍 Searching via Google: {query}")
    try:
        response = requests.get(search_url, proxies=proxies)
        response.raise_for_status()
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0]["link"]
        else:
            print("⚠️ No Google results, trying Tavily as backup...")
    except Exception as e:
        print(f"❌ Error during Google search: {e}\nTrying Tavily as backup...")
    # Tavily fallback with rotation
    for t_idx, tavily_key in enumerate(tavily_keys):
        try:
            tavily_client = TavilyClient(api_key=tavily_key)
            tavily_results = tavily_client.search(query, max_results=1)
            if tavily_results and "results" in tavily_results and len(tavily_results["results"]) > 0:
                return tavily_results["results"][0]["url"]
            else:
                print(f"❌ Tavily (key {t_idx+1}) returned no results.")
        except Exception as e:
            if "usage limit" in str(e).lower() or "rate limit" in str(e).lower():
                print(f"⚠️ Tavily key {t_idx+1} rate limited. Trying next key...")
                continue
            print(f"❌ Error during Tavily search: {e}")
    return None

# 💥 Step 2: Scrape first URL for company names
def get_company_names_from_url(url):
    print(f"🕸️ Crawling first URL for companies: {url}")
    soup = None
    try:
        api_url = f"http://api.scraperapi.com?api_key={scraper_api}&url={url}"
        response = requests.get(api_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        try:
            client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
            extract_response = client.extract(urls=[url])
            if extract_response and 'content' in extract_response:
                soup = BeautifulSoup(extract_response['content'], 'html.parser')
            else:
                print(f"❌ TavilyClient.extract returned no content for {url}.")
                return []
        except Exception as tavily_e:
            print(f"❌ Error with TavilyClient.extract fallback for {url}: {tavily_e}")
            return []

    if soup:
        # 🔍 Find all <a> tags with class exactly ["t-accent", "t-heavy"]
        company_tags = soup.find_all('a', class_='t-accent t-heavy')

        # 🧼 Clean the text and filter out anything sus
        companies = [
            tag.text.strip()
            for tag in company_tags
            if tag.text.strip() and "team" not in tag.text.lower()
        ]

        print(f"✅ Found {len(companies)} companies.\n")
        return companies[:30]  # 🎯 Top 15 only, 'cause we fancy
    return []

# 💥 Step 3: Scraping company pitchbook details (same as before)
def extract_company_details(soup):
    details = {}

    quick_facts = soup.select('div[role="list"][aria-label="Quick Facts"] div[data-pp-overview-item]')
    for fact in quick_facts:
        label = fact.select_one('li.dont-break.text-small')
        value = fact.select_one('span.pp-overview-item__title')
        if label and value:
            details[label.text.strip()] = value.text.strip()

    description = soup.select_one('div[data-general-info-description] p.pp-description_text')
    if description:
        details['Description'] = description.text.strip()

    contact_info = soup.select('div.pp-contact-info div.pp-contact-info_item')
    for info in contact_info:
        label = info.select_one('h5, div.font-weight-bold')
        value = info.select_one('a, div.font-weight-normal')
        if label and value:
            details[label.text.strip()] = value.text.strip()

    office = soup.select_one('div.pp-contact-info_corporate-office')
    if office:
        address_lines = office.select('ul.list-type-none li')
        details['Address'] = [line.text.strip() for line in address_lines]

    social_links = soup.select('div.info-item__social a')
    details['Social Media'] = {link.get('aria-label').replace(' link', ''): link.get('href') for link in social_links}

    industries = soup.select('div.pp-contact-info_item div.font-weight-normal')
    details['Industries'] = [industry.text.strip() for industry in industries if 'Industry' in industry.find_previous('div').text]

    verticals = soup.select('div.pp-contact-info_item a.font-underline')
    details['Verticals'] = [vertical.text.strip() for vertical in verticals]

    faqs = soup.select('ul.pp-faqs-table li')
    for faq in faqs:
        question = faq.select_one('h3')
        answer = faq.select_one('p')
        if question and answer:
            details[question.text.strip()] = answer.text.strip()

    return details

# fallback to selenium if cloudscraper fails
def scrape_with_selenium(url, chromedriver_path=None):
    print(f"\U0001F310 Scraping with Selenium: {url}")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    # Set a user-agent to help avoid bot detection
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Suppress most ChromeDriver logs
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
                time.sleep(3)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                return extract_company_details(soup)
            finally:
                driver.quit()
    except OSError as e:
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def scrape_with_cloudscraper(url, max_retries=3, backoff_factor=5):
    print(f"🌐 Scraping with cloudscraper: {url}")
    for attempt in range(max_retries):
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return extract_company_details(soup)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                wait = backoff_factor * (2 ** attempt)
                return scrape_with_selenium(url, chromedriver_path)
            else:
                return scrape_with_selenium(url, chromedriver_path)
        except Exception as e:
            return scrape_with_selenium(url, chromedriver_path)
    return scrape_with_selenium(url, chromedriver_path)

def save_json(data, filename='final_output.json'):
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../outputs', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"💾 Saved to {filepath}")

# 💥 Full Flow: Run it all
def extract_company_names_from_url(url):
    print(f"🕸️ Crawling via ScraperAPI: {url}")
    soup = None
    try:
        api_url = f"http://api.scraperapi.com?api_key={scraper_api}&url={url}"
        response = requests.get(api_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        try:
            client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
            extract_response = client.extract(urls=[url])
            if extract_response and 'content' in extract_response:
                soup = BeautifulSoup(extract_response['content'], 'html.parser')
            else:
                return []
        except Exception as tavily_e:
            return []
    
    if soup:
        # Check for anchor tags with company names (existing selectors)
        company_tags = [
            tag for tag in soup.find_all('a')
            if set(tag.get('class', [])) == set(['txn--font-16', 'txn--text-color-mine-shaft'])
        ]
        companies = [tag.text.strip() for tag in company_tags if tag.text.strip() and "team" not in tag.text.lower()]

        # Additional scraping method to cover other domains (existing)
        additional_tags = [
            tag for tag in soup.find_all('a')
            if set(tag.get('class', [])) == set(['txn--text-color-mine-shaft'])
        ]
        additional_companies = [tag.text.strip() for tag in additional_tags if tag.text.strip() and "team" not in tag.text.lower()]  # Limit to top 10


        # NEW: Also extract from <a class="txn--text-decoration-none txn--text-color-mine-shaft">
        extra_tags = [
            tag for tag in soup.find_all('a')
            if set(tag.get('class', [])) == set(['txn--text-decoration-none', 'txn--text-color-mine-shaft'])
        ]
        extra_companies = [tag.text.strip() for tag in extra_tags if tag.text.strip() and "team" not in tag.text.lower()]

        # Combine all lists and deduplicate
        all_companies = companies + additional_companies + extra_companies
        # Filter only valid company names (excluding social media and email links)
        valid_companies = [company for company in all_companies if not any(platform in company.lower() for platform in ['linkedin', 'twitter', 'facebook', 'email', 'contact', 'team', 'overview','companies','company','about'])]
        # Deduplicate while preserving order
        seen = set()
        deduped_companies = []
        for company in valid_companies:
            if company not in seen:
                deduped_companies.append(company)
                seen.add(company)
        # Limit to top 20 results
        deduped_companies = deduped_companies[:30]
        return deduped_companies
    return []
    
def scrape_company(company, google_api_key, cse_id, tavily_keys):
    try:
        pitchbook_query = f"{company} pitchbook"
        pitchbook_url = scraperapi_search(pitchbook_query, [google_api_key], [cse_id], tavily_keys)
        if pitchbook_url:
            details = scrape_with_cloudscraper(pitchbook_url)
            return {
                "company_name": company,
                "searched_url": pitchbook_url,
                "details": details
            }
        else:
            print(f"❌ Skipped {company} (no pitchbook URL)")
            return None
    except Exception as e:
        print(f"❌ Error scraping company {company}: {e}")
        return None

def get_sorted_companies_llm(startup_data, domain_search, major_domain, company_list):
    """
    You are an assistant that splits a list of companies into direct and indirect competitors for a startup.
    """
    title = startup_data.get('title', '')
    description = startup_data.get('description', '')
    main_feature = startup_data.get('main_feature', '')
    tech_stack = startup_data.get('tech_stack', [])
    delivery_model = "online" if "online" in description.lower() or "online" in title.lower() else "offline"
    prompt = f"""
You are an expert startup analyst. Given the following startup summary and a list of companies, split the companies into two categories:
- "direct_competitors": Companies that solve the same problem, serve the same users, and use a similar platform, technology, and delivery model as the startup.
- "indirect_competitors": Companies that are in a related domain or market but do not directly compete with the startup's core offering.

Startup summary:
{json.dumps(startup_data, ensure_ascii=False)}

Domain: {domain_search}
Major Domain: {major_domain}
Tech Stack: {tech_stack}
Delivery Model: {delivery_model}

Company list:
{json.dumps(company_list, ensure_ascii=False)}

Instructions:
- For each company, use your knowledge and any available public information to determine if it is a direct or indirect competitor.
- Only include companies you can reasonably classify.
- In indirect competitors, make sure to give the list in the sorted order based on the similarity to the startup and also quite popular in the market.
- Return ONLY a JSON object with two arrays: "direct_competitors" and "indirect_competitors". Example:
{{
  "direct_competitors": ["Company1", "Company2"],
  "indirect_competitors": ["Company3", "Company4"]
}}
"""
    lc_messages = [
        SystemMessage(content="You are a helpful assistant that splits companies into direct and indirect competitors for a startup."),
        HumanMessage(content=prompt)
    ]
    llm = ChatTogether(
        together_api_key=os.environ.get("TOGETHER_API_KEY2"),
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    )
    try:
        response = llm.invoke(lc_messages)
        content = response.content.strip()
        content = content.replace('```json', '').replace('```', '').strip()
        competitors = json.loads(content)
        if isinstance(competitors, dict):
            return competitors
    except Exception as e:
        print(f"❌ Error getting sorted companies from LLM: {e}")
    # fallback: treat all as direct
    return {"direct_competitors": company_list, "indirect_competitors": []}

# --- NEW: LLM prompt to get top 5 competitors in major_domain ---
def get_top_competitors_llm(domain_search, major_domain, startup_data):
    import os
    import json
    title = startup_data.get('title', 'Unknown')
    prompt = f"""
You are an expert in startup and tech market research for companies in India. List the top 10 companies that are best-known competitors for the startup data: '{json.dumps(startup_data, ensure_ascii=False)}'
ALL companies you return must be based in India or have significant operations in India. Ignore companies that are not Indian or do not have a major presence in India.
Be sure to include the top competitors from both the specific domain and the broader major domain.
Return ONLY a valid JSON array of company names, e.g. [\"Company1\", \"Company2\", ...].
Do not include any explanations, markdown, or extra text.
"""
    from langchain_together import ChatTogether
    from langchain_core.messages import SystemMessage, HumanMessage
    lc_messages = [
        SystemMessage(content="You are a competitor company finder in India. Always respond with a JSON array of company names that are based in India or have significant operations in India. Include the top competitors from both the domain and major domain. No extra text."),
        HumanMessage(content=prompt)
    ]
    llm = ChatTogether(
        together_api_key=os.environ.get("TOGETHER_API_KEY2"),
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    )
    try:
        response = llm.invoke(lc_messages)
        content = response.content.strip()
        content = content.replace('```json', '').replace('```', '').strip()
        companies = json.loads(content)
        if isinstance(companies, list):
            return [c for c in companies if isinstance(c, str)]
    except Exception as e:
        print(f"❌ Error getting top competitors: {e}")
    return []


def is_valid_company(company):
    details = company.get("details", {})
    if not details:
        return False
    if (
        not details.get("Industries") and
        not details.get("Verticals") and
        not details.get("Social Media")
    ):
        return False
    return True


def main(primary_prompt, secondary_prompt, third_prompt, fourth_prompt, domain_name, domain_search, major_domain, startup_data):
    import os
    import json

    all_companies = []
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../outputs')
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Add this line:
    tavily_keys = get_env_keys("TAVILY_API_KEY")

    # Always create the output files, even if empty
    final_output_path = os.path.join(OUTPUT_DIR, "final_result.json")
    competitor_analysis_path = os.path.join(OUTPUT_DIR, "final_result.json")

    # --- Parallelize the four search queries ---
    search_prompts = [
        (primary_prompt, 'primary'),
        (secondary_prompt, 'secondary'),
        (third_prompt, 'third'),
        (fourth_prompt, 'fourth')
    ]
    def search_and_extract(prompt, api_key, cse_id, label):
        url = scraperapi_search(prompt, api_key, cse_id, tavily_keys)
        print(f"DEBUG: {label.capitalize()} Search URL: {url}")
        if url:
            if label in ['primary', 'fourth']:
                return get_company_names_from_url(url)
            else:
                return extract_company_names_from_url(url)
        else:
            print(f"⚠️ Couldn't get {label} result. Moving on...")
            return []

    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_label = {
            executor.submit(search_and_extract, prompt, GOOGLE_API_KEY, GOOGLE_CSE_ID, label): label
            for prompt, label in search_prompts
        }
        for future in as_completed(future_to_label):
            label = future_to_label[future]
            try:
                results[label] = future.result()
            except Exception as e:
                print(f"⚠️ Error in {label} search: {e}")
                results[label] = []

    # Combine all results into all_companies
    all_companies = results.get('primary', []) + results.get('fourth', []) + results.get('secondary', []) + results.get('third', [])

    # Detect major_domain from startup_data
    if startup_data:
        llm_companies = get_top_competitors_llm(domain_search, major_domain, startup_data)
        print(f"🔎Top 5 competitors for startup '{startup_data.get('title', 'Unknown')}': {llm_companies}")
        all_companies = llm_companies + all_companies

    # Deduplicate before proceeding
    all_companies = list(dict.fromkeys(all_companies))
    # LLM sort
    if startup_data and all_companies:
        sorted_companies = get_sorted_companies_llm(startup_data,domain_search, major_domain, all_companies)
    else:
        sorted_companies = all_companies
    # Scrape company details for sorted list
    
    api_keys = [
        os.environ.get("GOOGLE_API_KEY1"),
        os.environ.get("GOOGLE_API_KEY2"),
        os.environ.get("GOOGLE_API_KEY3")
    ]
    cse_ids = [
        os.environ.get("GOOGLE_CSE_ID1"),
        os.environ.get("GOOGLE_CSE_ID2"),
        os.environ.get("GOOGLE_CSE_ID3"),
        os.environ.get("GOOGLE_CSE_ID4"),
        os.environ.get("GOOGLE_CSE_ID5"),
        os.environ.get("GOOGLE_CSE_ID6")
    ]
    api_cse_pairs = [
        (api_keys[0], cse_ids[0]),
        (api_keys[0], cse_ids[1]),
        (api_keys[1], cse_ids[2]),
        (api_keys[1], cse_ids[3]),
        (api_keys[2], cse_ids[4]),
        (api_keys[2], cse_ids[5])
    ]
    # Scrape company details for sorted list in parallel
    scraped_sorted = []

    # Extract direct_companies from sorted_companies if available
    if isinstance(sorted_companies, dict) and "direct_competitors" in sorted_companies:
        direct_companies = sorted_companies["direct_competitors"]
        indirect_companies = sorted_companies.get("indirect_competitors", [])
        if indirect_companies:
            indirect_companies = indirect_companies[:10]
        company_order = direct_companies + indirect_companies
        print(f"Company order: {company_order}")
    else:
        company_order = sorted_companies
        direct_companies = sorted_companies if isinstance(sorted_companies, list) else []

    api_cse_queue = queue.Queue()
    for pair in api_cse_pairs:
        api_cse_queue.put(pair)

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_company = {
            executor.submit(
                scrape_company_with_pool,
                company,
                api_cse_queue,
                tavily_keys
            ): company
            for company in company_order
        }
        for future in as_completed(future_to_company):
            result = future.result()
            if result and is_valid_company(result):
                scraped_sorted.append(result)

    # Sort so direct competitors come first, preserving LLM order
    scraped_sorted.sort(
        key=lambda c: (
            c["company_name"] not in direct_companies,
            direct_companies.index(c["company_name"]) if c["company_name"] in direct_companies else 9999
        )
    )

    # Instead, just return the data as a list from the function(s) that previously saved to file.
    return scraped_sorted


def main_in_memory(primary_prompt, secondary_prompt, third_prompt, fourth_prompt, domain_name, domain_search, major_domain, startup_data):
    """In-memory version of main() that doesn't use files, now with API key rotation"""
    competitors = []
    try:
        google_keys = get_env_keys("GOOGLE_API_KEY")
        cse_ids = get_env_keys("GOOGLE_CSE_ID")
        tavily_keys = get_env_keys("TAVILY_API_KEY")
        urls = []
        for prompt in [primary_prompt, secondary_prompt, third_prompt, fourth_prompt]:
            url = scraperapi_search(prompt, google_keys, cse_ids, tavily_keys)
            if url:
                urls.append(url)
        # Scrape companies from URLs
        all_companies = []
        for url in urls:
            companies = get_company_names_from_url(url)
            all_companies.extend(companies)
        # Remove duplicates
        all_companies = list(set(all_companies))
        #Get detailed info for each company
        for company in all_companies:
            details = scrape_company(company, google_keys, cse_ids, tavily_keys)
            if details:
                competitors.append(details)
        return {
            "competitors": competitors,
            "total": len(competitors),
            "domain": domain_search,
            "major_domain": major_domain
        }
    except Exception as e:
        print(f"❌ Error in competitor scraping: {e}")
        return {
            "competitors": [],
            "total": 0,
            "error": str(e)
        }


def scrape_company_with_pool(company, api_cse_queue, tavily_keys):
    api_key, cse_id = api_cse_queue.get()
    try:
        print(f"[POOL] Scraping '{company}' with API key: {api_key}, CSE ID: {cse_id}")
        result = scrape_company(company, api_key, cse_id, tavily_keys)
        return result
    finally:
        api_cse_queue.put((api_key, cse_id))


if __name__ == "__main__":
    # Example prompts and startup data for testing
    primary_prompt = f"top diabetes startups f6s india"
    secondary_prompt = f"top telemedicine companies tracxn india"
    third_prompt = f"top diabetes companies tracxn india"
    fourth_prompt = f"top telemedicine startups f6s india"
    domain_name = "HealthTech"
    domain_search = "diabetes"
    major_domain = "telemedicine"
    startup_data = {
        "title": "AI Health Platform",
        "description": "A platform using AI to provide digital health solutions in India.",
        "tech_stack": ["Python", "TensorFlow", "React"],
        "domain": "diabetes",
        "major_domain": "telemedicine"
    }

    print("🚀 Running competitor scraping pipeline test...")
    scraped_companies = main(
        primary_prompt,
        secondary_prompt,
        third_prompt,
        fourth_prompt,
        domain_name,
        domain_search,
        major_domain,
        startup_data
    )

    print(scraped_companies)






