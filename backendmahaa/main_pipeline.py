#Main Pipeline for FoundrScan Analysis


import json
import os
from pathlib import Path
from typing import Dict, Any
import asyncio
import concurrent.futures
from functools import partial

# Idea agent & competitor agent imports
from agents.idea_agent import StartupIdeaAnalyzer
from competitor_agent.domain import competitor_agent 

# Nova imports
from nova.query_generator import generate_queries
from nova.prompt_templates import parser
from nova.prompt_templates import MarketInsight
from nova.article_processor import summarize_article_data
from nova.insight_gen import build_market_insight_chain, get_market_insights
from nova.defaults import create_default_market_insight
from nova.web_search import run_web_search_agent
from nova.web_scrape import extract_all_articles

class ParallelFoundrScanPipeline:
    def __init__(self):
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)

    def run_idea_analysis(self) -> Dict[str, Any]:
        """Step 1: Get and analyze startup idea"""
        print("🔍 DEBUG: Starting idea analysis...")

        # TEMPORARY: Use predefined startup data for testing
        USE_TEST_DATA = False  # Easy toggle for testing
        if USE_TEST_DATA:
            try:
                summary_path = self.output_dir / "startup_summary.json"
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

        analyzer = StartupIdeaAnalyzer()
        idea, conversation = analyzer.interactive_session()
        summary = analyzer.generate_summary(idea, conversation)
        print(f"🔍 DEBUG: Idea analysis result type: {type(summary)}")
        print(f"🔍 DEBUG: Idea analysis keys: {list(summary.keys()) if isinstance(summary, dict) else 'Not a dict'}")
        
        # Save output
        self.save_json("startup_summary.json", summary)
        return summary

    # Updated Main Pipeline - Modified _run_competitor_analysis_sync method
    def _run_competitor_analysis_sync(self, startup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous competitor analysis (for thread pool)"""
        print(f"👥 Starting competitor analysis in thread...")
        print(f"🔍 DEBUG: Competitor analysis input type: {type(startup_data)}")
        print(f"🔍 DEBUG: Competitor analysis startup_data: {startup_data is not None}")
        
        try:
            # Import here to avoid circular imports
            from competitor_agent.domain import competitor_agent
            
            competitor_analysis = competitor_agent()
            
            # Ensure we have a valid dictionary response
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
        
        # Save output
        self.save_json("competitor_analysis.json", competitor_analysis)
        print(f"✅ Competitor analysis complete")
        return competitor_analysis

    def _run_market_research_sync(self, startup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous market research (for thread pool)"""
        print(f"📊 Starting market research in thread...")
        print(f"🔍 DEBUG: Market research input type: {type(startup_data)}")
        print(f"🔍 DEBUG: Market research startup_data is None: {startup_data is None}")
        print(f"🔍 DEBUG: Market research startup_data keys: {list(startup_data.keys()) if isinstance(startup_data, dict) else 'Not a dict'}")
        
        if not startup_data:
            print("❌ No startup data provided!")
            return create_default_market_insight()

        try:
            print(f"🔍 Analyzing startup: {startup_data.get('title', 'Unknown')}")
            
            # Add debug info for each step
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
            
            # Save output and return
            self.save_json("market_insights.json", result)
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
            self.save_json("market_insights.json", default_insights)
            return default_insights

    async def run_parallel_analysis(self, startup_data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Run competitor analysis and market research in parallel"""
        print("🚀 Starting parallel analysis (competitor + market research)...")
        
        # Use ThreadPoolExecutor for CPU-bound tasks
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks to the thread pool
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
            
            # Wait for both to complete
            print("⏳ Waiting for both analyses to complete...")
            competitor_data, market_data = await asyncio.gather(
                competitor_future, 
                market_future,
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
            
            print("✅ Both analyses completed!")
            return competitor_data, market_data

    def generate_recommendations(self, startup_data: Dict, competitor_data: Dict, market_data: Dict) -> Dict:
        """Generate strategic recommendations based on all analysis"""
        # Ensure inputs are dictionaries
        if not isinstance(competitor_data, dict):
            competitor_data = {}
        if not isinstance(market_data, dict):
            market_data = {}
        if not isinstance(startup_data, dict):
            startup_data = {}

        recommendations = {
            "market_strategy": [],
            "competitive_advantages": [],
            "growth_opportunities": [],
            "risk_mitigation": [],
            "next_steps": []
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

        return recommendations

    def create_final_report(self, startup_data: Dict, competitor_data: Dict, market_data: Dict) -> Dict:
        """Step 4: Combine all insights into final report"""
        final_report = {
            "startup_analysis": startup_data,
            "competitor_landscape": competitor_data,
            "market_insights": market_data,
            "recommendations": self.generate_recommendations(startup_data, competitor_data, market_data)
        }
        
        # Save final report
        self.save_json("complete_analysis.json", final_report)
        return final_report

    def save_json(self, filename: str, data: Any) -> None:
        """Helper to save JSON files with enhanced serialization"""
        filepath = self.output_dir / filename
        
        def serialize_data(obj):
            """Convert complex objects to JSON-serializable format"""
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif hasattr(obj, 'model_dump'):
                return obj.model_dump()
            elif hasattr(obj, 'dict'):
                return obj.dict()
            elif isinstance(obj, dict):
                return {k: serialize_data(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_data(item) for item in obj]
            return obj

        try:
            # Convert data to JSON-serializable format
            serialized_data = serialize_data(data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serialized_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved {filename}")
        except Exception as e:
            print(f"❌ Error saving {filename}: {e}")
            print(f"🔍 DEBUG: Data type: {type(data)}")

    async def run_pipeline_async(self, startup_data: Dict = None) -> Dict:
        """Run the complete analysis pipeline with parallel execution"""
        try:
            print("🚀 Starting Parallel FoundrScan Analysis Pipeline...")

            # Step 1: Idea Analysis (sequential - needed by others)
            print("\n1️⃣ Analyzing Startup Idea...")
            if startup_data is None:
                startup_data = self.run_idea_analysis()
            if not startup_data:
                raise ValueError("Failed to get startup data from idea analysis")

            # Steps 2 & 3: Run competitor analysis and market research in parallel
            print("\n2️⃣ & 3️⃣ Running Competitor Analysis and Market Research in Parallel...")
            competitor_data, market_data = await self.run_parallel_analysis(startup_data)

            # Step 4: Integration (sequential - needs results from steps 2 & 3)
            print("\n4️⃣ Generating Final Report...")
            final_report = self.create_final_report(
                startup_data,
                competitor_data,
                market_data
            )

            print("\n✨ Analysis Complete! Check the outputs/ directory for results.")
            return final_report

        except Exception as e:
            print(f"❌ Pipeline error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def run_pipeline(self, startup_data: Dict = None) -> Dict:
        """Synchronous wrapper for the async pipeline"""
        return asyncio.run(self.run_pipeline_async(startup_data))

# Alternative: ProcessPoolExecutor version for CPU-intensive tasks
class ProcessParallelFoundrScanPipeline(ParallelFoundrScanPipeline):
    """Version using ProcessPoolExecutor instead of ThreadPoolExecutor"""
    
    async def run_parallel_analysis(self, startup_data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Run competitor analysis and market research in parallel using processes"""
        print("🚀 Starting parallel analysis with ProcessPoolExecutor...")
        
        # Use ProcessPoolExecutor for CPU-bound tasks (better for compute-heavy workloads)
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            loop = asyncio.get_event_loop()
            
            # Create partial functions to pass startup_data
            competitor_func = partial(self._run_competitor_analysis_sync, startup_data)
            market_func = partial(self._run_market_research_sync, startup_data)
            
            competitor_future = loop.run_in_executor(executor, competitor_func)
            market_future = loop.run_in_executor(executor, market_func)
            
            print("⏳ Waiting for both analyses to complete...")
            competitor_data, market_data = await asyncio.gather(
                competitor_future, 
                market_future,
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
            
            print("✅ Both analyses completed!")
            return competitor_data, market_data

if __name__ == "__main__":
    # Use ThreadPoolExecutor version (recommended for I/O bound tasks)
    pipeline = ParallelFoundrScanPipeline()
    results = pipeline.run_pipeline()
    
    # Alternative: Use ProcessPoolExecutor version (for CPU-intensive tasks)
    # pipeline = ProcessParallelFoundrScanPipeline() 
    # results = pipeline.run_pipeline()