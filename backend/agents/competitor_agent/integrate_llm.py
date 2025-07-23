import json
import textwrap
from typing import Dict, List, Any
from together import Together
import os
from dotenv import load_dotenv, find_dotenv
from langchain_together import ChatTogether
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv(find_dotenv())

# Multiple API keys for rotation
TOGETHER_API_KEYS = [
    os.environ.get("TOGETHER_API_KEY2"),
    os.environ.get("TOGETHER_API_KEY3"),
    os.environ.get("TOGETHER_API_KEY4"),
    # Add more keys as needed
]

# Dynamic output directory creation
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def clean_json_to_text(data: Any, title="") -> str:
    text = f"\n📌 {title}:\n"
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                text += f"{k}:\n"
                for sk, sv in v.items():
                    text += f" - {sk}: {sv}\n"
            elif isinstance(v, list):
                items = v[:5]
                text += f"{k}: {', '.join(map(str, items))}\n"
                if len(v) > 5:
                    text += f" - ... and {len(v) - 5} more items\n"
            else:
                text += f"{k}: {v}\n"
    elif isinstance(data, list):
        items = data[:5]
        for i, item in enumerate(items):
            text += f"Item {i + 1}:\n"
            if isinstance(item, dict):
                for k, v in item.items():
                    text += f" - {k}: {v}\n"
            else:
                text += f" - {item}\n"
        if len(data) > 5:
            text += f" - ... and {len(data) - 5} more items\n"
    return text

def load_json_files() -> Dict:
    try:
        path1 = os.path.join(OUTPUT_DIR, "startup_summary.json")
        with open(path1, 'r', encoding='utf-8') as f:
            startup_data = json.load(f)
        return startup_data
    except FileNotFoundError as e:
        print(f"Error loading JSON files: {e}")
        return {}

def prepare_optimized_prompt(startup_data: Dict, competitor_data: Dict) -> List[Dict]:
    startup_info = {
        "name": startup_data.get("name", ""),
        "desc": startup_data.get("description", "")[:50],
        "web": startup_data.get("website", ""),
        "feat": startup_data.get("features", [])[:1] if startup_data.get("features") else ["Feature 1"],
        "price": startup_data.get("pricing", "") or "Subscription-based model",
        "fund": startup_data.get("funding", "")
    }
    competitors_info = []
    for comp in competitor_data:
        details = comp.get("details", {})
        company_name = comp.get("company_name", "")
        funding_key = f"How much funding has {company_name} raised over time?"
        funding_info = details.get(funding_key, "")
        funding_amount = 0
        if funding_info:
            import re
            numbers = re.findall(r'\d+\.?\d*', funding_info)
            if numbers:
                funding_amount = float(numbers[0])
        investors_key = f"Who are {company_name}'s investors?"
        investors = details.get(investors_key, "")
        if investors:
            investors = [inv.strip() for inv in investors.split(",")[:2]]
        description = details.get("Description", "")[:50]
        features = []
        if description:
            sentences = [s.strip() for s in description.split(".") if s.strip()]
            features = [s for s in sentences[:1] if len(s) > 10]
        if not features:
            features = ["Core Service"]
        comp_info = {
            "n": company_name,
            "d": description,
            "w": details.get("Website", ""),
            "f": features,
            "p": "Subscription-based model",
            "fd": funding_info,
            "funding_amount": funding_amount,
            "ad": {
                "type": details.get("Primary Industry", ""),
                "employees": details.get("Employees", ""),
                "location": details.get("Address", [""])[0] if isinstance(details.get("Address"), list) else "",
                "investors": investors[:2] if investors else [],
                "status": details.get("Status", ""),
                "deal_amount": details.get("Latest Deal Amount", "")
            }
        }
        competitors_info.append(comp_info)
    
    system_message = {
        "role": "system",
        "content": """You are a JSON generator. Your ONLY task is to return a valid JSON object.
        The output MUST be a single, valid JSON object that can be parsed by json.loads().
        The output MUST start with { and end with }.
        The output MUST NOT contain any text, explanations, markdown, or code blocks.
        The output MUST NOT contain any newlines or extra spaces.
        The output MUST be proper JSON format with all strings in double quotes.
        You MUST use the actual company names and data provided in the input.
        You MUST follow the exact JSON structure provided.
        You MUST give a feature score for each competitor companies that match with the startup features. 
        Make sure to give a score between 0-10. Also give the score only if the competitor company features match with the startup features.
        One and Only if many of the features doesn't match with the startup features then give feature score as 0 else provide the score.
        Provide the feature score around 1-3 if their idealogy matches and only few features matches it.
        Provide the feature score around 4-6 if their idealogy matches and many features matches it.
        Provide the feature score around 7-10 if their idealogy matches and all features matches it.
        The feature score should be different for each competitor company.
        You MUST NOT return any text before or after the JSON object.
        You MUST include all the competitors with the feature score greater than 0 in the competitors array.
        Give a valuation score 0-100 for each competitor company based on their details, features and popularity."""
    }

    # User message with the data and format
    user_message = {
        "role": "user",
        "content": f"""Return ONLY a valid JSON object with this EXACT structure, using the actual data provided:

{{
  "competitors": [
    {{
      "name": "company_name",
      "description": "detailed_description",
      "website": "company_website",
      "features": ["feature1", "feature2"],
      "pricing": "pricing_details",
      "funding": "funding_amount",
      "feature_score": "0-10",  
      "valuation_score": "0-100",
      "details": {{
        "type": "company_type",
        "employees": "employee_count",
        "location": "company_location",
        "investors": ["investor1", "investor2", "investor3"],
        "status": "company_status",
        "deal_type": "latest_deal_type",
        "deal_amount": "latest_deal_amount"
      }}
    }}
  ],
  "market_analysis": {{
    "total_market_size": "market_size_value",
    "growth_rate": "growth_rate_value",
    "key_trends": ["trend1", "trend2"]
  }},
  "collaboration_opportunities": ["opportunity1", "opportunity2"]
}}

Data to analyze:
Startup: {json.dumps(startup_info)}
Competitors: {json.dumps(competitors_info)}

IMPORTANT:
1. Return ONLY the JSON object, nothing else
2. Use the exact structure shown above
3. Replace all placeholder values with actual data
4. Ensure all strings are in double quotes
5. Do not add any comments or explanations
6. Do not include any markdown formatting
7. The output must be valid JSON that can be parsed by json.loads().
8. Include all the competitors with the feature score greater than 0 in the competitors array.
10. Sort competitors by funding amount in descending order
11. Do not include any empty strings or null values
12. All fields must contain actual data from the input
13. Include complete company details including investors and deal information
14. Add market analysis information
16. Keep descriptions and features concise to stay within token limits
17. Make sure to give a feature score between 0-10 for each competitor company based on the similarity of the features. 
18. Make sure to give a valution score between 0-100 for each competitor company based all the details provided.
19. One and Only if many of the features doesn't match with the startup features then give feature score as 0 else provide the score.
20. Provide the feature score around 1-3 if their idealogy matches and only few features matches it.
21. Provide the feature score around 4-6 if their idealogy matches and many features matches it.
22. Provide the feature score around 7-10 if their idealogy matches and all features matches it."""
    }
    return [system_message, user_message]

