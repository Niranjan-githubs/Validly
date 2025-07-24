import os
import json
from typing import Dict, List, Any, Optional
import asyncio
from collections import defaultdict

# LangChain imports
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_together import ChatTogether
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    print("⚠️ LangChain not installed. Install with: pip install langchain langchain-together")
    ChatPromptTemplate = None
    JsonOutputParser = None
    ChatTogether = None
    RecursiveCharacterTextSplitter = None

class CloudRiskAgent:
    """Cloud-ready risk analysis agent with no local file dependencies"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.session_data = {}  # In-memory storage
        
    def create_risk_agent(self):
        """Initialize and return a LangChain agent for startup risk analysis"""
        if not ChatTogether:
            raise ImportError("LangChain dependencies not available")
            
        # Get API key from environment
        api_key = os.getenv("TOGETHER_API_KEY") or os.getenv("TOGETHER_API_KEY2")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment variables")
        
        # Initialize LLM
        llm = ChatTogether(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            temperature=0.1,
            together_api_key=api_key
        )

        # Enhanced prompt template for comprehensive risk analysis
        prompt_template = """
        You are an expert startup risk analysis consultant. Your task is to generate a comprehensive risk analysis for the STARTUP IDEA described below.

        Use the COMPETITOR LANDSCAPE and MARKET INSIGHTS as context to inform your analysis of the startup idea. Focus on risks specific to this startup, considering the competitive and market environment.

        STARTUP IDEA:
        ---
        {startup_analysis}
        ---
        
        COMPETITOR LANDSCAPE (context):
        ---
        {competitor_landscape}
        ---
        
        MARKET INSIGHTS (context):
        ---
        {market_insights}
        ---

        Generate a comprehensive list of key risks categorized into these categories:
        - Market Risk: Competition, market size, demand validation, market timing
        - Financial Risk: Funding, revenue model, cash flow, pricing strategy
        - Technical Risk: Technology feasibility, scalability, security, infrastructure
        - Operational Risk: Team, execution, supply chain, partnerships
        - Regulatory Risk: Compliance, legal, IP protection, data privacy
        - Strategic Risk: Product-market fit, differentiation, customer acquisition

        For each identified risk, provide the following details in JSON format:

        - risk_name: A concise, specific name for the risk
        - type: The category of the risk (exactly one of the categories above)
        - probability: Score from 1 (very unlikely) to 5 (very likely)
        - impact: Score from 1 (very low impact) to 5 (very high impact)
        - score: The product of Probability × Impact (1-25)
        - description: Detailed explanation of the risk and its potential consequences
        - mitigation_strategies: List of 2-3 specific actions to mitigate this risk
        - indicators: Early warning signs that this risk is materializing

        Return the results as a JSON object with a "risk_matrix" key containing a list of risk objects.

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

    def summarize_section(self, section: Any, max_length: int = 2000) -> str:
        """Summarize context sections if too large"""
        if not section:
            return "No data available"
            
        text = json.dumps(section, indent=2) if isinstance(section, (dict, list)) else str(section)
        
        if len(text) > max_length:
            # Smart truncation - try to keep important parts
            if isinstance(section, dict):
                # For dicts, prioritize certain keys
                priority_keys = ['analysis', 'summary', 'description', 'insights', 'competitors', 'gaps']
                truncated = {}
                current_length = 0
                
                for key in priority_keys:
                    if key in section and current_length < max_length * 0.8:
                        value = section[key]
                        value_str = json.dumps(value, indent=2)
                        if current_length + len(value_str) < max_length * 0.8:
                            truncated[key] = value
                            current_length += len(value_str)
                
                # Add remaining keys if space allows
                for key, value in section.items():
                    if key not in truncated and current_length < max_length * 0.9:
                        value_str = json.dumps(value, indent=2)
                        if current_length + len(value_str) < max_length * 0.9:
                            truncated[key] = value
                            current_length += len(value_str)
                
                return json.dumps(truncated, indent=2) + "\n... [content truncated for length] ..."
            else:
                return text[:max_length] + "\n... [truncated] ..."
        
        return text

    def validate_and_enhance_risks(self, risks: List[Dict]) -> List[Dict]:
        """Validate and enhance risk data"""
        enhanced_risks = []
        
        for risk in risks:
            try:
                # Ensure required fields exist
                enhanced_risk = {
                    'risk_name': risk.get('risk_name', 'Unknown Risk'),
                    'type': risk.get('type', 'Strategic Risk'),
                    'probability': max(1, min(5, int(risk.get('probability', 3)))),
                    'impact': max(1, min(5, int(risk.get('impact', 3)))),
                    'description': risk.get('description', risk.get('notes', 'No description provided')),
                    'mitigation_strategies': risk.get('mitigation_strategies', ['Develop mitigation plan', 'Monitor regularly']),
                    'indicators': risk.get('indicators', ['Performance metrics decline', 'Market feedback negative'])
                }
                
                # Calculate score
                enhanced_risk['score'] = enhanced_risk['probability'] * enhanced_risk['impact']
                
                # Ensure mitigation_strategies and indicators are lists
                if isinstance(enhanced_risk['mitigation_strategies'], str):
                    enhanced_risk['mitigation_strategies'] = [enhanced_risk['mitigation_strategies']]
                if isinstance(enhanced_risk['indicators'], str):
                    enhanced_risk['indicators'] = [enhanced_risk['indicators']]
                
                enhanced_risks.append(enhanced_risk)
                
            except Exception as e:
                print(f"⚠️ Error processing risk: {e}")
                # Add a default risk if parsing fails
                enhanced_risks.append({
                    'risk_name': 'Risk Analysis Error',
                    'type': 'Technical Risk',
                    'probability': 2,
                    'impact': 2,
                    'score': 4,
                    'description': f'Error processing risk data: {str(e)}',
                    'mitigation_strategies': ['Review risk analysis process'],
                    'indicators': ['Analysis errors occur']
                })
        
        return enhanced_risks

    def deduplicate_and_merge_risks(self, risks: List[Dict]) -> List[Dict]:
        """Deduplicate and merge similar risks"""
        def normalize_key(risk):
            return (risk["risk_name"].strip().lower(), risk["type"].strip().lower())

        deduped = {}
        
        for risk in risks:
            key = normalize_key(risk)
            if key not in deduped:
                deduped[key] = risk.copy()
            else:
                existing = deduped[key]
                # Merge descriptions
                if existing["description"] != risk["description"]:
                    existing["description"] += f"\n\nAdditional context: {risk['description']}"
                
                # Take higher probability and impact
                existing["probability"] = max(existing["probability"], risk["probability"])
                existing["impact"] = max(existing["impact"], risk["impact"])
                existing["score"] = existing["probability"] * existing["impact"]
                
                # Merge mitigation strategies
                existing_strategies = set(existing.get("mitigation_strategies", []))
                new_strategies = set(risk.get("mitigation_strategies", []))
                existing["mitigation_strategies"] = list(existing_strategies.union(new_strategies))[:5]  # Limit to 5
                
                # Merge indicators
                existing_indicators = set(existing.get("indicators", []))
                new_indicators = set(risk.get("indicators", []))
                existing["indicators"] = list(existing_indicators.union(new_indicators))[:5]  # Limit to 5

        return list(deduped.values())

    def categorize_and_prioritize_risks(self, risks: List[Dict]) -> Dict[str, Any]:
        """Categorize risks by type and create priority matrix"""
        # Group by risk type
        grouped_risks = defaultdict(list)
        for risk in risks:
            grouped_risks[risk["type"]].append(risk)
        
        # Sort each category by score (highest first)
        for risk_type in grouped_risks:
            grouped_risks[risk_type].sort(key=lambda r: r["score"], reverse=True)
        
        # Create priority matrix
        high_priority = [r for r in risks if r["score"] >= 15]  # Score 15-25
        medium_priority = [r for r in risks if 8 <= r["score"] < 15]  # Score 8-14
        low_priority = [r for r in risks if r["score"] < 8]  # Score 1-7
        
        # Calculate overall risk profile
        total_risks = len(risks)
        avg_score = sum(r["score"] for r in risks) / max(total_risks, 1)
        
        risk_profile = "Low"
        if avg_score >= 15:
            risk_profile = "High"
        elif avg_score >= 10:
            risk_profile = "Medium"
        
        return {
            "risk_matrix": risks,
            "risks_by_category": dict(grouped_risks),
            "priority_matrix": {
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority
            },
            "risk_summary": {
                "total_risks": total_risks,
                "average_risk_score": round(avg_score, 2),
                "risk_profile": risk_profile,
                "high_priority_count": len(high_priority),
                "critical_areas": [category for category, risks_list in grouped_risks.items() 
                                if any(r["score"] >= 15 for r in risks_list)]
            }
        }

    async def analyze_startup_risks(self, startup_data: Dict, competitor_data: Dict = None, market_data: Dict = None) -> Dict[str, Any]:
        """Main function to analyze startup risks"""
        print("⚠️ Starting comprehensive risk analysis...")
        
        if not startup_data:
            print("❌ No startup data provided for risk analysis")
            return self.create_default_risk_analysis()
        
        try:
            # Create risk analysis agent
            risk_agent_chain = self.create_risk_agent()
            print("🤖 Risk agent initialized successfully")
            
            # Prepare context data
            startup_analysis_str = self.summarize_section(startup_data, max_length=4000)
            competitor_landscape_str = self.summarize_section(competitor_data or {}, max_length=2000)
            market_insights_str = self.summarize_section(market_data or {}, max_length=2000)
            
            print("📊 Analyzing risks with AI agent...")
            
            # Get risk analysis from LLM
            response = risk_agent_chain.invoke({
                "startup_analysis": startup_analysis_str,
                "competitor_landscape": competitor_landscape_str,
                "market_insights": market_insights_str
            })
            
            # Extract and validate risks
            raw_risks = response.get("risk_matrix", []) if isinstance(response, dict) else []
            if not raw_risks:
                print("⚠️ No risks returned from AI agent, using fallback analysis")
                return self.create_fallback_risk_analysis(startup_data)
            
            # Enhance and validate risk data
            enhanced_risks = self.validate_and_enhance_risks(raw_risks)
            
            # Deduplicate and merge similar risks
            deduplicated_risks = self.deduplicate_and_merge_risks(enhanced_risks)
            
            # Categorize and prioritize
            final_analysis = self.categorize_and_prioritize_risks(deduplicated_risks)
            
            print(f"✅ Risk analysis complete - identified {len(deduplicated_risks)} unique risks")
            print(f"📈 Risk profile: {final_analysis['risk_summary']['risk_profile']}")
            print(f"🚨 High priority risks: {final_analysis['risk_summary']['high_priority_count']}")
            
            return final_analysis
            
        except Exception as e:
            print(f"❌ Error in risk analysis: {e}")
            print("🔄 Falling back to basic risk analysis")
            return self.create_fallback_risk_analysis(startup_data)

    def create_default_risk_analysis(self) -> Dict[str, Any]:
        """Create default risk analysis when no data is available"""
        default_risks = [
            {
                "risk_name": "Market Validation Risk",
                "type": "Market Risk",
                "probability": 4,
                "impact": 4,
                "score": 16,
                "description": "Lack of sufficient market validation for the product concept",
                "mitigation_strategies": ["Conduct customer interviews", "Build MVP for testing", "Validate pricing model"],
                "indicators": ["Low user engagement", "Poor conversion rates", "Negative feedback"]
            },
            {
                "risk_name": "Competitive Pressure",
                "type": "Market Risk", 
                "probability": 3,
                "impact": 3,
                "score": 9,
                "description": "Existing or emerging competitors may capture market share",
                "mitigation_strategies": ["Develop unique value proposition", "Build strong brand", "Focus on customer retention"],
                "indicators": ["Competitor launches", "Market share decline", "Price pressure"]
            },
            {
                "risk_name": "Technical Execution Risk",
                "type": "Technical Risk",
                "probability": 3,
                "impact": 4,
                "score": 12,
                "description": "Challenges in building and scaling the technical solution",
                "mitigation_strategies": ["Hire experienced developers", "Use proven technologies", "Plan for scalability"],
                "indicators": ["Development delays", "Technical debt", "Performance issues"]
            }
        ]
        
        return self.categorize_and_prioritize_risks(default_risks)

    def create_fallback_risk_analysis(self, startup_data: Dict) -> Dict[str, Any]:
        """Create basic risk analysis based on startup data"""
        risks = []
        
        # Analyze startup data for common risk patterns
        title = startup_data.get('title', '').lower()
        description = startup_data.get('description', '').lower()
        business_model = startup_data.get('business_model', '').lower()
        
        # Market risks
        if 'new' in title or 'innovative' in description:
            risks.append({
                "risk_name": "Market Education Risk",
                "type": "Market Risk",
                "probability": 4,
                "impact": 3,
                "score": 12,
                "description": "Market may need significant education about the new solution",
                "mitigation_strategies": ["Invest in market education", "Partner with industry leaders", "Create compelling content"],
                "indicators": ["Slow adoption", "Customer confusion", "Long sales cycles"]
            })
        
        # Technical risks
        if any(tech in description for tech in ['ai', 'ml', 'blockchain', 'ar', 'vr']):
            risks.append({
                "risk_name": "Technology Maturity Risk",
                "type": "Technical Risk",
                "probability": 3,
                "impact": 4,
                "score": 12,
                "description": "Dependency on emerging technologies that may not be fully mature",
                "mitigation_strategies": ["Have fallback technologies", "Invest in R&D", "Partner with tech providers"],
                "indicators": ["Technical limitations", "Integration issues", "Performance problems"]
            })
        
        # Financial risks
        if 'subscription' in business_model or 'saas' in business_model:
            risks.append({
                "risk_name": "Customer Churn Risk",
                "type": "Financial Risk",
                "probability": 3,
                "impact": 4,
                "score": 12,
                "description": "High customer churn could impact recurring revenue model",
                "mitigation_strategies": ["Focus on customer success", "Improve onboarding", "Monitor usage metrics"],
                "indicators": ["Rising churn rate", "Low engagement", "Support tickets increase"]
            })
        
        # Add default risks if none identified
        if not risks:
            return self.create_default_risk_analysis()
        
        return self.categorize_and_prioritize_risks(risks)

