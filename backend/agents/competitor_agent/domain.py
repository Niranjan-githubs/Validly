# Updated domain.py - Modified to return complete scraped data

import os 
import json
import requests
from dotenv import load_dotenv, find_dotenv
import threading
#from competitor_agent.venture_angel import main3
from langchain_together import ChatTogether
from langchain_core.messages import SystemMessage, HumanMessage
from pathlib import Path
load_dotenv(find_dotenv())
import asyncio
from typing import Dict, Any

LLM_API_URL = "https://api.together.xyz/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ.get('TOGETHER_API_KEY2')}",
    "Content-Type": "application/json"
}

def guess_domain_with_llama3(json_data):
    prompt = f"""
You are an expert in analyzing startup and tech data. Your task is to:

1. Carefully read the provided JSON data about a startup.
Also make sure to decide the domain based on their tech stack. 
2. Return the following information in JSON format:
   - major_domain: The main domain/industry this startup operates in (one word, e.g., "AI","Telemedicine", Edtech).
   - domain_search: The most specific subdomain or focus area (one word, e.g., "Diabetes", "Multilingual", "AI agents", "AI based startups").
JSON data to analyze:
{json_data}

Please provide your response in JSON format like this:
{{
    "major_domain": "",
    "domain_search": "",
}}
"""
    lc_messages = [
        SystemMessage(content="You are a domain classification and naming assistant. Always respond in JSON format with major_domain, domain_searchfields."),
        HumanMessage(content=prompt)
    ]
    llm = ChatTogether(
        together_api_key=os.environ.get("TOGETHER_API_KEY4"),
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    )
    try:
        response = llm.invoke(lc_messages)
        content = response.content.strip()
        try:
            result = json.loads(content)
            if not all(key in result for key in ['major_domain', 'domain_search']):
                raise ValueError("Response missing required fields")
            return result
        except json.JSONDecodeError:
            # Try to extract fields from string output
            major_domain = "Unknown"
            domain_search = "Unknown"
            if "major_domain" in content and "domain_search" in content:
                for line in content.splitlines():
                    if "major_domain" in line:
                        major_domain = line.split(":", 1)[-1].replace('"', '').replace(",", '').replace("'", '').strip()
                    if "domain_search" in line:
                        domain_search = line.split(":", 1)[-1].replace('"', '').replace(",", '').replace("'", '').strip()
            return {"major_domain": major_domain, "domain_search": domain_search}
    except Exception as e:
        print(f"Error in domain classification: {str(e)}")
        return {"major_domain": "Unknown", "domain_search": "Unknown"}

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return json.dumps(data, indent=2)

def get_domain_name_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data.get('title', 'Unknown')

