import json
from functools import lru_cache
import concurrent.futures
from typing import List, Dict

def load_json_objects(filename: str) -> List[dict]:
    """Load a file containing concatenated JSON objects and return a list of dicts."""
    objects = []
    with open(filename, 'r') as f:
        buffer = ''
        for line in f:
            buffer += line.strip()
            # Try to decode a JSON object from the buffer
            try:
                while buffer:
                    obj, idx = json.JSONDecoder().raw_decode(buffer)
                    objects.append(obj)
                    buffer = buffer[idx:].lstrip()
            except json.JSONDecodeError:
                continue  # Need more lines to complete the object
    return objects

def process_competitor(company: dict, valuation_scores: dict) -> dict:
    """Process a single competitor's data."""
    # Ensure 'company_name' exists before proceeding
    if 'company_name' in company and company['company_name'] in valuation_scores:
        company['valuation_score'] = valuation_scores[company['company_name']]
        return company
    return None

def final():
    """Process and combine competitor analysis results efficiently."""
    # Load and flatten all competitors from concatenated JSON objects
    competitor_analysis_objs = load_json_objects('competitor_analysis_result.json')
    print(f"DEBUG: competitor_analysis_objs loaded: {len(competitor_analysis_objs)} objects")
    
    all_competitors = []
    for obj in competitor_analysis_objs:
        try:
            if 'competitors' in obj:
                all_competitors.extend(obj['competitors'])
        except Exception as e:
            print(f"⚠️ Skipping competitor object due to error: {e}")
            continue
    print(f"DEBUG: all_competitors (flattened): {len(all_competitors)} entries")

    # Create valuation scores mapping (use 0 if not present) - Enhanced with error handling
    valuation_scores = {}
    for comp in all_competitors:
        try:
            valuation_scores[comp['name']] = comp.get('valuation_score', 0)
        except Exception as e:
            print(f"⚠️ Skipping valuation score for a competitor due to error: {e}")
            continue
    print(f"DEBUG: valuation_scores created: {len(valuation_scores)} entries")

    print("phase 1")

    # Sort results by valuation score - Enhanced with error handling
    try:
        all_competitors.sort(key=lambda x: float(x.get('valuation_score', 0) or 0), reverse=True)
    except Exception as e:
        print(f"⚠️ Skipping sorting by valuation score due to error: {e}")

    # Filter companies with feature_score > 0 - Enhanced with error handling
    filtered_results = []
    for company in all_competitors:
        try:
            if float(company.get('feature_score', 0) or 0) > 0:
                filtered_results.append(company)
        except Exception as e:
            print(f"⚠️ Skipping company in filter due to error: {e}")
            continue
    print(f"DEBUG: filtered_results after feature_score > 0 filter: {len(filtered_results)} entries")

    # Sort results by feature_score in descending order - Enhanced with error handling
    try:
        filtered_results.sort(key=lambda x: float(x.get('feature_score', 0) or 0), reverse=True)
    except Exception as e:
        print(f"⚠️ Skipping sorting filtered results by feature score due to error: {e}")
    
    copy_matching_companies()

def is_details_nonempty(details):
    if not isinstance(details, dict):
        return False
    # Exclude if only Social Media, Industries, Verticals are present and all are empty
    allowed_empty_keys = {"Social Media", "Industries", "Verticals"}
    nonempty_found = False
    for k, v in details.items():
        if k in allowed_empty_keys:
            # Check if these are empty
            if isinstance(v, dict) and v:
                nonempty_found = True
            elif isinstance(v, list) and v:
                nonempty_found = True
            elif isinstance(v, str) and v.strip():
                nonempty_found = True
            elif v not in (None, '', [], {}):
                nonempty_found = True
        else:
            # For any other key, if non-empty, return True
            if isinstance(v, dict) and v:
                return True
            if isinstance(v, list) and v:
                return True
            if isinstance(v, str) and v.strip():
                return True
            if v not in (None, '', [], {}):
                return True
    # If only allowed_empty_keys are present and all are empty, return False
    if not nonempty_found:
        return False
    return True

def copy_matching_companies():
    """Copy details of companies from final_output.json to final_result.json if their company_name matches any competitor name in competitor_analysis_result.json with feature_score > 0, and only if details are not all empty."""
    # Load competitor names with feature_score > 0 - Enhanced with error handling
    competitor_analysis_objs = load_json_objects('competitor_analysis_result.json')
    competitor_names = set()
    for obj in competitor_analysis_objs:
        if 'competitors' in obj:
            for comp in obj['competitors']:
                try:
                    if float(comp.get('feature_score', 0) or 0) > 0:
                        competitor_names.add(comp['name'])
                except Exception as e:
                    print(f"⚠️ Skipping competitor name due to error: {e}")
                    continue

    # Load all companies
    try:
        with open('final_output.json', 'r') as f:
            all_companies = json.load(f)
    except FileNotFoundError:
        print("❌ final_output.json not found")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing final_output.json: {e}")
        return

    # Filter companies whose company_name matches any competitor name and details are not all empty - Enhanced with error handling
    matching_companies = []
    for company in all_companies:
        try:
            if company.get('company_name') in competitor_names and is_details_nonempty(company.get('details', {})):
                matching_companies.append(company)
        except Exception as e:
            print(f"⚠️ Skipping company in matching due to error: {e}")
            continue

    # Write the matching companies to final_result.json - Enhanced with error handling
    try:
        with open('final_result.json', 'w') as f:
            print("Got the results")
            json.dump(matching_companies, f, indent=2)
        print(f"✅ Successfully wrote {len(matching_companies)} matching companies to final_result.json")
    except Exception as e:
        print(f"❌ Error writing final_result.json: {e}")

# Additional utility function for better error handling
def validate_json_structure(data, required_fields):
    """Validate that the JSON data has the required structure."""
    if not isinstance(data, dict):
        return False
    for field in required_fields:
        if field not in data:
            return False
    return True

# Enhanced function to handle file operations safely
def safe_load_json(filename: str) -> dict:
    """Safely load a JSON file with comprehensive error handling."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {filename}: {e}")
        return {}
    except Exception as e:
        print(f"❌ Unexpected error loading {filename}: {e}")
        return {}

def safe_save_json(data, filename: str) -> bool:
    """Safely save data to a JSON file with comprehensive error handling."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving {filename}: {e}")
        return False