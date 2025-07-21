# Updated domain.py - Modified to return complete scraped data

import os 
import json
import requests
from .scraping_domain import main 
from dotenv import load_dotenv, find_dotenv

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
2. Return the following information in JSON format:
   - major_domain: The main domain/industry this startup operates in (one word, e.g., "AI", "Fintech","Telemedicine").
   - domain_search: The most specific subdomain or focus area (one word, e.g., "Diabetes").
   - best_title: The most specific, unique, and apt title for this startup idea, based on the data. This should be a concise, creative, and accurate name that captures the essence of the startup. Avoid generic names; be as specific as possible.(For example : "Diabeteic Teleconsultation")

JSON data to analyze:
{json_data}

Please provide your response in JSON format like this:
{{
    "major_domain": "",
    "domain_search": "",
    "best_title": ""
}}
"""
    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": "You are a domain classification and naming assistant. Always respond in JSON format with major_domain, domain_search, and best_title fields."},
            {"role": "user", "content": prompt}
        ],
    }

    try:
        res = requests.post(LLM_API_URL, headers=headers, json=payload)
        res.raise_for_status()
        response = res.json()['choices'][0]['message']['content'].strip()
        
        # Parse the JSON response
        try:
            result = json.loads(response)
            if not all(key in result for key in ['major_domain', 'domain_search', 'best_title']):
                raise ValueError("Response missing required fields")
            return result
        except json.JSONDecodeError:
            # If parsing fails, fall back to old behavior
            return {"major_domain": response, "domain_search": response, "best_title": response}
    except Exception as e:
        print(f"Error in domain classification: {str(e)}")
        return {"major_domain": "Unknown", "domain_search": "Unknown", "best_title": "Unknown"}

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

# 🚀 MAIN - Modified to return complete scraped data
def competitor_agent():
    file_path = r"outputs/startup_summary.json"
    if not os.path.exists(file_path):
        print("Bruhhh 🫠 File not found!")
        return {
            "competitors": [],
            "status": "error",
            "message": "Startup summary file not found"
        }
    
    # Print the domain name from the 'title' key
    domain_name = get_domain_name_from_json(file_path)
    print(f"🌐 Domain Name (from title): {domain_name}")
    
    file_data = read_json_file(file_path)
    domain_info = guess_domain_with_llama3(file_data)
    major_domain = domain_info.get('major_domain', 'Unknown')
    domain_search = domain_info.get('domain_search', major_domain)
    best_title = domain_info.get('best_title', domain_name)

    if(domain_search.lower() == "unknown"):
        major_domain = domain_name
        domain_search = domain_name
    print(f"📂 File: {file_path}")
    print(f"🔍 Detected Major Domain: {major_domain}")
    print(f"🔍 Detected Search Domain: {domain_search}")
    print(f"🏷️  Most Specific Title: {best_title}")

    # 🧠 Form queries using that domain and best title
    prompt1 = f"{domain_search} startups f6s india"
    prompt2 = f"top {major_domain} companies tracxn india"
    prompt3 = f"top {domain_search} companies tracxn india"
    prompt4 = f"top {major_domain} startups f6s india"

    try:
        # Run the scraping process
        main(prompt1, prompt2, prompt3, prompt4)  # This will create final_result.json
        
        # Load the complete results without transformation
        final_result_data = load_final_result()
        
        # Check if it's the "no competitors found" case
        if isinstance(final_result_data, dict) and 'message' in final_result_data:
            print("ℹ️ No competitors found")
            return {
                "competitors": [],
                "status": "no_competitors_found",
                "message": final_result_data['message']
            }
        
        # Return the complete scraped data as-is
        if isinstance(final_result_data, list) and len(final_result_data) > 0:
            print(f"✅ Competitor analysis complete: Found {len(final_result_data)} competitors")
            return {
                "competitors": final_result_data,  # Return the complete scraped data
                "status": "success",
                "competitor_count": len(final_result_data),
                "message": f"Successfully found {len(final_result_data)} competitors with detailed analysis"
            }
        else:
            print("⚠️ No competitor data found")
            return {
                "competitors": [],
                "status": "no_data",
                "message": "No competitor data was found or scraped"
            }
        
    except Exception as e:
        print(f"❌ Error in competitor analysis: {str(e)}")
        return {
            "competitors": [],
            "status": "error",
            "message": f"Error during competitor analysis: {str(e)}"
        }

def competitor_agent_from_data(startup_data: dict):
    """
    In-memory competitor agent: accepts startup_data as dict, returns result as dict, no file I/O.
    """
    # Use the same logic as competitor_agent, but with in-memory data
    try:
        # Use the title from the dict
        domain_name = startup_data.get('title', 'Unknown')
        print(f"🌐 Domain Name (from title): {domain_name}")
        file_data = json.dumps(startup_data, indent=2)
        domain_info = guess_domain_with_llama3(file_data)
        major_domain = domain_info.get('major_domain', 'Unknown')
        domain_search = domain_info.get('domain_search', major_domain)
        best_title = domain_info.get('best_title', domain_name)
        if (domain_search.lower() == "unknown"):
            major_domain = domain_name
            domain_search = domain_name
        print(f"🔍 Detected Major Domain: {major_domain}")
        print(f"🔍 Detected Search Domain: {domain_search}")
        print(f"🏷️  Most Specific Title: {best_title}")
        # Form prompts
        prompt1 = f"{domain_search} startups f6s india"
        prompt2 = f"top {major_domain} companies tracxn india"
        prompt3 = f"top {domain_search} companies tracxn india"
        prompt4 = f"top {major_domain} startups f6s india"
        # Call the new in-memory scraping function
        from competitor_agent.scraping_domain import main_in_memory
        competitor_results = main_in_memory(prompt1, prompt2, prompt3, prompt4)
        if isinstance(competitor_results, dict) and 'message' in competitor_results:
            print("ℹ️ No competitors found")
            return {
                "competitors": [],
                "status": "no_competitors_found",
                "message": competitor_results['message']
            }
        if isinstance(competitor_results, list) and len(competitor_results) > 0:
            print(f"✅ Competitor analysis complete: Found {len(competitor_results)} competitors")
            return {
                "competitors": competitor_results,
                "status": "success",
                "competitor_count": len(competitor_results),
                "message": f"Successfully found {len(competitor_results)} competitors with detailed analysis"
            }
        else:
            print("⚠️ No competitor data found")
            return {
                "competitors": [],
                "status": "no_data",
                "message": "No competitor data was found or scraped"
            }
    except Exception as e:
        print(f"❌ Error in competitor analysis: {str(e)}")
        return {
            "competitors": [],
            "status": "error",
            "message": f"Error during competitor analysis: {str(e)}"
        }