def is_valid_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False

def analyze_with_llm(messages: List[Dict], max_retries: int = 2) -> str:
    # Convert messages to LangChain format
    lc_messages = []
    for msg in messages:
        if msg["role"] == "system":
            lc_messages.append(SystemMessage(content=msg["content"]))
        elif msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
    
    # Try each API key in rotation
    for key_index in range(len(TOGETHER_API_KEYS)):
        api_key = TOGETHER_API_KEYS[key_index % len(TOGETHER_API_KEYS)]
        if not api_key:  # Skip None/empty keys
            continue
            
        llm = ChatTogether(
            together_api_key=api_key,
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            max_tokens=5000,  # Increased token limit
            top_p=0.9
        )
        
        for attempt in range(max_retries):
            try:
                response = llm.invoke(lc_messages)
                result = response.content.strip()
                result = result.replace("```json", "").replace("```", "").strip()
                result = result.replace("\n", "").replace("  ", " ")
                if not result.startswith("{"):
                    result = "{" + result
                if not result.endswith("}"):
                    result = result + "}"
                if is_valid_json(result):
                    return result
            except Exception as e:
                # Check for rate limit error (429 or model_rate_limit)
                if ("429" in str(e)) or ("rate limit" in str(e).lower()) or ("model_rate_limit" in str(e)):
                    print(f"Rate limit hit for key {key_index + 1}, trying next key...")
                    break  # Try next key
                print(f"Attempt {attempt + 1} failed with key {key_index + 1}: {e}")
                if attempt == max_retries - 1:
                    break  # Move to next key after max retries
    
    print("All API keys exhausted or failed")
    return "{}"

def save_analysis_result(result: str, filename: str = 'competitor_analysis_result.json'):
    try:
        result = result.strip()
        if not result.startswith("{"):
            result = "{" + result
        if not result.endswith("}"):
            result = result + "}"
        data = json.loads(result)
        required_fields = ["competitors", "market_analysis", "collaboration_opportunities"]
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field: {field}")
                return
            if not data[field]:
                print(f"❌ Empty field: {field}")
                return
        
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:  # Changed from 'a' to 'w' to overwrite
            json.dump(data, f, indent=2)
        print(f"✅ Analysis saved to {filepath}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON output from the model: {str(e)}")
    except Exception as e:
        print(f"❌ Error saving analysis: {e}")

async def main2(output_data, startup_data=None):
    # Enhanced parameter handling
    if startup_data is None:
        # Fallback to loading from file only if not provided
        startup_data = load_json_files()
        if not startup_data:
            print("❌ No startup data provided and failed to load from file")
            return
    
    if not startup_data or not output_data:
        print("❌ Failed to load required data")
        return
    
    try:
        messages = prepare_optimized_prompt(startup_data, output_data)
        result = analyze_with_llm(messages)
        if result and result != "{}":
            save_analysis_result(result)
        else:
            print("❌ Failed to generate valid JSON analysis")
    except AttributeError as e:
        if "'NoneType' object has no attribute 'get'" in str(e):
            print(f"⚠️ Skipping this company due to AttributeError: {e}")
            return  # Skip this company and continue
        else:
            print(f"❌ Unexpected AttributeError: {e}")
            return
    except Exception as e:
        print(f"⚠️ Skipping this company due to unexpected error: {e}")
        return