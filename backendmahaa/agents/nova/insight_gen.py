from langchain_together import Together
from langchain.chains import LLMChain
from langchain_core.exceptions import OutputParserException
import json
import re
import os

from .prompt_templates import prompt, parser, MarketInsight
from .query_generator import generate_queries
from .web_scrape import extract_all_articles
from .web_search import run_web_search_agent
from .defaults import create_default_market_insight
from dataclasses import asdict

import os
from dotenv import load_dotenv

load_dotenv()

def build_market_insight_chain():
    from langchain.output_parsers import ResponseSchema
    from langchain.output_parsers import StructuredOutputParser

    response_schemas = [
        ResponseSchema(name="industry", description="Industry category with NACE code if possible"),
        ResponseSchema(name="market_trend", description="Market trend with stats, e.g., CAGR"),
        ResponseSchema(name="TAM_SAM_SOM", description="Dict with TAM, SAM, SOM values in USD"),
        ResponseSchema(name="customer_segments", description="List of customer segments with details"),
        ResponseSchema(name="pricing_opportunity", description="Pricing models and strategies"),
        ResponseSchema(name="market_opportunities", description="List of market opportunities"),
        ResponseSchema(name="market_risks", description="List of market risks with examples"),
        ResponseSchema(name="recent_investments", description="List of recent investments with details")
    ]

    structured_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = structured_parser.get_format_instructions()

    llm = Together(
        model="meta-llama/Llama-Vision-Free",
        temperature=0.2,
        max_tokens=4000,
        api_key = os.getenv("TOGETHER_API_KEY")  
    )

    chain = prompt | llm | parser
    return chain

def get_market_insights(chain, inputs, max_retries=3):
    """
    Attempt to get market insights with retry logic and fallback mechanisms.
    
    Args:
        chain: The LangChain chain
        inputs: Input dictionary for the chain (must contain startup_json, scraped_text, format_instructions)
        max_retries: Maximum number of retry attempts
    
    Returns:
        A valid MarketInsight object
    """
    # Validate inputs
    if not isinstance(inputs, dict):
        print("❌ Invalid inputs provided to get_market_insights")
        default_data = create_default_market_insight()
        return {"text": MarketInsight(**default_data)}
    
    # Ensure required keys exist
    inputs.setdefault("startup_json", "{}")
    inputs.setdefault("scraped_text", "")
    inputs.setdefault("format_instructions", parser.get_format_instructions())
    
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

    # Fallback (should never reach here, but just in case)
    default_data = create_default_market_insight()
    return {"text": MarketInsight(**default_data)}