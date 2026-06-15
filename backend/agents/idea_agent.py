from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import json
import logging
from pathlib import Path
import os
from together import Together
from dotenv import load_dotenv
import re
import asyncio
import aiohttp
import pyaudio
from deepgram import Deepgram
from gtts import gTTS
import tempfile
import pygame
import io
import random
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../utils')))
from utils import info_tracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Audio parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Initialize pygame for audio playback
pygame.mixer.init()

@dataclass
class StartupSummary:
    title: str
    description: str
    target_users: List[str]
    problem: str
    solution: str
    tech_stack: List[str]
    business_model: str
    monetization: str
    competition: str
    differentiator: str
    scale: str
    risks: List[str]
    vision: str

    def to_dict(self) -> Dict:
        """Convert the summary to a dictionary"""
        return {
            "title": self.title,
            "description": self.description,
            "target_users": self.target_users,
            "problem": self.problem,
            "solution": self.solution,
            "tech_stack": self.tech_stack,
            "business_model": self.business_model,
            "monetization": self.monetization,
            "competition": self.competition,
            "differentiator": self.differentiator,
            "scale": self.scale,
            "risks": self.risks,
            "vision": self.vision
        }

    def to_json(self) -> str:
        """Convert the summary to a JSON string"""
        return json.dumps(self.to_dict(), indent=2)

