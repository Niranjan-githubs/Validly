import json
from insight_gen import build_market_insight_chain
from prompt_templates import prompt, parser
from dataclasses import asdict
import os 
from pathlib import Path 
from query_generator import generate_queries
from web_scrape import extract_all_articles
from web_search import run_web_search_agent

# Load input JSONs
with open("../agents/output/startup_summary.json", "r") as f:
    startup_json = json.load(f) 


queries = generate_queries(startup_json)
article_links = run_web_search_agent(queries)
article_data = extract_all_articles(article_links)

# Debugging: Check the structure of article_data
print("\n🔍 ARTICLE DATA STRUCTURE:")
for url, content in article_data.items():
    print(f"\nURL: {url}")
    print(f"Content type: {type(content)}")
    print(f"Content length: {len(str(content)) if content else 0}")
    break  # Just print the first entry for brevity


def summarize_article_data(article_data, max_chars_per_article=800):
    """
    Summarize article data while preserving key facts, numbers, and points.
    
    Args:
        article_data: Dictionary mapping URLs to content (which might be lists)
        max_chars_per_article: Maximum characters per article summary
    
    Returns:
        Dictionary with summarized content
    """
    import re
    summarized_data = {}
    
    for url, content_data in article_data.items():
        try:
            # Handle case where content is a list
            if isinstance(content_data, list):
                # Convert list items to strings and join them
                content_text = ""
                for item in content_data:
                    if isinstance(item, dict) and "extracted_text" in item:
                        # If it's a dict with extracted_text, use that
                        content_text += item.get("extracted_text", "") + "\n\n"
                    elif isinstance(item, str):
                        # If it's already a string, use it directly
                        content_text += item + "\n\n"
                    else:
                        # Otherwise, try to convert to string
                        content_text += str(item) + "\n\n"
            else:
                # If it's not a list, try to use it as is or convert to string
                content_text = str(content_data)
            
            # Skip if we ended up with no usable content
            if not content_text.strip():
                summarized_data[url] = "No usable content available"
                continue
                
            # Extract first sentence as title
            first_sentence = content_text.split('.')[0] + '.' if '.' in content_text else content_text[:100]
            
            # Extract numerical facts using regex
            numerical_facts = re.findall(r'\b\d+(?:\.\d+)?%?\s+[a-zA-Z\s]+', content_text)
            stats = ' '.join(numerical_facts[:10])  # Take first 10 stats
            
            # Get first and last paragraph for context
            paragraphs = content_text.split('\n\n')
            intro = paragraphs[0] if paragraphs else ""
            conclusion = paragraphs[-1] if len(paragraphs) > 1 else ""
            
            # Create summary with key components
            summary = f"{first_sentence}\n\nKEY STATS: {stats}\n\nINTRO: {intro[:300]}...\n\nCONCLUSION: {conclusion[:300]}..."
            
            # Ensure summary is within length limit
            if len(summary) > max_chars_per_article:
                summary = summary[:max_chars_per_article] + "..."
            
            summarized_data[url] = summary
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            summarized_data[url] = f"Error processing content: {str(e)[:100]}"
    
    return summarized_data

summarized_data = summarize_article_data(article_data, max_chars_per_article = 800)


print("\n🔍 ARTICLE DATA (Sample):")
for i, (url, content) in enumerate(article_data.items()):
    print(f"\n🔗 {url}\n📝 {content[:300]}...\n")
    if i >= 1:  # just print the first 2 entries
        break

print("FORMAT INSTRUCTIONS >>>", parser.get_format_instructions())



#with open("foundrscan/agents/nova_agent/data/scraped_text.json", "r") as f:
    #scraped_text = f.read()

# Run the chain
chain = build_market_insight_chain()
# Add this right after you define the chain but before you invoke it
import re
import json
from prompt_templates import MarketInsight
from langchain_core.exceptions import OutputParserException

