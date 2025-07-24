from together import Together
import os
import json
from dotenv import load_dotenv
load_dotenv()

# Initialize Together client
client = Together()  # API key should be set as TOGETHER_API_KEY environment variable

# Unified query function using Together's LLaMA 3
def query_model(prompt, conversation_history=""):
    system_content = """You're a smart startup assistant helping understand a founder's idea. 
Your job is to:
1. Understand their startup idea.
2. Ask follow-up questions across these categories (if relevant):
   - Technical Details
   - Business Viability
   - Team
   - Traction & Timeline
   - Challenges & Risks
   - Long-term Vision
Only ask one question at a time. Be curious but friendly.
When you think you have all the information, say: '✅ I'm ready to summarize your startup now.'"""
    
    messages = [{"role": "system", "content": system_content}]

    if conversation_history:
        # Split history into lines and alternate between user/assistant roles
        lines = conversation_history.strip().split("\n")
        for line in lines:
            if line.startswith("User:"):
                messages.append({"role": "user", "content": line.replace("User:", "").strip()})
            elif line.startswith("Assistant:") or line.startswith("System:"):
                messages.append({"role": "assistant", "content": line.replace("Assistant:", "").replace("System:", "").strip()})

    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling Together AI: {e}")
        return "I'm sorry, I encountered an error. Please try again."

# Contextual chat loop
def interactive_idea_extractor():
    print("🧠 Tell me your startup idea (ex: AI for diabetes care):")
    user_idea = input("> ").strip()
    
    if not user_idea:
        print("Please provide a startup idea to continue.")
        return None, None
    
    system_prompt = """
You're a smart startup assistant helping understand a founder's idea.
Your job is to:
1. Understand their startup idea.
2. Ask follow-up questions across these categories (if relevant):
   - Technical Details
   - Business Viability
   - Team
   - Traction & Timeline
   - Challenges & Risks
   - Long-term Vision
Only ask one question at a time. Be curious but friendly.
When you think you have all the information, say: '✅ I'm ready to summarize your startup now.'
"""
    
    # Initialize conversation history
    conversation = f"System: {system_prompt}\nUser: My startup idea: {user_idea}\n"
    
    # First response from AI
    response = query_model(f"A user has shared their startup idea: '{user_idea}'. Please respond with your first question to understand their idea better.")
    print(f"\n🤖 {response}")
    conversation += f"Assistant: {response}\n"
    
    # Chat loop
    max_turns = 10  # Prevent infinite loops
    turn_count = 0
    
    while turn_count < max_turns:
        if "✅ I'm ready to summarize" in response:
            break
            
        user_reply = input("💬 You: ").strip()
        if not user_reply:
            continue
            
        conversation += f"User: {user_reply}\n"
        
        response = query_model(
            f"Continue this conversation about the startup idea. Ask one more relevant question or say you're ready to summarize if you have enough information.",
            conversation
        )
        print(f"\n🤖 {response}")
        conversation += f"Assistant: {response}\n"
        turn_count += 1
    
    return user_idea, conversation

# Generate a proper summary from conversation
def summarize_startup(user_idea, conversation):
    summary_prompt = f"""
Based on the following conversation about a startup idea, please create a comprehensive JSON summary:

User's Idea: {user_idea}

Conversation History:
{conversation}

Please analyze all the information gathered and create a JSON summary with this exact structure:

{{
  "title": "One-line Title",
  "description": "A clear explanation of the startup idea",
  "target_users": ["user type 1", "user type 2"],
  "problem": "The problem being solved",
  "solution": "How the startup solves the problem",
  "tech_stack": ["technology 1", "technology 2"],
  "business_model": "How the business operates",
  "monetization": "How the business makes money",
  "competition": "Key competitors or alternatives",
  "differentiator": "What makes this startup unique",
  "risks": ["risk 1", "risk 2"],
  "vision": "Long-term vision for the company"
}}

Only output the JSON, no additional text.
"""

    response = query_model(summary_prompt)
    
    # Try to extract and validate JSON
    try:
        # Try to extract JSON from response
        if "```json" in response:
            json_part = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_part = response.split("```")[1].split("```")[0].strip()
        else:
            json_part = response.strip()
        
        # Validate JSON
        parsed_json = json.loads(json_part)
        return parsed_json
    except json.JSONDecodeError:
        print("Warning: Could not parse JSON response. Returning raw response.")
        return {"raw_response": response}

# Main run
if __name__ == "__main__":
    try:
        idea, conversation = interactive_idea_extractor()
        if idea and conversation:
            print("\n📦 Generating your startup summary...\n")
            summary = summarize_startup(idea, conversation)
            
            # Pretty print the summary
            if isinstance(summary, dict) and "raw_response" not in summary:
                print(json.dumps(summary, indent=2))
            else:
                print(summary)
        else:
            print("No startup idea provided. Exiting.")
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"An error occurred: {e}")