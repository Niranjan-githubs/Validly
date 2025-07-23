# Updated domain.py - Merged with all paste2 functionalities

import os 
import json
import requests
import threading
from .scraping_domain import main 
from .venture_angel import main3
from dotenv import load_dotenv, find_dotenv
from langchain_together import ChatTogether
from langchain_core.messages import SystemMessage, HumanMessage
from pathlib import Path

load_dotenv(find_dotenv())

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
    "domain_search": ""
}}
"""
    
    # Use LangChain approach for better error handling
    lc_messages = [
        SystemMessage(content="You are a domain classification and naming assistant. Always respond in JSON format with major_domain, domain_search fields."),
        HumanMessage(content=prompt)
    ]
    llm = ChatTogether(
        together_api_key=os.environ.get("TOGETHER_API_KEY2"),
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

def load_final_result():
    """Load the final_result.json file and return its contents"""
    try:
        with open('final_result.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ final_result.json not found")
        return []
    except json.JSONDecodeError:
        print("❌ Error parsing final_result.json")
        return []

def load_all_investors():
    """Load and merge all investors as a list."""
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

# 🚀 MAIN - Updated with paste2 functionality (accepts startup_data parameter)
def competitor_agent(startup_data=None):
    """
    Main competitor agent function - now accepts startup_data as parameter
    Falls back to file reading if no data provided (backward compatibility)
    """
    # Handle both parameter and file-based input for backward compatibility
    if startup_data is None:
        # Fallback to original file-based approach
        file_path = r"outputs/startup_summary.json"
        if not os.path.exists(file_path):
            print("Bruhhh 🫠 File not found!")
            return {
                "gaps": [],
                "competitors": [],
                "analysis": "Startup summary file not found",
                "competitor_count": 0,
                "status": "error",
                "message": "Startup summary file not found"
            }
        
        domain_name = get_domain_name_from_json(file_path)
        file_data = read_json_file(file_path)
    else:
        # Use provided startup_data
        if not startup_data:
            print("Bruhhh 🫠 No startup data provided!")
            return {
                "gaps": [],
                "competitors": [],
                "analysis": "No startup data provided",
                "competitor_count": 0,
                "status": "error",
                "message": "No startup data provided"
            }
        
        domain_name = startup_data.get('title', 'Unknown')
        file_data = json.dumps(startup_data, indent=2)
    
    print(f"🌐 Domain Name (from title): {domain_name}")
    
    domain_info = guess_domain_with_llama3(file_data)
    major_domain = domain_info.get('major_domain', 'Unknown')
    domain_search = domain_info.get('domain_search', major_domain)

    if(domain_search.lower() == "unknown"):
        major_domain = domain_name
        domain_search = domain_name
        
    print(f"🔍 Detected Major Domain: {major_domain}")
    print(f"🔍 Detected Search Domain: {domain_search}")

    try:
        # 🧠 Form queries using that domain
        prompt1 = f"{domain_search} startups f6s india"
        prompt2 = f"top {major_domain} companies tracxn india"
        prompt3 = f"top {domain_search} companies tracxn india"
        prompt4 = f"top {major_domain} startups f6s india"
        prompt5 = f"{major_domain} sector startup investors india"

        # Start the parallel thread for investors
        parallel_thread = threading.Thread(target=main3, args=(prompt5,))
        parallel_thread.start()

        # Run the scraping process in the main thread
        if startup_data:
            main(prompt1, prompt2, prompt3, prompt4, startup_data)
        
        
        # Wait for the parallel thread to complete
        parallel_thread.join()
        
        # Load the complete results without transformation
        final_result_data = load_final_result()
        
        # Check if it's the "no competitors found" case
        if isinstance(final_result_data, dict) and 'message' in final_result_data:
            print("ℹ️ No competitors found")
            return {
                "gaps": [],
                "competitors": [],
                "analysis": f"No competitors found for domain: {major_domain} / {domain_search}",
                "competitor_count": 0,
                "status": "no_competitors_found",
                "message": final_result_data['message']
            }
        
        # Return the complete scraped data as-is
        if isinstance(final_result_data, list) and len(final_result_data) > 0:
            print(f"✅ Competitor analysis complete: Found {len(final_result_data)} competitors")
            return {
                "gaps": [],  # If you have gap analysis, fill here
                "competitors": final_result_data,  # Return the complete scraped data
                "analysis": f"Found {len(final_result_data)} competitors for domain: {major_domain} / {domain_search}",
                "competitor_count": len(final_result_data),
                "status": "success",
                "message": f"Successfully found {len(final_result_data)} competitors with detailed analysis"
            }
        else:
            print("⚠️ No competitor data found")
            return {
                "gaps": [],
                "competitors": [],
                "analysis": f"No competitor data found for domain: {major_domain} / {domain_search}",
                "competitor_count": 0,
                "status": "no_data",
                "message": "No competitor data was found or scraped"
            }
        
    except Exception as e:
        print(f"❌ Error in competitor analysis: {str(e)}")
        return {
            "gaps": [],
            "competitors": [],
            "analysis": f"Error during competitor analysis: {str(e)}",
            "competitor_count": 0,
            "status": "error",
            "message": f"Error during competitor analysis: {str(e)}"
        }

def competitor_agent_from_data(startup_data: dict):
    """
    In-memory competitor agent: accepts startup_data as dict, returns result as dict, no file I/O.
    This is now just a wrapper around the main competitor_agent function.
    """
    return competitor_agent(startup_data)