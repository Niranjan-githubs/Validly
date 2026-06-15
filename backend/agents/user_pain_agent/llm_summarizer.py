import os
import json
from typing import List, Dict
from langchain_together import ChatTogether
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import concurrent.futures
import re

# Define OUTPUT_DIR for file operations
# OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../outputs')
# if not os.path.exists(OUTPUT_DIR):
#     os.makedirs(OUTPUT_DIR)

# Load environment variables
load_dotenv(dotenv_path="D:/mahaa_v/.env")

class TopComment(BaseModel):
    pain_point: str = Field(description="Short summary of the pain point")
    comment: str = Field(description="The original Reddit comment")
    relevance_score: int = Field(description="1-10, how relevant this pain point is to the startup")
    url: str = Field(description="Reddit URL")
    author: str = Field(description="Reddit author")

def format_comment_for_llm(comment: dict) -> str:
    return (
        f"Comment: {comment.get('comment', '')}\n"
        f"URL: {comment.get('url', '')}\n"
        f"Author: {comment.get('author', '')}\n"
    )

def extract_json_from_response(response):
    # Remove markdown code fences
    response = response.replace('```json', '').replace('```', '').strip()
    # Find the first { and last }
    match = re.search(r'({.*})', response, re.DOTALL)
    if match:
        return match.group(1)
    return response  # fallback

def select_top_comments_with_llm(comments: List[Dict], keyword: str, startup_summary: Dict) -> List[Dict]:
    # Short, direct system prompt
    system_prompt = (
        "You are a focused startup research assistant analyzing Reddit comments for **real, actionable pain points** "
        "based on a specific startup's context.\n\n"
        "Here is the startup summary in JSON:\n"
        f"{json.dumps(startup_summary, ensure_ascii=False)}\n\n"
        "✅ Your job:\n"
        "- ONLY extract pain points that are **directly relevant** to the startup's focus (consider the full JSON summary, not just the title).\n"
        "- If a comment is not relevant to the startup, or is purely positive/supportive, or off-topic → return relevance_score = 1.\n"
        "- If the comment lacks a clear pain point (e.g. joke, meme, praise), return `null` for the full output.\n\n"
        "⛔ DO NOT give your opinion, no explanations, no extra thoughts.\n"
        "✅ STRICTLY return results ONLY in this JSON format:\n"
        "{\n"
        '  "pain_point": "Short 1-sentence summary of the issue",\n'
        '  "comment": "Full original comment",\n'
        '  "relevance_score": Integer 1-10,\n'
        '  "url": "Reddit post URL",\n'
        '  "author": "Reddit username"\n'
        "}\n\n"
        "Note: Relevance score 10 = deeply aligned with the startup’s vision and challenges. Score 1 = not related at all.\n"
        "Return null if the comment is vague, irrelevant, or not a real pain point."
    ).replace('{', '{{').replace('}', '}}')

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Analyze the following Reddit comment and return a JSON object as described.\n\nComment:\n{comment}")
    ])


    class TopCommentShort(BaseModel):
        pain_point: str = Field(description="Short summary of the pain point")
        comment: str = Field(description="The original Reddit comment")
        relevance_score: int = Field(description="1-10, how relevant this pain point is to the startup")
        url: str = Field(description="Reddit URL")
        author: str = Field(description="Reddit author")

    output_parser = JsonOutputParser(pydantic_object=TopCommentShort)

    TOGETHER_API_KEYS = [
        os.environ.get("TOGETHER_API_KEY2"),
        os.environ.get("TOGETHER_API_KEY3"),
        os.environ.get("TOGETHER_API_KEY4"),
        # Add more keys as needed
    ]

    all_top_comments = []
    failed_filter_count = 0
    def process_single_comment(comment):
        nonlocal failed_filter_count
        comment_str = format_comment_for_llm(comment)
        max_retries = len(TOGETHER_API_KEYS)
        for key_index in range(max_retries):
            api_key = TOGETHER_API_KEYS[key_index % len(TOGETHER_API_KEYS)]
            try:
                llm = ChatTogether(
                    together_api_key=api_key,
                    model="meta-llama/Llama-Vision-Free",
                    temperature=0.3,
                    top_p=0.9
                )
                chain = prompt | llm | output_parser
                result = chain.invoke({"comment": comment_str})
                if result is None or (isinstance(result, str) and result.strip().lower() == 'null'):
                    return None
                if isinstance(result, str):
                    clean_result = extract_json_from_response(result)
                    result = json.loads(clean_result)
                for field in ['pain_point', 'comment', 'relevance_score', 'url', 'author']:
                    if field not in result or result[field] is None or (isinstance(result[field], str) and result[field].strip() == ""):
                        result[field] = "" if field in ['pain_point', 'comment', 'url', 'author'] else None
                if result['relevance_score'] is not None:
                    try:
                        result['relevance_score'] = int(result['relevance_score'])
                    except Exception:
                        result['relevance_score'] = None
                if (result.get('relevance_score') or 0) >= 5:
                    return result
                else:
                    failed_filter_count += 1
                    return None
            except Exception as e:
                if ("429" in str(e)) or ("rate limit" in str(e).lower()) or ("model_rate_limit" in str(e)):
                    continue
                print(f"❌ Error processing comment: {e}")
                return None
        print("❌ All API keys exhausted or max retries exceeded for this comment.")
        return None
    step = 2
    for i in range(0, len(comments), step):
        group = comments[i:i+step]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_single_comment, group))
        for res in results:
            if res:
                all_top_comments.append(res)
        if failed_filter_count > 10:
            print(f"❌ More than 10 comments did not pass the filter. Exiting LLM processing early.")
            return all_top_comments
    return all_top_comments

def is_domain_pain_point(comment, keywords):
    text = (comment.get('pain_point') or "") + " " + (comment.get('comment') or "")
    text = text.lower()
    return any(kw.lower() in text for kw in keywords)

# if __name__ == "__main__":
#     # Example usage
#     import argparse
#     parser = argparse.ArgumentParser(description="Summarize Reddit pain points and score relevance to a startup.")
#     parser.add_argument('--comments', type=str, required=True, help='Path to JSON file with Reddit comments')
#     parser.add_argument('--keyword', type=str, required=True, help='Keyword for analysis')
#     parser.add_argument('--startup_summary', type=str, required=True, help='Path to startup summary JSON file')
#     parser.add_argument('--output', type=str, default='pain_points_llm.json', help='Output JSON file for all top comments (append mode)')
#     args = parser.parse_args()

#     # Load data
#     with open(args.comments, 'r', encoding='utf-8') as f:
#         comments = json.load(f)
#     json_path = args.startup_summary
#     startup_summary = load_startup_summary(json_path)

#     # Run LLM summarizer
#     top_comments = select_top_comments_with_llm(comments, args.keyword, startup_summary)