class ConversationTracker:
    """Tracks conversation progress and generates contextual responses"""
    
    def __init__(self):
        self.info_gathered = {
            'concept': False,
            'target_users': False,
            'problem': False,
            'solution': False,
            'business_model': False,
            'monetization': False,
            'competition': False,
            'differentiator': False,
            'tech_requirements': False,
            'risks': False,
            'vision': False
        }
        
        self.conversation_flow = [
            'concept',
            'target_users', 
            'problem',
            'solution',
            'business_model',
            'monetization',
            'competition',
            'differentiator',
            'tech_requirements',
            'vision'
        ]
        
        self.current_focus = 'concept'
        self.turn_count = 0
        
    def analyze_user_response(self, response: str) -> List[str]:
        """Analyze user response to identify what information was provided"""
        response_lower = response.lower()
        topics_covered = []
        
        # Concept/Idea indicators
        if any(word in response_lower for word in ['app', 'platform', 'service', 'product', 'tool', 'system']):
            topics_covered.append('concept')
            
        # Target users indicators
        if any(word in response_lower for word in ['users', 'customers', 'people', 'patients', 'students', 'professionals', 'businesses']):
            topics_covered.append('target_users')
            
        # Problem indicators
        if any(word in response_lower for word in ['problem', 'issue', 'challenge', 'pain', 'difficult', 'struggle', 'need']):
            topics_covered.append('problem')
            
        # Solution indicators
        if any(word in response_lower for word in ['solution', 'solve', 'help', 'feature', 'functionality', 'algorithm', 'ai', 'ml']):
            topics_covered.append('solution')
            
        # Business model indicators
        if any(word in response_lower for word in ['business', 'model', 'approach', 'strategy', 'marketplace', 'b2b', 'b2c']):
            topics_covered.append('business_model')
            
        # Monetization indicators
        if any(word in response_lower for word in ['money', 'revenue', 'commission', 'subscription', 'fee', 'pricing', 'charge']):
            topics_covered.append('monetization')
            
        # Competition indicators
        if any(word in response_lower for word in ['competitor', 'competition', 'existing', 'alternative', 'similar', 'different']):
            topics_covered.append('competition')
            
        # Differentiator indicators
        if any(word in response_lower for word in ['unique', 'different', 'better', 'advantage', 'special', 'innovation']):
            topics_covered.append('differentiator')
            
        # Tech requirements indicators
        if any(word in response_lower for word in ['tech', 'technology', 'mobile', 'web', 'api', 'database', 'verification', 'integration']):
            topics_covered.append('tech_requirements')
            
        # Vision indicators
        if any(word in response_lower for word in ['vision', 'future', 'plan', 'goal', 'expand', 'scale', 'growth']):
            topics_covered.append('vision')
            
        return topics_covered

    def update_progress(self, user_response: str):
        """Update conversation progress based on user response"""
        topics_covered = self.analyze_user_response(user_response)
        
        for topic in topics_covered:
            if topic in self.info_gathered:
                self.info_gathered[topic] = True
                
        self.turn_count += 1

    def get_next_focus(self) -> str:
        """Determine what topic to focus on next"""
        # Find the first uncovered topic in our flow
        for topic in self.conversation_flow:
            if not self.info_gathered.get(topic, False):
                return topic
        
        # If all main topics covered, we're ready to summarize
        return 'summary'

    def generate_contextual_response(self, user_response: str, previous_context: str = "") -> str:
        """Generate a contextual response based on conversation state"""
        
        self.update_progress(user_response)
        next_focus = self.get_next_focus()
        
        if next_focus == 'summary':
            return "That's comprehensive! ✅ I have enough information to create your startup summary."
        
        # Contextual acknowledgments and transitions
        acknowledgments = {
            'concept': ["That's an interesting concept!", "Great idea!", "Interesting approach!"],
            'target_users': ["That's a specific target market.", "Good to have a clear user base.", "Makes sense!"],
            'problem': ["That's definitely a real problem.", "I can see how that would be frustrating.", "Important issue to solve."],
            'solution': ["That's a smart solution!", "Clever approach!", "That could work well!"],
            'business_model': ["Solid business model!", "That makes business sense.", "Good strategy!"],
            'monetization': ["Smart revenue approach!", "That's a viable monetization strategy.", "Good way to generate revenue!"],
            'competition': ["That differentiation is key!", "Good competitive positioning.", "Important to understand the landscape."],
            'tech_requirements': ["That's a great approach to quality control.", "Smart technical consideration!", "Good planning!"]
        }
        
        # Generate acknowledgment for what they just shared
        topics_just_covered = self.analyze_user_response(user_response)
        acknowledgment = ""
        if topics_just_covered:
            topic = topics_just_covered[0]  # Use first topic covered
            if topic in acknowledgments:
                acknowledgment = random.choice(acknowledgments[topic]) + "\n\n"
        
        # Generate next question based on focus area
        questions = {
            'target_users': [
                "Who specifically would use this?",
                "What's your target user demographic?",
                "Who's your ideal customer?"
            ],
            'problem': [
                "What specific problem does this solve for them?",
                "What pain point are you addressing?",
                "What challenge do they currently face?"
            ],
            'solution': [
                "How exactly does your solution work?",
                "What's your approach to solving this?",
                "Can you walk me through the solution?"
            ],
            'business_model': [
                "What's your business model?",
                "How do you plan to structure this business?",
                "Is this B2B, B2C, or marketplace?"
            ],
            'monetization': [
                "How do you plan to make money from this?",
                "What's your revenue strategy?",
                "How will you monetize this?"
            ],
            'competition': [
                "What's your competition like?",
                "How does this compare to existing solutions?",
                "Who else is in this space?"
            ],
            'differentiator': [
                "What makes this different from competitors?",
                "What's your unique advantage?",
                "How do you stand out?"
            ],
            'tech_requirements': [
                "What technical requirements do you have?",
                "Any specific technology considerations?",
                "How do you plan to handle the technical side?"
            ],
            'vision': [
                "What's your long-term vision?",
                "Where do you see this in 5 years?",
                "What are your growth plans?"
            ]
        }
        
        # Add topic prefix for better organization
        topic_prefixes = {
            'target_users': "Target Market:",
            'problem': "Problem Definition:",
            'solution': "Solution Details:",
            'business_model': "Business Model:",
            'monetization': "Revenue Strategy:",
            'competition': "Competitive Analysis:",
            'differentiator': "Differentiation:",
            'tech_requirements': "Technical Details:",
            'vision': "Vision & Growth:"
        }
        
        if next_focus in questions:
            prefix = topic_prefixes.get(next_focus, "")
            question = random.choice(questions[next_focus])
            
            if prefix:
                return f"{acknowledgment}{prefix} {question}"
            else:
                return f"{acknowledgment}{question}"
        
        return f"{acknowledgment}Tell me more about that."