def load_final_result(output_dir):
    """Load the final_result.json file and return its contents"""
    try:
        with open(r'D:\mahaa_v\outputs\final_result.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ final_result.json not found")
        return []
    except json.JSONDecodeError:
        print("❌ Error parsing final_result.json")
        return []

def new_parallel_function():
    """Placeholder for the new function to run in parallel."""
    print("✨ Running new parallel function...")
    # Add your code here for the function you want to run in parallel
    # For demonstration, let's just sleep for a bit
    # import time
    # time.sleep(5)
    print("✅ New parallel function finished.")

# 🚀 MAIN - Modified to return complete scraped data
# Remove file-based functions
async def competitor_agent(startup_data: Dict[str, Any]) -> Dict[str, Any]:
    """Modified to work with in-memory data only"""
    if not startup_data:
        print("❌ No startup data provided!")
        return {
            "gaps": [],
            "competitors": [],
            "analysis": "No startup data provided",
            "competitor_count": 0,
            "status": "error",
            "message": "No startup data provided"
        }
    
    info = get_domain_and_prompts(startup_data)
    domain_name = info["domain_name"]
    major_domain = info["major_domain"]
    domain_search = info["domain_search"]
    prompt1 = info["prompt1"]
    prompt2 = info["prompt2"]
    prompt3 = info["prompt3"]
    prompt4 = info["prompt4"]

    print(f"🌐 Domain Name (from title): {domain_name}")
    print(f"🔍 Detected Major Domain: {major_domain}")
    print(f"🔍 Detected Search Domain: {domain_search}")

    try:
        prompt5 = f"{major_domain} sector startup investors india"
        
        # Import scraping_domain here to avoid circular imports
        from agents.competitor_agent.scraping_domain import main_in_memory
        
        # Get competitor data directly without saving to files
        competitor_data = main_in_memory(
            primary_prompt=prompt1,
            secondary_prompt=prompt2,
            third_prompt=prompt3,
            fourth_prompt=prompt4,
            domain_name=domain_name,
            domain_search=domain_search,
            major_domain=major_domain,
            startup_data=startup_data
        )
        
        if not competitor_data or not competitor_data.get('competitors'):
            return {
                "gaps": [],
                "competitors": [],
                "analysis": f"No competitors found for domain: {major_domain} / {domain_search}",
                "competitor_count": 0,
                "status": "no_competitors_found"
            }
        
        return {
            "gaps": [],  # Future: Add gap analysis here
            "competitors": competitor_data['competitors'],
            "analysis": f"Found {len(competitor_data['competitors'])} competitors",
            "competitor_count": len(competitor_data['competitors']),
            "status": "success"
        }

    except Exception as e:
        print(f"❌ Error in competitor analysis: {str(e)}")
        return {
            "gaps": [],
            "competitors": [],
            "analysis": f"Error during competitor analysis: {str(e)}",
            "competitor_count": 0,
            "status": "error"
        }

def get_domain_and_prompts(startup_data):
    """
    Returns domain_name, major_domain, domain_search, the 4 prompts, and startup_data.
    All three (domain_name, major_domain, domain_search) are derived from the LLM output.
    """
    file_data = json.dumps(startup_data, indent=2)
    domain_info = guess_domain_with_llama3(file_data)
    # Always get all three from LLM output
    domain_name = domain_info.get('domain_name', 'Unknown')
    major_domain = domain_info.get('major_domain', 'Unknown')
    domain_search = domain_info.get('domain_search', major_domain)

    # Fallbacks if LLM output is missing
    if not domain_name or domain_name.lower() == "unknown":
        domain_name = major_domain if major_domain != "Unknown" else domain_search
    if not major_domain or major_domain.lower() == "unknown":
        major_domain = domain_search if domain_search != "Unknown" else domain_name
    if not domain_search or domain_search.lower() == "unknown":
        domain_search = major_domain if major_domain != "Unknown" else domain_name

    prompt1 = f"{domain_search} startups f6s india"
    prompt2 = f"top {major_domain} companies tracxn india"
    prompt3 = f"top {domain_search} companies tracxn india"
    prompt4 = f"top {major_domain} startups f6s india"

    return {
        "domain_name": domain_name,
        "major_domain": major_domain,
        "domain_search": domain_search,
        "prompt1": prompt1,
        "prompt2": prompt2,
        "prompt3": prompt3,
        "prompt4": prompt4,
        "startup_data": startup_data
    }

# Helper to load and merge venture.json and angel.json investors

def load_all_investors():
    """Load and merge all investors as a list."""
    import json
    from pathlib import Path
    investors = []
    investor_path = Path(__file__).parent / 'investors.json'
    try:
        if investor_path.exists():
            with open(investor_path, 'r', encoding='utf-8') as f:
                investor_data = json.load(f)
                investors.extend(investor_data.get('investors', []))
    except Exception as e:
        print(f"❌ Error loading investors.json: {e}")
    return investors

if __name__ == "__main__":
    # Example: Load startup_data from a JSON file (or define inline for testing)
    import sys

    # Option 1: Load from file if provided as argument
    if len(sys.argv) > 1:
        startup_json_path = sys.argv[1]
        with open(startup_json_path, "r", encoding="utf-8") as f:
            startup_data = json.load(f)
    else:
        # Option 2: Use a sample startup_data dict for testing
        startup_data = {
            "title": "Diabetes AI Health Platform",
            "description": "An online platform using AI and analytics to help diabetes patients manage their health.",
            "tech_stack": ["Python", "AI", "Cloud", "Analytics"],
            "domain": "Diabetes",
            "major_domain": "Telemedicine"
        }

    print("🚀 Running competitor_agent with startup_data:")
    print(json.dumps(startup_data, indent=2))

    result = competitor_agent(startup_data)
    print("\n=== Competitor Agent Result ===")
    print(json.dumps(result, indent=2))