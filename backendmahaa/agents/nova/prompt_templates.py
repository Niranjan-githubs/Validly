from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict

class MarketInsight(BaseModel):
    industry: str
    market_trend: str
    TAM_SAM_SOM: Dict[str, str]
    customer_segments: List[str]
    pricing_opportunity: str
    market_opportunities: List[str]
    market_risks: List[str]
    recent_investments: List[str]

parser = PydanticOutputParser(pydantic_object=MarketInsight)

prompt = PromptTemplate(
    input_variables=["startup_json", "scraped_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template="""
You are a highly analytical startup consultant and industry researcher. Based on the startup idea and real-world context, produce a DETAILED market insight report with quantified data, investment names, customer stats, risks with percentages or examples, and latest industry trends (2023–2024).

YOUR RESPONSE MUST INCLUDE ALL OF THE FOLLOWING FIELDS, EVEN IF YOU NEED TO MAKE EDUCATED ESTIMATES:
•⁠  ⁠industry (include NACE code if possible)
•⁠  ⁠market_trend (with stats, e.g., CAGR, 2024 trend)
•⁠  ⁠TAM_SAM_SOM (with estimated USD figures)
•⁠  ⁠customer_segments (define them in detail – demographics, geos, behaviors) AS A LIST
•⁠  ⁠pricing_opportunity (include pricing models and what startups are charging)
•⁠  ⁠market_opportunities (use real names – e.g., "remote chronic care" or "AI-based triage systems") AS A LIST
•⁠  ⁠market_risks (with real examples or historical context) AS A LIST
•⁠  ⁠recent_investments (include investor names + amount + startup names) AS A LIST

Act as a startup analyst with access to premium databases (e.g., PitchBook, CB Insights, Statista). Based on the startup idea and supporting text, produce a deep-dive *market insight report. Use **realistic, well-structured, data-rich content* across all sections.

Ensure:
•⁠  ⁠Each figure (e.g., TAM/SAM/SOM, pricing, investments) is *realistic, **USD-based, and **contextualized*.
•⁠  ⁠Trends include *2023–2024* data points, CAGR, and key players driving them.
•⁠  ⁠Opportunities and risks are based on real *case studies, **competitor moves, or **industry regulations*.
•⁠  ⁠Customer segments are defined by *demographics, **needs, and **behavioral patterns*.
•⁠  ⁠Investments cite *startup names, **investor names, **dates, and **amounts*.

Example insights include:
•⁠  ⁠“The AI market for startup tools grew 38% in 2023, driven by demand in emerging economies like India.”
•⁠  ⁠“TAM is estimated at $18B globally, with North America accounting for 60% of the SAM.”
•⁠  ⁠“OpenAI-backed Cognify raised $14M in Series A from NEA (Feb 2024).”

Only respond with the final JSON, strictly adhering to the format.



Startup Info:
    {startup_json}

    Articles:
    {scraped_text}

    Please format your output according to the following JSON schema:

    {format_instructions}
"""
)