def run_risk_analysis(startup_data: Dict, competitor_data: Dict = None, market_data: Dict = None) -> Dict[str, Any]:
    """Synchronous wrapper for the async risk analysis"""
    risk_agent = CloudRiskAgent()
    return asyncio.run(risk_agent.analyze_startup_risks(startup_data, competitor_data, market_data))

# Backward compatibility function for pipeline integration
def analyze_risks_for_pipeline(startup_data: Dict, competitor_data: Dict = None, market_data: Dict = None) -> Dict[str, Any]:
    """Pipeline-ready risk analysis function"""
    return run_risk_analysis(startup_data, competitor_data, market_data)

if __name__ == "__main__":
    # Test with sample data
    sample_startup = {
        "title": "AI-powered project management tool",
        "description": "Uses machine learning to predict project risks and optimize resource allocation for remote teams",
        "business_model": "SaaS subscription with tiered pricing",
        "target_market": "Remote teams and project managers",
        "problem": "Project managers struggle to predict risks and allocate resources effectively in remote work environments"
    }
    
    sample_competitor = {
        "competitors": ["Asana", "Monday.com", "Jira"],
        "gaps": ["No AI-powered risk prediction", "Limited remote team features"],
        "analysis": "Competitive market with established players"
    }
    
    sample_market = {
        "market_size": 5000000000,
        "market_trend": "Growing demand for AI-powered productivity tools",
        "target_demographics": "Remote teams, project managers, tech companies"
    }
    
    results = run_risk_analysis(sample_startup, sample_competitor, sample_market)
    print(f"\n🎯 Risk Analysis Results:")
    print(f"Total Risks: {results['risk_summary']['total_risks']}")
    print(f"Risk Profile: {results['risk_summary']['risk_profile']}")
    print(f"High Priority Risks: {results['risk_summary']['high_priority_count']}")
    
    print(f"\n📊 Top 3 Risks:")
    top_risks = sorted(results['risk_matrix'], key=lambda x: x['score'], reverse=True)[:3]
    for i, risk in enumerate(top_risks, 1):
        print(f"{i}. {risk['risk_name']} (Score: {risk['score']}) - {risk['description'][:100]}...")