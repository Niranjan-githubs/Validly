from typing import Dict, Any

def create_default_market_insight()-> Dict[str, Any]:
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