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

class ParallelFoundrScanPipeline:
    def __init__(self, firebase_service):
        self.firebase_service = firebase_service
        self.idea_extractor = IdeaExtractor()

    def save_to_firestore(self, uid, session_id, field, data):
        session_ref = self.firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id)
        session_ref.update({field: data})

    def run_idea_analysis(self) -> Dict[str, Any]:
        print("🔍 DEBUG: Starting idea analysis...")
        USE_TEST_DATA = False  # Easy toggle for testing
        if USE_TEST_DATA:
            try:
                summary_path = Path("outputs") / "startup_summary.json"
                if summary_path.exists():
                    with open(summary_path, 'r') as f:
                        test_summary = json.load(f)
                    print("🔧 TESTING: Loaded existing startup data from file")
                    return test_summary
                else:
                    print("⚠️ No existing startup_summary.json found, falling back to interactive mode")
                    USE_TEST_DATA = False
            except Exception as e:
                print(f"⚠️ Error loading test data: {e}, falling back to interactive mode")
                USE_TEST_DATA = False
        idea, conversation = self.idea_extractor.interactive_idea_extractor()
        summary = self.idea_extractor.summarize_startup(idea, conversation)
        print(f"🔍 DEBUG: Idea analysis result type: {type(summary)}")
        print(f"🔍 DEBUG: Idea analysis keys: {list(summary.keys()) if isinstance(summary, dict) else 'Not a dict'}")
        return summary

    def _run_competitor_analysis_sync(self, startup_data: Dict[str, Any], uid, session_id) -> Dict[str, Any]:
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
        self.save_to_firestore(uid, session_id, "competitor_analysis", competitor_analysis)
        print(f"✅ Competitor analysis complete")
        return competitor_analysis

    def _run_market_research_sync(self, startup_data: Dict[str, Any], uid, session_id) -> Dict[str, Any]:
        print(f"📊 Starting market research in thread...")
        print(f"🔍 DEBUG: Market research input type: {type(startup_data)}")
        print(f"🔍 DEBUG: Market research startup_data is None: {startup_data is None}")
        print(f"🔍 DEBUG: Market research startup_data keys: {list(startup_data.keys()) if isinstance(startup_data, dict) else 'Not a dict'}")
        if not startup_data:
            print("❌ No startup data provided!")
            default_insights = create_default_market_insight()
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
            print(f"🔍 DEBUG: Market insights result type: {type(result)}")
            self.save_to_firestore(uid, session_id, "market_insights", result)
            print(f"✅ Market research complete")
            return result
        except Exception as e:
            print(f"❌ Error in market research: {str(e)}")
            print("Falling back to default market data")
            default_insights = create_default_market_insight()
            self.save_to_firestore(uid, session_id, "market_insights", default_insights)
            return default_insights

    def _create_default_market_insight(self) -> Dict[str, Any]:
        return {
            "market_size": 1000000000,
            "growth_rate": "10%",
            "key_trends": ["AI adoption", "Remote work", "Digital transformation"],
            "opportunities": ["Untapped market segments", "Emerging technologies"],
            "risks": ["Competition", "Regulatory changes"],
            "status": "default"
        }

    async def run_parallel_analysis(self, startup_data: Dict[str, Any], uid, session_id) -> tuple[Dict[str, Any], Dict[str, Any]]:
        print("🚀 Starting parallel analysis (competitor + market research)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            loop = asyncio.get_event_loop()
            competitor_future = loop.run_in_executor(
                executor, self._run_competitor_analysis_sync, startup_data, uid, session_id
            )
            market_future = loop.run_in_executor(
                executor, self._run_market_research_sync, startup_data, uid, session_id
            )
            competitor_data, market_data = await asyncio.gather(
                competitor_future, market_future, return_exceptions=True
            )
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
            return competitor_data, market_data

    def generate_recommendations(self, startup_data: Dict, competitor_data: Dict, market_data: Dict, uid, session_id) -> Dict:
        print("💡 Generating recommendations...")
        recommendations = {
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
        self.save_to_firestore(uid, session_id, "recommendations", recommendations)
        return recommendations

    def create_final_report(self, startup_data: Dict, competitor_data: Dict, market_data: Dict, uid, session_id) -> Dict:
        print("📋 Creating final report...")
        final_report = {
            "startup_summary": startup_data,
            "competitor_analysis": competitor_data,
            "market_research": market_data,
            "recommendations": self.generate_recommendations(startup_data, competitor_data, market_data, uid, session_id),
            "timestamp": str(Path().cwd()),
            "status": "complete"
        }
        self.save_to_firestore(uid, session_id, "complete_analysis", final_report)
        return final_report

    async def run_pipeline_async(self, startup_data: Dict, uid, session_id) -> Dict:
        print("🚀 Starting FoundrScan Pipeline...")
        if not startup_data:
            startup_data = self.run_idea_analysis()
        competitor_data, market_data = await self.run_parallel_analysis(startup_data, uid, session_id)
        final_report = self.create_final_report(startup_data, competitor_data, market_data, uid, session_id)
        print("✅ Pipeline complete!")
        return final_report

    def run_pipeline(self, startup_data: Dict, uid, session_id) -> Dict:
        return asyncio.run(self.run_pipeline_async(startup_data, uid, session_id))

class ProcessParallelFoundrScanPipeline(ParallelFoundrScanPipeline):
    """Process-based parallel pipeline for better isolation"""
    
    async def run_parallel_analysis(self, startup_data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        print("🚀 Starting process-based parallel analysis...")
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            loop = asyncio.get_event_loop()
            competitor_future = loop.run_in_executor(
                executor, 
                self._run_competitor_analysis_sync, 
                startup_data
            )
            market_future = loop.run_in_executor(
                executor, 
                self._run_market_research_sync, 
                startup_data
            )
            competitor_data, market_data = await asyncio.gather(
                competitor_future, 
                market_future,
                return_exceptions=True
            )
            if isinstance(competitor_data, Exception):
                competitor_data = {"error": str(competitor_data)}
            if isinstance(market_data, Exception):
                market_data = create_default_market_insight()
            return competitor_data, market_data
