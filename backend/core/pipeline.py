import json
import os
from pathlib import Path
from typing import Dict, Any
import asyncio
import concurrent.futures
from functools import partial

# Core imports
from .idea_extractor import IdeaExtractor

# Agent imports
from agents.idea_agent import StartupIdeaAnalyzer

# Competitor agent imports
from agents.competitor_agent.domain import competitor_agent

# Nova imports
from agents.nova.query_generator import generate_queries
from agents.nova.prompt_templates import parser
from agents.nova.prompt_templates import MarketInsight
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
    """Dynamic import for risk agent"""
    try:
        base_dir = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))
        risk_agent_path = os.path.join(base_dir, "agents", "risk_agent", "risk_agent.py")
        if not os.path.exists(risk_agent_path):
            raise FileNotFoundError(f"Risk agent not found at {risk_agent_path}")
        spec = importlib.util.spec_from_file_location("risk_agent", risk_agent_path)
        risk_agent = importlib.util.module_from_spec(spec)
        sys.modules["risk_agent"] = risk_agent
        spec.loader.exec_module(risk_agent)
        return risk_agent
    except Exception as e:
        print(f"❌ Error loading risk agent: {e}")
        return None


class ParallelFoundrScanPipeline:
    def __init__(self, firebase_service=None):
        self.firebase_service = firebase_service
        self.idea_extractor = IdeaExtractor()
        
        # COMMENTED OUT: No local output directory needed for session-only storage
        # OUTPUT_DIR = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs'))
        # if not OUTPUT_DIR.exists():
        #     OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        # self.output_dir = OUTPUT_DIR

    def save_to_firestore(self, uid, session_id, field, data):
        """Save to Firestore user session - PRIMARY STORAGE METHOD"""
        if not self.firebase_service or not uid or not session_id:
            print(f"⚠️ Cannot save {field} - missing firebase_service, uid, or session_id")
            return
        
        try:
            session_ref = self.firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id)
            # Convert custom objects to dict if needed
            if hasattr(data, "to_dict"):
                data = data.to_dict()
            elif hasattr(data, "model_dump"):
                data = data.model_dump()
            elif hasattr(data, "dict"):
                data = data.dict()
            
            session_ref.set({field: data}, merge=True)
            print(f"✅ Saved {field} to Firestore session {session_id}")
        except Exception as e:
            print(f"❌ Error saving {field} to Firestore: {e}")

    # COMMENTED OUT: No local file saving for session-only storage
    # def save_json(self, filename: str, data: Any) -> None:
    #     """Save JSON files locally - REMOVED FOR SESSION-ONLY STORAGE"""
    #     filepath = self.output_dir / filename
    #     
    #     def serialize_data(obj):
    #         """Convert complex objects to JSON-serializable format"""
    #         if hasattr(obj, 'to_dict'):
    #             return obj.to_dict()
    #         elif hasattr(obj, 'model_dump'):
    #             return obj.model_dump()
    #         elif hasattr(obj, 'dict'):
    #             return obj.dict()
    #         elif isinstance(obj, dict):
    #             return {k: serialize_data(v) for k, v in obj.items()}
    #         elif isinstance(obj, list):
    #             return [serialize_data(item) for item in obj]
    #         return obj
    # 
    #     try:
    #         serialized_data = serialize_data(data)
    #         with open(filepath, 'w', encoding='utf-8') as f:
    #             json.dump(serialized_data, f, indent=2, ensure_ascii=False)
    #         print(f"✅ Saved {filename} to {filepath}")
    #     except Exception as e:
    #         print(f"❌ Error saving {filename}: {e}")
    #         print(f"🔍 DEBUG: Data type: {type(data)}")
    
    @staticmethod
    def ensure_dict(obj):
        """Ensure object is dictionary"""
        if isinstance(obj, dict):
            return obj
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return obj

    def run_idea_analysis(self, startup_data=None, uid=None, session_id=None) -> Dict[str, Any]:
        """Step 1: Get and analyze startup idea"""
        print("🔍 DEBUG: Starting idea analysis...")
        
        # If startup_data is provided, use it directly (from API)
        if startup_data:
            print("🔧 Using provided startup data")
            # Save to Firestore if we have uid and session_id
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "startup_analysis", startup_data)
            return startup_data
        
        # COMMENTED OUT: Test data loading from local files - using session-only storage
        # USE_TEST_DATA = False  # Easy toggle for testing
        # if USE_TEST_DATA:
        #     try:
        #         summary_path = self.output_dir / "startup_summary.json"
        #         if summary_path.exists():
        #             with open(summary_path, 'r') as f:
        #                 test_summary = json.load(f)
        #             print("🔧 TESTING: Loaded existing startup data from file")
        #             return test_summary
        #         else:
        #             print("⚠️ No existing startup_summary.json found, falling back to interactive mode")
        #             USE_TEST_DATA = False
        #     except Exception as e:
        #         print(f"⚠️ Error loading test data: {e}, falling back to interactive mode")
        #         USE_TEST_DATA = False
        
        # Fallback to interactive mode (for standalone usage)
        idea, conversation = self.idea_extractor.interactive_idea_extractor()
        summary = self.idea_extractor.summarize_startup(idea, conversation)
        print(f"🔍 DEBUG: Idea analysis result type: {type(summary)}")
        print(f"🔍 DEBUG: Idea analysis keys: {list(summary.keys()) if isinstance(summary, dict) else 'Not a dict'}")
        
        # Save to Firestore only (no local files)
        # COMMENTED OUT: self.save_json("startup_summary.json", summary)
        if uid and session_id:
            self.save_to_firestore(uid, session_id, "startup_analysis", summary)
        
        return summary

    def _run_competitor_analysis_sync(self, startup_data: Dict[str, Any], uid=None, session_id=None) -> Dict[str, Any]:
        """Synchronous competitor analysis"""
        print(f"👥 Starting competitor analysis in thread...")
        print(f"🔍 DEBUG: Competitor analysis input type: {type(startup_data)}")
        print(f"🔍 DEBUG: Competitor analysis startup_data: {startup_data is not None}")
        
        try:
            # Use the new in-memory competitor agent
            from agents.competitor_agent.domain import competitor_agent_from_data
            competitor_analysis = competitor_agent_from_data(startup_data)
            if not isinstance(competitor_analysis, dict):
                competitor_analysis = {
                    "gaps": [],
                    "competitors": [],
                    "analysis": "Analysis returned invalid format",
                    "competitor_count": 0,
                    "status": "error"
                }
        except Exception as e:
            print(f"❌ Error in competitor analysis: {e}")
            competitor_analysis = {
                "gaps": [],
                "competitors": [],
                "analysis": f"Analysis failed: {str(e)}",
                "competitor_count": 0,
                "status": "error"
            }
        
        # Save to Firestore only (no local files)
        # COMMENTED OUT: self.save_json("competitor_analysis.json", competitor_analysis)
        if uid and session_id:
            self.save_to_firestore(uid, session_id, "competitor_analysis", competitor_analysis)
        
        print(f"✅ Competitor analysis complete")
        return competitor_analysis

    def _run_market_research_sync(self, startup_data: Dict[str, Any], uid=None, session_id=None) -> Dict[str, Any]:
        """Synchronous market research"""
        print(f"📊 Starting market research in thread...")
        print(f"🔍 DEBUG: Market research input type: {type(startup_data)}")
        print(f"🔍 DEBUG: Market research startup_data is None: {startup_data is None}")
        print(f"🔍 DEBUG: Market research startup_data keys: {list(startup_data.keys()) if isinstance(startup_data, dict) else 'Not a dict'}")
        
        if not startup_data:
            print("❌ No startup data provided!")
            default_insights = create_default_market_insight()
            # Save to Firestore only
            # COMMENTED OUT: self.save_json("market_insights.json", default_insights)
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "market_insights", default_insights)
            return default_insights

        try:
            print(f"🔍 Analyzing startup: {startup_data.get('title', 'Unknown')}")
            print("🔍 DEBUG: About to generate queries...")
            queries = generate_queries(startup_data)
            print(f"📝 Generated {len(queries)} search queries")
            print(f"🔍 DEBUG: Queries: {queries}")
            
            print("🔍 DEBUG: About to run web search...")
            article_links = run_web_search_agent(queries)
            print(f"🌐 Found {len(article_links)} articles")
            
            print("🔍 DEBUG: About to extract articles...")
            article_data = extract_all_articles(article_links)
            if not article_data:
                raise ValueError("No article data extracted")
            
            print("🔍 DEBUG: About to summarize articles...")
            summarized_data = summarize_article_data(article_data)
            
            print("🔍 DEBUG: About to build market insight chain...")
            chain = build_market_insight_chain()
            inputs = {
                "startup_json": json.dumps(startup_data),
                "scraped_text": summarized_data,
                "format_instructions": parser.get_format_instructions()
            }
            
            print("🔍 DEBUG: About to get market insights...")
            result = get_market_insights(chain, inputs)
            result = self.ensure_dict(result)
            print(f"🔍 DEBUG: Market insights result type: {type(result)}")
            
            # Save to Firestore only (no local files)
            # COMMENTED OUT: self.save_json("market_insights.json", result)
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "market_insights", result)
            
            print(f"✅ Market research complete")
            return result

        except Exception as e:
            print(f"❌ Error in market research: {str(e)}")
            print(f"🔍 DEBUG: Exception type: {type(e)}")
            print(f"🔍 DEBUG: Exception args: {e.args}")
            import traceback
            print(f"🔍 DEBUG: Full traceback:")
            traceback.print_exc()
            
            print("Falling back to default market data")
            default_insights = create_default_market_insight()
            # Save to Firestore only
            # COMMENTED OUT: self.save_json("market_insights.json", default_insights)
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "market_insights", default_insights)
            return default_insights

    def _run_user_pain_agent_sync(self, startup_data: Dict[str, Any], uid=None, session_id=None) -> list:
        """User pain agent analysis"""
        print(f"😣 Starting user pain analysis in thread...")
        try:
            user_pain_points = run_user_pain_agent(startup_data)
            
            # Save to Firestore only (no local files)
            if uid and session_id:
                self.save_to_firestore(uid, session_id, "user_pain_points", user_pain_points)
            
            return user_pain_points
        except Exception as e:
            print(f"❌ Error in user pain analysis: {e}")
            return []

    def _create_default_market_insight(self) -> Dict[str, Any]:
        """Default market insight"""
        return {
            "market_size": 1000000000,
            "growth_rate": "10%",
            "key_trends": ["AI adoption", "Remote work", "Digital transformation"],
            "opportunities": ["Untapped market segments", "Emerging technologies"],
            "risks": ["Competition", "Regulatory changes"],
            "status": "default"
        }

    async def run_parallel_analysis(self, startup_data: Dict[str, Any], uid=None, session_id=None) -> tuple[Dict[str, Any], Dict[str, Any], list]:
        """Run all analyses in parallel"""
        print("🚀 Starting parallel analysis (competitor + market research + user pain points)...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            loop = asyncio.get_event_loop()
            
            # Create futures for all three analyses
            competitor_future = loop.run_in_executor(
                executor, self._run_competitor_analysis_sync, startup_data, uid, session_id
            )
            market_future = loop.run_in_executor(
                executor, self._run_market_research_sync, startup_data, uid, session_id
            )
            pain_points_future = loop.run_in_executor(
                executor, self._run_user_pain_agent_sync, startup_data, uid, session_id
            )
            
            print("⏳ Waiting for all analyses to complete...")
            competitor_data, market_data, user_pain_points = await asyncio.gather(
                competitor_future, market_future, pain_points_future, return_exceptions=True
            )
            
            # Handle any exceptions
            if isinstance(competitor_data, Exception):
                print(f"❌ Competitor analysis failed: {competitor_data}")
                competitor_data = {
                    "gaps": [],
                    "competitors": [],
                    "analysis": "Analysis failed",
                    "error": str(competitor_data)
                }
            
            if isinstance(market_data, Exception):
                print(f"❌ Market research failed: {market_data}")
                market_data = self._create_default_market_insight()
            
            if isinstance(user_pain_points, Exception):
                print(f"❌ User pain agent failed: {user_pain_points}")
                user_pain_points = []
                
            print("✅ All analyses completed!")
            return competitor_data, market_data, user_pain_points

    def generate_recommendations(self, startup_data: Dict, competitor_data: Dict, market_data: Dict, uid=None, session_id=None) -> Dict:
        """Generate strategic recommendations"""
        print("💡 Generating recommendations...")
        
        # Ensure inputs are dictionaries
        if not isinstance(competitor_data, dict):
            competitor_data = {}
        if not isinstance(market_data, dict):
            market_data = {}
        if not isinstance(startup_data, dict):
            startup_data = {}

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
                "insight": gap,
                "action": "Develop features/services to address this gap"
            })

        # Growth Opportunities
        for opp in market_data.get("market_opportunities", []):
            recommendations["growth_opportunities"].append({
                "focus": "Expansion",
                "insight": opp,
                "action": "Develop roadmap to capture this opportunity"
            })

        # Risk Mitigation
        for risk in market_data.get("market_risks", []):
            recommendations["risk_mitigation"].append({
                "focus": "Risk Management",
                "insight": risk,
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

        # Save to Firestore only
        if uid and session_id:
            self.save_to_firestore(uid, session_id, "recommendations", recommendations)
        
        return recommendations

    def add_risk_mitigation_to_report(self, session_data: Dict, uid=None, session_id=None):
        """Add risk analysis to session data (updated to work with session storage)"""
        try:
            risk_agent = load_risk_agent()
            print("\n🚨 Running risk analysis on session data...")
            
            # COMMENTED OUT: Local file processing - using session data instead
            # risk_agent.analyze_risks(complete_analysis_path)
            # risk_json_path = os.path.join(os.path.dirname(__file__), 'risk_agent', 'risk_analysis.json')
            
            # Process risk analysis directly from session data
            risk_data = {}  # Placeholder - would need to adapt risk_agent to work with dict input
            
            # Add to session data
            try:
                session_data['risk_mitigation'] = risk_data.get('risk_matrix', [])
                
                # Save updated session data to Firestore
                if uid and session_id:
                    self.save_to_firestore(uid, session_id, "complete_analysis", session_data)
                
                print("✅ Added risk_mitigation to session data")
            except Exception as e:
                print(f"❌ Error updating session data with risk analysis: {e}")
        except Exception as e:
            print(f"❌ Error in risk analysis: {e}")

    def load_investor_data(self, uid=None, session_id=None) -> tuple[list, list]:
        """Load investor data - adapted for session storage"""
        # COMMENTED OUT: Local file loading - using default data for session storage
        # investors_path = self.output_dir / "investors.json"
        # top_vcs = []
        # top_angels = []
        # try:
        #     if investors_path.exists():
        #         with open(investors_path, 'r', encoding='utf-8') as f:
        #             investors_data = json.load(f)
        #             # Only take top 5 from each key
        #             top_vcs = investors_data.get('venture_capitalist', [])[:5]
        #             top_angels = investors_data.get('angel_investors', [])[:5]
        # except Exception as e:
        #     print(f"❌ Error loading investors.json: {e}")
        
        # Default investor data for session storage
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

    def create_final_report(self, startup_data: Dict, competitor_data: Dict, market_data: Dict, user_pain_points: list = None, uid=None, session_id=None) -> Dict:
        """Create comprehensive final report"""
        print("📋 Creating final report...")
        
        # Load investor data (adapted for session storage)
        top_vcs, top_angels = self.load_investor_data(uid, session_id)

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
        
        # Save to Firestore only (no local files)
        # COMMENTED OUT: self.save_json("complete_analysis.json", final_report)
        if uid and session_id:
            self.save_to_firestore(uid, session_id, "complete_analysis", final_report)
        
        return final_report

    async def run_pipeline_async(self, startup_data: Dict = None, uid=None, session_id=None) -> Dict:
        """Run the complete analysis pipeline with parallel execution"""
        try:
            print("🚀 Starting Parallel FoundrScan Analysis Pipeline...")
            
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
            
            # Step 6: Run risk analysis and update session data
            # COMMENTED OUT: Local file processing - adapted for session storage
            # complete_analysis_path = str(self.output_dir / "complete_analysis.json")
            # self.add_risk_mitigation_to_report(complete_analysis_path)
            self.add_risk_mitigation_to_report(final_report, uid, session_id)
            
            print("\n✅ All analysis complete. Results stored in user session.")
            return final_report
            
        except Exception as e:
            print(f"❌ Pipeline error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def run_pipeline(self, startup_data: Dict = None, uid=None, session_id=None) -> Dict:
        """Synchronous wrapper for the async pipeline"""
        return asyncio.run(self.run_pipeline_async(startup_data, uid, session_id))

class ProcessParallelFoundrScanPipeline(ParallelFoundrScanPipeline):
    """Process-based parallel pipeline for better isolation"""
    
    async def run_parallel_analysis(self, startup_data: Dict[str, Any], uid=None, session_id=None) -> tuple[Dict[str, Any], Dict[str, Any], list]:
        """Run analyses in parallel using processes"""
        print("🚀 Starting process-based parallel analysis...")
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
            loop = asyncio.get_event_loop()
            
            # Create partial functions to pass startup_data
            competitor_func = partial(self._run_competitor_analysis_sync, startup_data, uid, session_id)
            market_func = partial(self._run_market_research_sync, startup_data, uid, session_id)
            pain_func = partial(self._run_user_pain_agent_sync, startup_data, uid, session_id)
            
            competitor_future = loop.run_in_executor(executor, competitor_func)
            market_future = loop.run_in_executor(executor, market_func)
            pain_future = loop.run_in_executor(executor, pain_func)
            
            print("⏳ Waiting for all analyses to complete...")
            competitor_data, market_data, user_pain_points = await asyncio.gather(
                competitor_future, 
                market_future,
                pain_future,
                return_exceptions=True
            )
            
            # Handle any exceptions
            if isinstance(competitor_data, Exception):
                print(f"❌ Competitor analysis failed: {competitor_data}")
                competitor_data = {
                    "gaps": [],
                    "competitors": [],
                    "analysis": "Analysis failed",
                    "error": str(competitor_data)
                }
            
            if isinstance(market_data, Exception):
                print(f"❌ Market research failed: {market_data}")
                market_data = create_default_market_insight()
                
            if isinstance(user_pain_points, Exception):
                print(f"❌ User pain analysis failed: {user_pain_points}")
                user_pain_points = []
            
            print("✅ All analyses completed!")
            return competitor_data, market_data, user_pain_points