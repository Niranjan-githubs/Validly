import json
import os
import time
import contextlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup

# Remove local file imports and replace with cloud-ready alternatives
try:
    from tavily import TavilyClient
except ImportError:
    print("⚠️ Tavily not installed. Install with: pip install tavily-python")
    TavilyClient = None

# Cloud-ready imports
try:
    import praw  # Reddit API
except ImportError:
    print("⚠️ PRAW not installed. Install with: pip install praw")
    praw = None

class CloudRedditScraper:
    """Cloud-ready Reddit scraper with no local file dependencies"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.session_data = {}  # In-memory storage
        
    def get_env_keys(self, prefix: str) -> List[str]:
        """Get multiple API keys from environment variables"""
        keys = []
        idx = 1
        while True:
            key = os.environ.get(f"{prefix}{idx}")
            if key:
                keys.append(key)
                idx += 1
            else:
                break
        return keys

    def tavily_search(self, query: str, num_results: int = 10) -> List[str]:
        """Search Reddit URLs using Tavily API"""
        if not TavilyClient:
            print("❌ Tavily not available. Using fallback search...")
            return self.fallback_reddit_search(query)
            
        tavily_keys = self.get_env_keys("TAVILY_API_KEY")
        if not tavily_keys:
            print("⚠️ No Tavily API keys found. Using fallback search...")
            return self.fallback_reddit_search(query)
            
        for t_idx, tavily_key in enumerate(tavily_keys):
            try:
                client = TavilyClient(api_key=tavily_key)
                response = client.search(query=query, max_results=num_results)
                reddit_urls = [
                    item['url'] for item in response.get('results', []) 
                    if 'reddit.com/r/' in item['url']
                ]
                print(f"✅ Found {len(reddit_urls)} Reddit URLs via Tavily")
                return reddit_urls
            except Exception as e:
                if "usage limit" in str(e).lower() or "rate limit" in str(e).lower():
                    print(f"⚠️ Tavily key {t_idx+1} rate limited. Trying next key...")
                    continue
                print(f"❌ Error during Tavily search: {e}")
        
        print("🔄 All Tavily keys exhausted. Using fallback search...")
        return self.fallback_reddit_search(query)

    def fallback_reddit_search(self, query: str) -> List[str]:
        """Fallback search method when Tavily is unavailable"""
        try:
            # Use Google search as fallback
            search_query = f"site:reddit.com {query}"
            # This is a simplified fallback - in production, use a proper search API
            fallback_urls = [
                f"https://www.reddit.com/r/startups/search/?q={query.replace(' ', '+')}&restrict_sr=1",
                f"https://www.reddit.com/r/entrepreneur/search/?q={query.replace(' ', '+')}&restrict_sr=1",
                f"https://www.reddit.com/r/smallbusiness/search/?q={query.replace(' ', '+')}&restrict_sr=1",
            ]
            print(f"🔄 Using {len(fallback_urls)} fallback Reddit URLs")
            return fallback_urls
        except Exception as e:
            print(f"❌ Fallback search failed: {e}")
            return []

    def reddit_api_search(self, startup_data: Dict) -> List[Dict]:
        """Use Reddit API for direct access (preferred method)"""
        if not praw:
            print("⚠️ Reddit API not available (praw not installed)")
            return []
            
        try:
            reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
            reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'startup_analysis_bot/1.0')
            
            if not reddit_client_id or not reddit_client_secret:
                print("⚠️ Reddit API credentials not found in environment")
                return []
                
            reddit = praw.Reddit(
                client_id=reddit_client_id,
                client_secret=reddit_client_secret,
                user_agent=reddit_user_agent
            )
            
            # Extract keywords from startup data
            domain_keywords = self.extract_domain_keywords(startup_data)
            pain_points = []
            
            # Search relevant subreddits
            relevant_subreddits = [
                'startups', 'entrepreneur', 'smallbusiness', 'business',
                'SaaS', 'technology', 'productivity', 'customer_service'
            ]
            
            for subreddit_name in relevant_subreddits:
                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    for keyword in domain_keywords[:3]:  # Limit to top 3 keywords
                        submissions = subreddit.search(keyword, limit=20, time_filter='year')
                        
                        for submission in submissions:
                            try:
                                submission.comments.replace_more(limit=0)
                                for comment in submission.comments.list()[:10]:  # Top 10 comments
                                    if len(comment.body) > 50 and comment.score > 1:
                                        pain_point = {
                                            'url': f"https://reddit.com{comment.permalink}",
                                            'author': str(comment.author) if comment.author else 'unknown',
                                            'comment': comment.body,
                                            'score': comment.score,
                                            'subreddit': subreddit_name,
                                            'submission_title': submission.title
                                        }
                                        pain_points.append(pain_point)
                                        
                                        if len(pain_points) >= 50:  # Limit total results
                                            return pain_points
                            except Exception as e:
                                print(f"⚠️ Error processing submission: {e}")
                                continue
                                
                except Exception as e:
                    print(f"⚠️ Error accessing subreddit {subreddit_name}: {e}")
                    continue
                    
            print(f"✅ Collected {len(pain_points)} comments via Reddit API")
            return pain_points
            
        except Exception as e:
            print(f"❌ Reddit API search failed: {e}")
            return []

    def cloud_browser_scrape(self, url: str) -> List[Dict]:
        """Use cloud browser service for scraping"""
        browserless_key = os.getenv('BROWSERLESS_API_KEY')
        scrapingbee_key = os.getenv('SCRAPINGBEE_API_KEY')
        
        # Try Browserless.io first
        if browserless_key:
            try:
                return self.scrape_with_browserless(url, browserless_key)
            except Exception as e:
                print(f"⚠️ Browserless failed: {e}")
        
        # Try ScrapingBee as fallback
        if scrapingbee_key:
            try:
                return self.scrape_with_scrapingbee(url, scrapingbee_key)
            except Exception as e:
                print(f"⚠️ ScrapingBee failed: {e}")
        
        # Final fallback: direct HTTP request
        return self.direct_http_scrape(url)

    def scrape_with_browserless(self, url: str, api_key: str) -> List[Dict]:
        """Scrape using Browserless.io cloud service"""
        try:
            response = requests.post(
                f'https://chrome.browserless.io/scrape?token={api_key}',
                json={
                    'url': url,
                    'elements': [{
                        'selector': '[data-testid="comment"]',
                        'timeout': 10000
                    }]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                comments = []
                
                for element in data.get('data', []):
                    try:
                        # Parse the scraped HTML
                        soup = BeautifulSoup(element.get('html', ''), 'html.parser')
                        comment_text = soup.get_text(strip=True)
                        
                        if len(comment_text) > 30:  # Filter out short comments
                            comments.append({
                                'url': url,
                                'author': 'reddit_user',  # Browserless might not capture username
                                'comment': comment_text
                            })
                    except Exception as e:
                        print(f"⚠️ Error parsing browserless result: {e}")
                        continue
                
                print(f"✅ Scraped {len(comments)} comments via Browserless")
                return comments
                
        except Exception as e:
            print(f"❌ Browserless scraping failed: {e}")
            raise

    def scrape_with_scrapingbee(self, url: str, api_key: str) -> List[Dict]:
        """Scrape using ScrapingBee cloud service"""
        try:
            response = requests.get(
                'https://app.scrapingbee.com/api/v1/',
                params={
                    'api_key': api_key,
                    'url': url,
                    'render_js': 'true',
                    'wait': 3000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                comments = []
                
                # Look for Reddit comment patterns
                comment_elements = soup.find_all(['div', 'p'], string=lambda text: text and len(text) > 50)
                
                for element in comment_elements[:20]:  # Limit results
                    comment_text = element.get_text(strip=True)
                    comments.append({
                        'url': url,
                        'author': 'reddit_user',
                        'comment': comment_text
                    })
                
                print(f"✅ Scraped {len(comments)} comments via ScrapingBee")
                return comments
                
        except Exception as e:
            print(f"❌ ScrapingBee scraping failed: {e}")
            raise

    def direct_http_scrape(self, url: str) -> List[Dict]:
        """Direct HTTP scraping as final fallback"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                comments = []
                
                # Try to find comment-like content
                text_elements = soup.find_all(['p', 'div'], string=lambda text: text and len(text) > 30)
                
                for element in text_elements[:10]:  # Limit results
                    text = element.get_text(strip=True)
                    if 'comment' in text.lower() or len(text) > 100:
                        comments.append({
                            'url': url,
                            'author': 'reddit_user',
                            'comment': text[:500]  # Truncate long comments
                        })
                
                print(f"✅ Direct scraped {len(comments)} potential comments")
                return comments
                
        except Exception as e:
            print(f"❌ Direct HTTP scraping failed: {e}")
            return []

    def extract_domain_keywords(self, startup_data: Dict) -> List[str]:
        """Extract relevant keywords from startup data"""
        keywords = []
        
        # Get from startup data
        if isinstance(startup_data, dict):
            keywords.extend(startup_data.get('keywords', []))
            
            # Extract from title and description
            title = startup_data.get('title', '')
            description = startup_data.get('description', '')
            problem = startup_data.get('problem', '')
            
            # Simple keyword extraction
            text_to_analyze = f"{title} {description} {problem}".lower()
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'a', 'an'}
            
            words = [word.strip('.,!?()[]{}') for word in text_to_analyze.split()]
            keywords.extend([word for word in words if len(word) > 3 and word not in common_words])
        
        # Use domain info if available
        try:
            # This would normally come from the domain agent
            domain_info = self.get_domain_info(startup_data)
            if domain_info:
                keywords.extend([domain_info.get('domain_search', ''), domain_info.get('major_domain', '')])
        except Exception:
            pass
        
        # Remove duplicates and empty strings
        unique_keywords = list(set([k for k in keywords if k and len(k) > 2]))
        return unique_keywords[:10]  # Limit to top 10 keywords

    def get_domain_info(self, startup_data: Dict) -> Dict:
        """Get domain information (placeholder for domain agent)"""
        try:
            # This would normally call the domain agent
            # For now, return a basic domain classification
            title = startup_data.get('title', '').lower()
            description = startup_data.get('description', '').lower()
            
            if any(word in f"{title} {description}" for word in ['saas', 'software', 'app', 'platform']):
                return {'domain_search': 'software', 'major_domain': 'technology'}
            elif any(word in f"{title} {description}" for word in ['ecommerce', 'marketplace', 'shopping']):
                return {'domain_search': 'ecommerce', 'major_domain': 'retail'}
            elif any(word in f"{title} {description}" for word in ['health', 'medical', 'wellness']):
                return {'domain_search': 'healthcare', 'major_domain': 'health'}
            else:
                return {'domain_search': 'business', 'major_domain': 'general'}
        except Exception:
            return {'domain_search': 'business', 'major_domain': 'general'}

    async def process_comment_with_llm(self, comment: Dict, startup_data: Dict) -> Optional[Dict]:
        """Process comment through LLM to determine relevance"""
        try:
            # This would normally call the LLM summarizer
            # For now, implement basic relevance checking
            comment_text = comment.get('comment', '').lower()
            
            # Check for pain point indicators
            pain_indicators = [
                'frustrated', 'annoying', 'problem', 'issue', 'difficult', 'hard',
                'hate', 'worst', 'terrible', 'awful', 'sucks', 'broken',
                'wish there was', 'need something', 'looking for', 'cant find'
            ]
            
            # Check for domain relevance
            domain_keywords = self.extract_domain_keywords(startup_data)
            
            has_pain_indicator = any(indicator in comment_text for indicator in pain_indicators)
            has_domain_relevance = any(keyword.lower() in comment_text for keyword in domain_keywords)
            
            if has_pain_indicator and (has_domain_relevance or len(comment_text) > 100):
                return {
                    **comment,
                    'relevance_score': (has_pain_indicator * 0.5) + (has_domain_relevance * 0.5),
                    'pain_indicators': [indicator for indicator in pain_indicators if indicator in comment_text]
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error processing comment with LLM: {e}")
            return None

    async def run_user_pain_agent(self, startup_data: Dict) -> List[Dict]:
        """Main function to extract user pain points"""
        print("😣 Starting cloud-ready user pain analysis...")
        
        if not startup_data:
            print("⚠️ No startup data provided")
            return []
        
        try:
            pain_points = []
            
            # Method 1: Try Reddit API first (preferred)
            print("🔍 Trying Reddit API...")
            api_comments = self.reddit_api_search(startup_data)
            
            if api_comments:
                print(f"✅ Found {len(api_comments)} comments via Reddit API")
                # Process through LLM filter
                for comment in api_comments[:20]:  # Limit processing
                    processed = await self.process_comment_with_llm(comment, startup_data)
                    if processed:
                        pain_points.append(processed)
                        if len(pain_points) >= 7:  # Target: 7 high-quality pain points
                            break
            
            # Method 2: If API didn't yield enough results, try web scraping
            if len(pain_points) < 5:
                print("🕸️ Supplementing with web scraping...")
                domain_keywords = self.extract_domain_keywords(startup_data)
                query = f"site:reddit.com {' '.join(domain_keywords[:3])} users worst experience"
                
                urls = self.tavily_search(query, num_results=5)
                
                # Process URLs in parallel
                with ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_url = {
                        executor.submit(self.cloud_browser_scrape, url): url 
                        for url in urls[:3]  # Limit concurrent requests
                    }
                    
                    for future in as_completed(future_to_url):
                        try:
                            scraped_comments = future.result()
                            for comment in scraped_comments:
                                processed = await self.process_comment_with_llm(comment, startup_data)
                                if processed:
                                    pain_points.append(processed)
                                    if len(pain_points) >= 7:
                                        break
                        except Exception as e:
                            print(f"⚠️ Error processing scraped URL: {e}")
                            continue
                        
                        if len(pain_points) >= 7:
                            break
            
            # Sort by relevance score if available
            pain_points.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            print(f"✅ User pain analysis complete - found {len(pain_points)} relevant pain points")
            return pain_points[:7]  # Return top 7
            
        except Exception as e:
            print(f"❌ Error in user pain analysis: {e}")
            return []

def run_user_pain_agent(startup_data: Dict) -> List[Dict]:
    """Synchronous wrapper for the async pain agent"""
    scraper = CloudRedditScraper()
    return asyncio.run(scraper.run_user_pain_agent(startup_data))

# Backward compatibility
if __name__ == "__main__":
    # Test with sample data
    sample_startup = {
        "title": "AI-powered productivity tool",
        "description": "Helps remote workers stay focused and organized",
        "keywords": ["productivity", "remote work", "AI"],
        "problem": "Remote workers struggle with time management and focus"
    }
    
    results = run_user_pain_agent(sample_startup)
    print(f"\n🎯 Found {len(results)} pain points:")
    for i, pain_point in enumerate(results, 1):
        print(f"{i}. {pain_point.get('comment', '')[:100]}...")