class StartupIdeaAnalyzer:
    """Main class for analyzing startup ideas using AI"""

    def __init__(self):
        """Initialize the analyzer with Together AI client and audio capabilities"""
        try:
            load_dotenv(override=True)
            together_api_key = os.getenv("TOGETHER_API_KEY")
            self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
            
            if not together_api_key:
                raise ValueError("TOGETHER_API_KEY environment variable is not set")
            if not self.deepgram_api_key:
                raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
                
            self.client = Together(api_key=together_api_key)
            self.audio = pyaudio.PyAudio()
            
            # Initialize conversation tracker
            self.tracker = ConversationTracker()
            
            logger.info("Successfully initialized Together AI client and audio capabilities")
            
        except Exception as e:
            logger.error(f"Failed to initialize: {str(e)}")
            raise

    def _get_system_prompt(self) -> str:
        """System prompt for natural conversation"""
        return """You are a friendly startup mentor having a natural conversation. 

Your goal is to understand their startup idea through natural dialogue and gather key information about:
- Target users and market
- Problem being solved  
- Solution approach
- Business model
- Revenue strategy
- Competition
- Key differentiators
- Technical requirements
- Vision and growth plans

Rules:
1. Be conversational and natural - like chatting with a friend
2. Acknowledge what they share before asking the next question
3. Ask ONE focused question at a time
4. Use natural transitions and reactions
5. When you have comprehensive information, say "✅ I have enough information to create your startup summary"

Be engaging, supportive, and genuinely curious about their idea!"""

    def query_model(self, prompt: str, conversation: Optional[list] = None) -> str:
        """Query the AI model with improved conversation handling"""
        try:
            full_prompt = prompt
            if conversation:
                # Convert conversation array to string format for the model
                convo_str = "\n".join(
                    f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation if msg['role'] != 'system'
                )
                full_prompt = f"{convo_str}\n\n{prompt}"

            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=512,
                stop=["\n\nUser:", "\n\nAssistant:"]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Together AI query failed: {str(e)}")
            return "Tell me more about your startup idea!"

    def check_info_completion(self, conversation: list) -> tuple[bool, dict]:
        """Check if enough info is present in the conversation using info_tracker util."""
        # Extract only user/assistant messages
        messages = [msg['content'] for msg in conversation if msg['role'] in ('user', 'assistant')]
        info, is_done = info_tracker.extract_startup_info(messages)
        return is_done, info

    def chat_step(self, conversation: str, user_message: str) -> Tuple[str, str, bool]:
        """Enhanced chat step with conversation tracking"""
        
        # Add user message to conversation
        conversation += f"\n💬 You: {user_message}\n"
        
        # Use conversation tracker for more natural responses
        response = self.tracker.generate_contextual_response(user_message, conversation)
        
        # Check if ready to summarize (rule-based)
        # Parse conversation into list of dicts
        convo_list = []
        for line in conversation.split('\n'):
            if line.startswith('💬 You:'):
                convo_list.append({'role': 'user', 'content': line.replace('💬 You:', '').strip()})
            elif line.startswith('🤖'):
                convo_list.append({'role': 'assistant', 'content': line.replace('🤖', '').strip()})
        is_done, _ = self.check_info_completion(convo_list)
        
        # Add assistant response with emoji
        conversation += f"🤖 {response}\n"
        
        return response, conversation, is_done

    def interactive_session(self) -> Tuple[str, str]:
        """Interactive session with improved flow"""
        try:
            print("🚀 Startup Idea Validator")
            print("=" * 50)
            print("Tell me about your startup idea - we'll discuss it together and validate the concept!\n")
            
            user_input = input("💬 You: ").strip()
            if not user_input:  # Voice input fallback
                user_idea = asyncio.run(self.transcribe_live())
            else:
                user_idea = user_input
            
            # Reset tracker for new session
            self.tracker = ConversationTracker()
            
            # Initialize conversation
            conversation = f"💬 You: {user_idea}\n"
            
            # Generate first response
            response = self.tracker.generate_contextual_response(user_idea)
            print(f"🤖 {response}")
            
            # Optional: Text-to-speech
            if hasattr(self, 'speak_response'):
                self.speak_response(response)
            
            conversation += f"🤖 {response}\n"
            
            # Continue conversation until ready
            while True:
                user_input = input("💬 You: ").strip()
                if not user_input:
                    user_reply = asyncio.run(self.transcribe_live())
                else:
                    user_reply = user_input
                
                response, conversation, is_done = self.chat_step(conversation, user_reply)
                print(f"🤖 {response}")
                
                if hasattr(self, 'speak_response'):
                    self.speak_response(response)
                    
                if is_done:
                    print("✅ Enough information gathered for summary (rule-based).\n")
                    break
            
            return user_idea, conversation

        except KeyboardInterrupt:
            logger.info("Session interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Error in interactive session: {str(e)}")
            raise

    def generate_summary(self, user_idea: str, conversation: list) -> StartupSummary:
        """Generate a structured summary of the startup idea"""
        try:
            # Convert conversation array to string format for the prompt
            convo_str = "\n".join(
                f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation if msg['role'] != 'system'
            )
            prompt = f"""Based on this startup idea conversation, create a comprehensive structured summary in JSON format:

Original Idea: {user_idea}

Full Conversation:
{convo_str}

Generate a complete startup analysis with these exact fields:
{{
  "title": "Concise startup name/title",
  "description": "Clear 2-3 sentence description",
  "target_users": ["specific user type 1", "user type 2"],
  "problem": "Clear problem statement",
  "solution": "Detailed solution approach",
  "tech_stack": ["technology 1", "technology 2", "technology 3"],
  "business_model": "Business model description",
  "monetization": "Revenue generation strategy",
  "competition": "Competitive landscape analysis",
  "differentiator": "Key competitive advantages",
  "scale": "Scalability approach and growth strategy",
  "risks": ["risk 1", "risk 2", "risk 3"],
  "vision": "Long-term vision and goals"
}}

Return ONLY the JSON object, no additional text."""

            response = self.query_model(prompt)
            
            # Clean up JSON response
            json_str = response.strip()
            
            # Remove markdown formatting
            if "```" in json_str:
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                else:
                    json_str = json_str.split("```")[1].split("```")[0].strip()
            
            # Additional cleanup
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*]', ']', json_str)
            
            try:
                summary_dict = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {str(e)}")
                logger.error(f"Raw response: {json_str}")
                
                # Create fallback summary
                summary_dict = {
                    "title": user_idea,
                    "description": "Generated from conversation analysis",
                    "target_users": [],
                    "problem": "",
                    "solution": "",
                    "tech_stack": [],
                    "business_model": "",
                    "monetization": "",
                    "competition": "",
                    "differentiator": "",
                    "scale": "",
                    "risks": [],
                    "vision": ""
                }
            
            # Ensure all required fields exist
            required_fields = [
                "title", "description", "target_users", "problem", "solution",
                "tech_stack", "business_model", "monetization", "competition",
                "differentiator", "scale", "risks", "vision"
            ]
            
            for field in required_fields:
                if field not in summary_dict:
                    summary_dict[field] = [] if field in ["target_users", "tech_stack", "risks"] else ""
                
                # Ensure list fields are lists
                if field in ["target_users", "tech_stack", "risks"] and not isinstance(summary_dict[field], list):
                    summary_dict[field] = [str(summary_dict[field])] if summary_dict[field] else []

            return StartupSummary(**summary_dict)

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return StartupSummary(
                title=user_idea,
                description="Analysis could not be completed",
                target_users=[],
                problem="",
                solution="",
                tech_stack=[],
                business_model="",
                monetization="",
                competition="",
                differentiator="",
                scale="",
                risks=[],
                vision=""
            )

    def __del__(self):
        """Cleanup audio resources"""
        try:
            self.audio.terminate()
            pygame.mixer.quit()
        except:
            pass

def main():
    """Main entry point for the startup idea analyzer"""
    try:
        analyzer = StartupIdeaAnalyzer()
        idea, conversation = analyzer.interactive_session()
        
        print("\n" + "="*50)
        print("📦 Generating Your Startup Summary...")
        print("="*50)
        
        summary = analyzer.generate_summary(idea, conversation)
        
        # Print formatted summary
        print("\n🎯 STARTUP SUMMARY")
        print("="*50)
        print(summary.to_json())
        
        # Save to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "startup_summary.json", "w") as f:
            json.dump(summary.to_dict(), f, indent=2)
            
        print(f"\n💾 Summary saved to output/startup_summary.json")
        logger.info("Summary saved successfully")

    except KeyboardInterrupt:
        print("\n\n👋 Session terminated by user. Thanks for using Startup Idea Validator!")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"\n❌ An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()