def get_market_insights(chain, inputs, max_retries=3):
    """
    Attempt to get market insights with retry logic and fallback mechanisms.
    
    Args:
        chain: The LangChain chain
        inputs: Input dictionary for the chain
        max_retries: Maximum number of retry attempts
    
    Returns:
        A valid MarketInsight object
    """
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt+1} of {max_retries}")
            result = chain.invoke(inputs)
            # If we get here, the chain executed successfully
            return result
        except OutputParserException as e:
            print(f"Parsing error on attempt {attempt+1}: {e}")
            
            # Check if we have any JSON in the error message
            partial_json_match = re.search(r'completion\s+(\{.*?\})', str(e), re.DOTALL)
            
            if partial_json_match:
                try:
                    # Parse the partial JSON
                    partial_data = json.loads(partial_json_match.group(1))
                    
                    # Complete the data with default values
                    full_data = {
                        "industry": partial_data.get("industry", "Software"),
                        "market_trend": partial_data.get("market_trend", "Growing"),
                        "TAM_SAM_SOM": partial_data.get("TAM_SAM_SOM", {"TAM": "100M", "SAM": "50M", "SOM": "10M"}),
                        "customer_segments": partial_data.get("customer_segments", ["Enterprise customers", "SMBs", "Startups"]),
                        "pricing_opportunity": partial_data.get("pricing_opportunity", "SaaS subscription model"),
                        "market_opportunities": partial_data.get("market_opportunities", ["Market expansion", "Product innovation"]),
                        "market_risks": partial_data.get("market_risks", ["Competition", "Regulatory changes"]),
                        "recent_investments": partial_data.get("recent_investments", ["No recent investments data available"])
                    }
                    
                    # If this is the last attempt, return what we have
                    if attempt == max_retries - 1:
                        print("Using partial data with defaults")
                        return {"text": MarketInsight(**full_data)}
                except Exception as json_e:
                    print(f"Failed to process partial JSON: {json_e}")
                    # Continue to next attempt unless we're on the last one
                    if attempt == max_retries - 1:
                        # Create a completely default response as last resort
                        default_data = create_default_market_insight()
                        print("Created entirely default response")
                        return {"text": MarketInsight(**default_data)}
            else:
                # No JSON found in the error
                if attempt == max_retries - 1:
                    # Last attempt, create a default response
                    default_data = create_default_market_insight()
                    print("No JSON found in response, using default data")
                    return {"text": MarketInsight(**default_data)}
        except Exception as general_e:
            print(f"General error on attempt {attempt+1}: {general_e}")
            if attempt == max_retries - 1:
                # Last attempt, create a default response
                default_data = create_default_market_insight()
                print("General error occurred, using default data")
                return {"text": MarketInsight(**default_data)}

def create_default_market_insight():
    """Create a default MarketInsight data structure."""
    return {
        "industry": "Software",
        "market_trend": "Growing market with increasing demand",
        "TAM_SAM_SOM": {"TAM": "100M", "SAM": "50M", "SOM": "10M"},
        "customer_segments": ["Enterprise customers", "SMBs", "Startups"],
        "pricing_opportunity": "SaaS subscription model with tiered pricing",
        "market_opportunities": ["Market expansion", "Product innovation", "Integration opportunities"],
        "market_risks": ["Competition", "Regulatory changes", "Technology disruption"],
        "recent_investments": ["No specific investment data available"]
    }
# Use this function instead of calling chain.invoke directly
inputs = {
    "startup_json": json.dumps(startup_json, indent=2),
    "scraped_text": summarized_data,
    "format_instructions": parser.get_format_instructions()
}

result = get_market_insights(chain, inputs)

# Print to console
print("\n📊 Market Insights: --not printing fr now--")
#print(result)

# Save to file
output_path = "nova/data/market_insights.json"
with open(output_path, "w") as outfile:
    # Check if result contains a Pydantic model under 'text' key
    if isinstance(result, dict) and 'text' in result and hasattr(result['text'], 'model_dump'):
        # Pydantic v2
        result_dict = result['text'].model_dump()
    elif isinstance(result, dict) and 'text' in result and hasattr(result['text'], 'dict'):
        # Pydantic v1
        result_dict = result['text'].dict()
    elif hasattr(result, 'model_dump'):
        # Direct Pydantic v2 object
        result_dict = result.model_dump()
    elif hasattr(result, 'dict'):
        # Direct Pydantic v1 object
        result_dict = result.dict()
    else:
        # Try using asdict if it's a dataclass
        try:
            result_dict = asdict(result)
        except (TypeError, AttributeError):
            # Last resort - might still fail if contains non-serializable objects
            result_dict = result
        
    json.dump(result_dict, outfile, indent=2)

print(f"\n✅ Insights saved to {output_path}")
