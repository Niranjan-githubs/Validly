import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import asyncio
import concurrent.futures
from functools import partial
import traceback

# Core imports
from .idea_extractor import IdeaExtractor

# Agent imports
from agents.idea_agent import StartupIdeaAnalyzer

# Competitor agent imports - Fixed import structure
from agents.competitor_agent.domain import competitor_agent

# Nova imports - Fixed import structure
from agents.nova.query_generator import generate_queries
from agents.nova.prompt_templates import parser, MarketInsight
from agents.nova.article_processor import summarize_article_data
from agents.nova.insight_gen import build_market_insight_chain, get_market_insights
from agents.nova.defaults import create_default_market_insight
from agents.nova.web_search import run_web_search_agent
from agents.nova.web_scrape import extract_all_articles

# User pain agent import
from agents.user_pain_agent.reddit_scraper import run_user_pain_agent

# Risk agent dynamic import
import sys
import importlib.util

def load_risk_agent():
    """Dynamic import for risk agent with better error handling"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        risk_agent_path = os.path.join(base_dir, "agents", "risk_agent", "risk_agent.py")
        if not os.path.exists(risk_agent_path):
            print(f"⚠️ Risk agent not found at {risk_agent_path}")
            return None
        
        spec = importlib.util.spec_from_file_location("risk_agent", risk_agent_path)
        risk_agent = importlib.util.module_from_spec(spec)
        sys.modules["risk_agent"] = risk_agent
        spec.loader.exec_module(risk_agent)
        return risk_agent
    except Exception as e:
        print(f"❌ Error loading risk agent: {e}")
        return None


class OptimizedFoundrScanPipeline:
    """Optimized pipeline with session-only storage and proper error handling"""
    
    def __init__(self, firebase_service=None):
        self.firebase_service = firebase_service
        self.idea_extractor = IdeaExtractor()

    def save_to_firestore(self, uid: str, session_id: str, field: str, data: Any) -> bool:
        """Save to Firestore user session with improved error handling"""
        if not self.firebase_service or not uid or not session_id:
            print(f"⚠️ Cannot save {field} - missing firebase_service, uid, or session_id")
            return False
        
        try:
            session_ref = self.firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id)
            
            # Convert custom objects to dict if needed
            serialized_data = self._serialize_data(data)
            
            session_ref.set({field: serialized_data}, merge=True)
            print(f"✅ Saved {field} to Firestore session {session_id}")
            return True
        except Exception as e:
            print(f"❌ Error saving {field} to Firestore: {e}")
            return False

    def _serialize_data(self, obj: Any) -> Any:
        """Convert complex objects to JSON-serializable format"""
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        elif hasattr(obj, 'dict'):
            return obj.dict()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return {k: self._serialize_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_data(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        else:
            try:
                return str(obj)
            except:
                return f"<{type(obj).__name__} object>"

    def run_idea_analysis(self, startup_data: Optional[Dict] = None, uid: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Step 1: Get and analyze startup idea"""
        print("🔍 Starting idea analysis...")
        
        # If startup_data is provided, use it directly (from API)
        if startup_data:
            print("🔧 Using provided startup data")
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "startup_analysis", startup_data)
            return startup_data
        
        # Fallback to interactive mode (for standalone usage)
        try:
            idea, conversation = self.idea_extractor.interactive_idea_extractor()
            summary = self.idea_extractor.summarize_startup(idea, conversation)
            
            print(f"🔍 Idea analysis result type: {type(summary)}")
            
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "startup_analysis", summary)
            
            return summary
        except Exception as e:
            print(f"❌ Error in idea analysis: {e}")
            return {}

    async def _run_competitor_analysis_async(self, startup_data: Dict[str, Any], uid: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Run competitor analysis asynchronously"""
        try:
            print("👥 Starting competitor analysis...")
            
            if not startup_data:
                raise ValueError("No startup data provided for competitor analysis")
            
            # Call the async competitor_agent function
            competitor_data = await competitor_agent(startup_data)
            
            # Validate the result
            if not isinstance(competitor_data, dict):
                raise ValueError(f"Invalid competitor data type: {type(competitor_data)}")
            
            # Save to Firebase if session info provided
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "competitor_analysis", competitor_data)
                
            print(f"✅ Competitor analysis complete - found {competitor_data.get('competitor_count', 0)} competitors")
            return competitor_data
            
        except Exception as e:
            print(f"❌ Error in competitor analysis: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "competitors": [],
                "gaps": [],
                "analysis": f"Analysis failed: {str(e)}",
                "competitor_count": 0
            }

    def _run_market_research_sync(self, startup_data: Dict[str, Any], uid: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Synchronous market research with better error handling"""
        print("📊 Starting market research...")
        
        if not startup_data:
            print("❌ No startup data provided for market research!")
            default_insights = create_default_market_insight()
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "market_insights", default_insights)
            return default_insights

        try:
            print(f"🔍 Analyzing startup: {startup_data.get('title', 'Unknown')}")
            
            # Step 1: Generate queries
            print("🔍 Generating search queries...")
            queries = generate_queries(startup_data)
            print(f"📝 Generated {len(queries)} search queries: {queries}")
            
            # Step 2: Web search
            print("🔍 Running web search...")
            print("🔍 DEBUG: About to run web search...")
            article_links = run_web_search_agent(queries)
            print(f"DEBUG: article_links type = {type(article_links)}, sample = {str(article_links)[:500]}")
            print(f"🌐 Found {len(article_links)} articles")
            
            if not article_links:
                raise ValueError("No articles found during web search")
            
            # Step 3: Extract articles
            print("🔍 Extracting article content...")
            article_data = extract_all_articles(article_links)
            
            if not article_data:
                raise ValueError("No article data extracted")
            
            # Step 4: Summarize articles
            print("🔍 Summarizing articles...")
            summarized_data = summarize_article_data(article_data)
            
            # Step 5: Build market insight chain
            print("🔍 Building market insight chain...")
            chain = build_market_insight_chain()
            
            inputs = {
                "startup_json": json.dumps(startup_data),
                "scraped_text": summarized_data,
                "format_instructions": parser.get_format_instructions()
            }
            
            # Step 6: Get market insights
            print("🔍 Getting market insights...")
            result = get_market_insights(chain, inputs)
            
            # Ensure result is a dictionary
            if hasattr(result, 'model_dump'):
                result = result.model_dump()
            elif hasattr(result, 'dict'):
                result = result.dict()
            elif isinstance(result, dict) and 'text' in result:
                if hasattr(result['text'], 'model_dump'):
                    result = result['text'].model_dump()
                elif hasattr(result['text'], 'dict'):
                    result = result['text'].dict()
            
            print(f"🔍 Market insights result type: {type(result)}")
            
            # Save to Firestore
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "market_insights", result)
            
            print("✅ Market research complete")
            return result

        except Exception as e:
            print(f"❌ Error in market research: {str(e)}")
            traceback.print_exc()
            
            print("🔄 Falling back to default market data")
            default_insights = create_default_market_insight()
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "market_insights", default_insights)
            return default_insights

    def _run_user_pain_agent_sync(self, startup_data: Dict[str, Any], uid: Optional[str] = None, session_id: Optional[str] = None) -> List[Any]:
        """User pain agent analysis with better error handling"""
        print("😣 Starting user pain analysis...")
        
        try:
            if not startup_data:
                print("⚠️ No startup data provided for user pain analysis")
                return []
            
            user_pain_points = run_user_pain_agent(startup_data)
            
            # Ensure it's a list
            if not isinstance(user_pain_points, list):
                user_pain_points = []
            
            # Save to Firestore
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "user_pain_points", user_pain_points)
            
            print(f"✅ User pain analysis complete - found {len(user_pain_points)} pain points")
            return user_pain_points
            
        except Exception as e:
            print(f"❌ Error in user pain analysis: {e}")
            traceback.print_exc()
            return []

    async def run_parallel_analysis(self, startup_data: Dict[str, Any], uid: Optional[str] = None, session_id: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any], List[Any]]:
        """Run all analyses in parallel with improved error handling"""
        print("🚀 Starting parallel analysis (competitor + market research + user pain points)...")
        
        # Validate input
        if not startup_data:
            raise ValueError("No startup data provided for parallel analysis")
        
        try:
            # Use asyncio.gather for better async handling
            competitor_task = self._run_competitor_analysis_async(startup_data, uid, session_id)
            
            # Run sync functions in thread pool
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                market_task = loop.run_in_executor(
                    executor, self._run_market_research_sync, startup_data, uid, session_id
                )
                pain_task = loop.run_in_executor(
                    executor, self._run_user_pain_agent_sync, startup_data, uid, session_id
                )
                
                print("⏳ Waiting for all analyses to complete...")
                results = await asyncio.gather(
                    competitor_task, market_task, pain_task, 
                    return_exceptions=True
                )
            
            competitor_data, market_data, user_pain_points = results
            
            # Handle any exceptions
            if isinstance(competitor_data, Exception):
                print(f"❌ Competitor analysis failed: {competitor_data}")
                competitor_data = {
                    "gaps": [],
                    "competitors": [],
                    "analysis": f"Analysis failed: {str(competitor_data)}",
                    "competitor_count": 0,
                    "status": "error"
                }
            
            if isinstance(market_data, Exception):
                print(f"❌ Market research failed: {market_data}")
                market_data = create_default_market_insight()
            
            if isinstance(user_pain_points, Exception):
                print(f"❌ User pain agent failed: {user_pain_points}")
                user_pain_points = []
                
            print("✅ All parallel analyses completed!")
            return competitor_data, market_data, user_pain_points
            
        except Exception as e:
            print(f"❌ Error in parallel analysis: {e}")
            traceback.print_exc()
            
            # Return default values
            return (
                {"gaps": [], "competitors": [], "analysis": f"Failed: {str(e)}", "competitor_count": 0, "status": "error"},
                create_default_market_insight(),
                []
            )

    def generate_recommendations(self, startup_data: Dict, competitor_data: Dict, market_data: Dict, uid: Optional[str] = None, session_id: Optional[str] = None) -> Dict:
        """Generate strategic recommendations with better validation"""
        print("💡 Generating recommendations...")
        
        # Ensure inputs are dictionaries
        startup_data = startup_data if isinstance(startup_data, dict) else {}
        competitor_data = competitor_data if isinstance(competitor_data, dict) else {}
        market_data = market_data if isinstance(market_data, dict) else {}

        try:
            # Enhanced recommendations structure
            recommendations = {
                "market_strategy": [],
                "competitive_advantages": [],
                "growth_opportunities": [],
                "risk_mitigation": [],
                "next_steps": [],
                # Legacy fields for backward compatibility
                "market_opportunity": "High" if market_data.get("market_size", 0) > 1000000000 else "Medium",
                "competition_level": "Low" if len(competitor_data.get("competitors", [])) < 5 else "High",
                "technical_feasibility": "High" if startup_data.get("tech_stack") else "Medium",
                "business_model_viability": "High" if startup_data.get("business_model") else "Medium",
                "risk_assessment": "Low" if len(startup_data.get("risks", [])) < 3 else "High",
                "recommended_next_steps": [
                    "Conduct detailed market research",
                    "Develop MVP",
                    "Build founding team",
                    "Secure initial funding",
                    "Validate with potential customers"
                ]
            }

            # Market Strategy Recommendations
            market_trend = market_data.get("market_trend", "growing market demand")
            recommendations["market_strategy"].append({
                "focus": "Market Positioning",
                "insight": f"Based on {market_trend}",
                "action": "Position the product to capitalize on this trend"
            })

            # Competitive Advantage Recommendations  
            for gap in competitor_data.get("gaps", []):
                recommendations["competitive_advantages"].append({
                    "focus": "Market Gap",
                    "insight": str(gap),
                    "action": "Develop features/services to address this gap"
                })

            # Growth Opportunities
            for opp in market_data.get("market_opportunities", []):
                recommendations["growth_opportunities"].append({
                    "focus": "Expansion",
                    "insight": str(opp),
                    "action": "Develop roadmap to capture this opportunity"
                })

            # Risk Mitigation
            for risk in market_data.get("market_risks", []):
                recommendations["risk_mitigation"].append({
                    "focus": "Risk Management",
                    "insight": str(risk),
                    "action": "Develop mitigation strategy"
                })

            # Next Steps
            recommendations["next_steps"] = [
                {
                    "focus": "MVP Development",
                    "action": "Build minimum viable product focusing on core differentiators",
                    "timeline": "0-3 months"
                },
                {
                    "focus": "Market Testing",
                    "action": "Test with early adopters in primary target segment",
                    "timeline": "3-6 months"
                },
                {
                    "focus": "Scaling Strategy",
                    "action": "Develop scaling plan based on market feedback",
                    "timeline": "6-12 months"
                }
            ]

            # Save to Firestore
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "recommendations", recommendations)
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error generating recommendations: {e}")
            return {"error": str(e), "status": "failed"}

    def load_investor_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Load investor data - using default data for session storage"""
        top_vcs = [
            {"name": "Sequoia Capital", "focus": "Early to growth stage", "typical_check": "$1M-100M"},
            {"name": "Andreessen Horowitz", "focus": "Tech startups", "typical_check": "$500K-50M"},
            {"name": "Kleiner Perkins", "focus": "Venture capital", "typical_check": "$1M-25M"},
        ]
        top_angels = [
            {"name": "Naval Ravikant", "focus": "Tech, consumer", "typical_check": "$25K-250K"},
            {"name": "Jason Calacanis", "focus": "Early stage", "typical_check": "$25K-100K"},
            {"name": "Ron Conway", "focus": "Seed stage", "typical_check": "$25K-500K"},
        ]
        return top_vcs, top_angels

    def create_final_report(self, startup_data: Dict, competitor_data: Dict, market_data: Dict, user_pain_points: List = None, uid: Optional[str] = None, session_id: Optional[str] = None) -> Dict:
        """Create comprehensive final report"""
        print("📋 Creating final report...")
        
        try:
            # Load investor data
            top_vcs, top_angels = self.load_investor_data()

            # Generate recommendations
            recommendations = self.generate_recommendations(startup_data, competitor_data, market_data, uid, session_id)

            final_report = {
                # Enhanced structure
                "startup_analysis": startup_data,
                "competitor_landscape": competitor_data,
                "market_insights": market_data,
                "user_pain_points": user_pain_points or [],
                "investor_landscape": {
                    "venture_capitalist": top_vcs,
                    "angel_investors": top_angels
                },
                "recommendations": recommendations,
                # Legacy structure for backward compatibility
                "startup_summary": startup_data,
                "competitor_analysis": competitor_data,
                "market_research": market_data,
                "timestamp": str(Path().cwd()),
                "status": "complete"
            }
            
            # Save to Firestore
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "complete_analysis", final_report)
            
            return final_report
            
        except Exception as e:
            print(f"❌ Error creating final report: {e}")
            return {"error": str(e), "status": "failed"}

    async def run_pipeline_async(self, startup_data: Optional[Dict] = None, uid: Optional[str] = None, session_id: Optional[str] = None) -> Dict:
        """Run the complete analysis pipeline with parallel execution"""
        try:
            print("🚀 Starting Optimized FoundrScan Analysis Pipeline...")
            
            # Step 1: Idea Analysis (sequential - needed by others)
            print("\n1️⃣ Analyzing Startup Idea...")
            if startup_data is None:
                startup_data = self.run_idea_analysis(None, uid, session_id)
            else:
                # Save provided startup data to session
                if uid and session_id:
                    self.save_to_firestore(uid, session_id, "startup_analysis", startup_data)
            
            if not startup_data:
                raise ValueError("Failed to get startup data from idea analysis")
            
            # Steps 2, 3 & 4: Run all analyses in parallel
            print("\n2️⃣, 3️⃣ & 4️⃣ Running Competitor Analysis, Market Research, and User Pain Agent in Parallel...")
            competitor_data, market_data, user_pain_points = await self.run_parallel_analysis(startup_data, uid, session_id)
            
            # Step 5: Integration (sequential - needs results from parallel steps)
            print("\n5️⃣ Generating Final Report...")
            final_report = self.create_final_report(
                startup_data,
                competitor_data,
                market_data,
                user_pain_points,
                uid,
                session_id
            )
            
            print("\n✨ Analysis Complete! Results saved to Firestore session.")
            print(f"📊 Summary: {competitor_data.get('competitor_count', 0)} competitors, "
                  f"{len(user_pain_points)} pain points identified")
            
            return final_report
            
        except Exception as e:
            print(f"❌ Pipeline error: {str(e)}")
            traceback.print_exc()
            
            # Return error report
            error_report = {
                "status": "error",
                "error": str(e),
                "startup_analysis": startup_data or {},
                "competitor_landscape": {"competitors": [], "status": "error"},
                "market_insights": create_default_market_insight(),
                "user_pain_points": [],
                "recommendations": {"error": str(e)}
            }
            
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "error_report", error_report)
            
            return error_report

    def run_pipeline(self, startup_data: Optional[Dict] = None, uid: Optional[str] = None, session_id: Optional[str] = None) -> Dict:
        """Synchronous wrapper for the async pipeline"""
        try:
            return asyncio.run(self.run_pipeline_async(startup_data, uid, session_id))
        except Exception as e:
            print(f"❌ Error running pipeline: {e}")
            traceback.print_exc()
            return {"status": "error", "error": str(e)}


# Backward compatibility alias
ParallelFoundrScanPipeline = OptimizedFoundrScanPipeline