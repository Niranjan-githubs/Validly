import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_together import ChatTogether
from langchain_text_splitters import RecursiveCharacterTextSplitter
from collections import defaultdict
import concurrent.futures
from typing import Any

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../outputs')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def create_risk_agent():
    """
    Initializes and returns a LangChain agent for startup risk analysis.
    """
    # The user mentioned "meta llama 3.3 turbo free", but that's not a standard name.
    # We'll use a standard Llama 3 model from Together AI's free tier.
    llm = ChatTogether(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        temperature=0.1,
    )

    # Updated prompt template to clarify context usage
    prompt_template = """
    You are a startup risk analysis agent. Your task is to generate a comprehensive risk analysis for the STARTUP IDEA described below.

    Use the COMPETITOR LANDSCAPE and MARKET INSIGHTS only as context to inform your analysis of the startup idea. Do NOT generate risks for competitors or the market in isolation. All risks should be for the startup idea, considering the competitive and market environment.

    STARTUP IDEA:
    ---
    {startup_analysis}
    ---
    COMPETITOR LANDSCAPE (context only):
    ---
    {competitor_landscape}
    ---
    MARKET INSIGHTS (context only):
    ---
    {market_insights}
    ---

    Generate a list of key risks categorized into:
    - Data Risk
    - Market Risk
    - Regulatory Risk
    - Financial Risk
    - Tech Risk
    - Operational Risk

    For each identified risk, provide the following details in a clean JSON format. The final output should be a single JSON object with a "risk_matrix" key, containing a list of risk objects.

    - risk_name: A concise name for the risk.
    - type: The category of the risk.
    - probability: A score from 1 (very unlikely) to 5 (very likely).
    - impact: A score from 1 (very low) to 5 (very high).
    - score: The product of Probability x Impact.
    - notes: A brief explanation of the context and why it's a risk, citing details from the startup info.

    {format_instructions}
    """

    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_template(
        template=prompt_template,
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Create the chain
    chain = prompt | llm | parser
    return chain

def split_startup_info(startup_info, chunk_size=2000, chunk_overlap=200):
    """
    Splits the startup_info JSON into manageable text chunks using LangChain's text splitter.
    """
    text = json.dumps(startup_info, indent=2)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

# Summarize context sections if too large
def summarize_section(section: Any, max_length=2000):
    text = json.dumps(section, indent=2)
    if len(text) > max_length:
        # Truncate and indicate truncation
        return text[:max_length] + "\n... [truncated] ..."
    return text

def analyze_risks(startup_info_path: str):
    """
    Loads startup info, runs the risk analysis agent, and prints the results.
    """
    # Load the environment variables from .env file
    load_dotenv()

    # Check for the API key
    if not os.getenv("TOGETHER_API_KEY2"):
        raise ValueError(
            "TOGETHER_API_KEY not found in environment variables. "
            "Please create a .env file and add your key."
        )

    # Load the startup analysis data
    try:
        with open(startup_info_path, 'r', encoding='utf-8') as f:
            full_info = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{startup_info_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file '{startup_info_path}'.")
        return

    # Extract relevant sections
    startup_analysis = full_info.get("startup_analysis", {})
    competitor_landscape = full_info.get("competitor_landscape", {})
    market_insights = full_info.get("market_insights", {})

    # Summarize context sections if too large
    competitor_landscape_str = summarize_section(competitor_landscape)
    market_insights_str = summarize_section(market_insights)
    startup_analysis_str = summarize_section(startup_analysis, max_length=4000)

    # Use only the relevant_info as input for the risk agent
    risk_agent_chain = create_risk_agent()
    print("🤖 Risk agent is analyzing the startup info...")

    response = risk_agent_chain.invoke({
        "startup_analysis": startup_analysis_str,
        "competitor_landscape": competitor_landscape_str,
        "market_insights": market_insights_str
    })

    # --- Deduplicate, merge, and group risks ---
    def normalize_key(risk):
        return (risk["risk_name"].strip().lower(), risk["type"].strip().lower())

    deduped = {}
    all_risks = response["risk_matrix"] if "risk_matrix" in response else []
    for risk in all_risks:
        key = normalize_key(risk)
        if key not in deduped:
            deduped[key] = risk.copy()
        else:
            existing = deduped[key]
            existing["notes"] += "\n" + risk["notes"]
            existing["probability"] = max(existing["probability"], risk["probability"])
            existing["impact"] = max(existing["impact"], risk["impact"])
            existing["score"] = max(existing["score"], risk["score"])

    from collections import defaultdict
    grouped = defaultdict(list)
    for risk in deduped.values():
        grouped[risk["type"]].append(risk)
    for risk_type in grouped:
        grouped[risk_type].sort(key=lambda r: r["score"], reverse=True)
    all_merged_risks = list(deduped.values())
    final_result = {
        "risk_matrix": all_merged_risks
    }
    print("\n--- Risk Analysis Complete ---")
    print(json.dumps(final_result, indent=2))
    print("----------------------------\n")

    # Save risk_analysis.json in outputs directory
    risk_json_path = os.path.join(OUTPUT_DIR, 'risk_analysis.json')
    with open(risk_json_path, 'w', encoding='utf-8') as f:
        json.dump({"risk_matrix": all_risks}, f, indent=2, ensure_ascii=False)
    print(f"✅ Risk analysis saved to {risk_json_path}")


if __name__ == "__main__":
    # The complete_analysis.json file is in the 'outputs' directory in the parent folder.
    # We construct the path relative to this script's location.
    script_dir = os.path.dirname(__file__)
    analysis_file_path = os.path.join(script_dir, '..', 'outputs', 'complete_analysis.json')
    analyze_risks(analysis_file_path) 