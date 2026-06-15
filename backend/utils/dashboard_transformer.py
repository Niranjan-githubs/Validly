# FounderScan/backend/utils/dashboard_transformer.py

def transform_dashboard_data(raw_data):
    """
    Transforms raw analysis JSON from Firebase into a dashboard-friendly, rich format.
    """
    competitor_analysis = raw_data.get("competitor_analysis", {})
    market_research = raw_data.get("market_research", {})
    recommendations = raw_data.get("recommendations", {})
    startup_summary = raw_data.get("startup_summary", {})
    user_pain_points = raw_data.get("user_pain_points", [])
    #market_insights = raw_data.get("market_insights", {})
    investor_landscape = raw_data.get("investor_landscape", {})
    venture_capitalists = investor_landscape.get("venture_capitalist", [])
    angel_investors = investor_landscape.get("angel_investors", [])

    # Transform competitors with rich details
    competitors = []
    for c in competitor_analysis.get("competitors", []):
        details = c.get("details") or {}
        competitors.append({
            "name": c.get("company_name"),
            "url": c.get("searched_url"),
            "description": details.get("Description") or details.get("description"),
            "industries": details.get("Industries") or details.get("Primary Industry") or details.get("Primary industry"),
            "verticals": details.get("Verticals") or details.get("Vertical(s)"),
            "employees": details.get("Employees") or details.get("What is the size of " + c.get("company_name", "")),
            "headquarters": details.get("Where is " + c.get("company_name", "") + " headquartered?"),
            "website": details.get("Website"),
            "social_media": details.get("Social Media"),
            "funding": details.get("How much funding has " + c.get("company_name", "") + " raised over time?"),
            "revenue": details.get("What is " + c.get("company_name", "") + "’s current revenue?"),
            "status": details.get("Status"),
            "ownership_status": details.get("Ownership Status"),
            "year_founded": details.get("Year Founded") or details.get("When was " + c.get("company_name", "") + " founded?"),
            # Add more fields as needed
        })

    

    # Transform user pain points
    pain_points = [
        {
            "title": p.get("submission_title"),
            "comment": p.get("comment"),
            "author": p.get("author"),
            "score": p.get("score"),
            "url": p.get("url"),
            "relevance_score": p.get("relevance_score"),
            "subreddit": p.get("subreddit"),
            "pain_indicators": p.get("pain_indicators"),
        }
        for p in user_pain_points
    ]

    # Transform startup summary Q&A
    
    """conversation = [
        {"role": entry.get("role"), "content": entry.get("content")}
        for entry in startup_summary.get("conversation", [])
    ]"""

    return {
        "market_analysis": {
            "industry": market_research.get("industry"),
            "market_trend": market_research.get("market_trend"),
            "pricing_opportunity": market_research.get("pricing_opportunity"),
            "TAM": market_research.get("TAM_SAM_SOM", {}).get("TAM"),
            "SAM": market_research.get("TAM_SAM_SOM", {}).get("SAM"),
            "SOM": market_research.get("TAM_SAM_SOM", {}).get("SOM"),
            "customer_segments": market_research.get("customer_segments"),
            "market_opportunity": market_research.get("market_opportunity"),
            "market_risks": market_research.get("market_risks"),
            "recent_investments": market_research.get("recent_investments"),

        },
        "venture_capitalists": venture_capitalists,
        "angel_investors": angel_investors,
        "recommendations": [step["action"] for step in recommendations.get("next_steps", [])],
        "risks": market_research.get("market_risks"),
        "summary_title": startup_summary.get("title"),
        "summary_description": startup_summary.get("description"),
        #"startup_conversation": conversation,
        "user_pain_points": pain_points,
        "competitor_count": competitor_analysis.get("competitor_count"),
        "competitors": competitors,
        # Add more fields as needed (e.g., market_insights, etc.)
    }