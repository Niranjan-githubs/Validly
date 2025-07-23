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

def select_top_comments_with_llm(comments: List[Dict], keyword: str, startup_summary: Dict, filename: str = "pain_points_llm.json") -> List[Dict]:
    # Short, direct system prompt
    system_prompt = (
        "You are an assistant that analyzes Reddit comments for actionable pain points relevant to this startup.\n"
        "Startup: " + (startup_summary.get('title', '') or '') + "\n"
        "For each comment, return a JSON with these fields (all required):\n"
        "- pain_point: Short summary of the pain point (1 sentence)\n"
        "- comment: The original Reddit comment\n"
        "- relevance_score: Integer 1-10 (10 = highly relevant, 1 = not relevant). Provide the relevant score = 1 when the comment is positive and supportive to the domain. \n"
        "- url: Reddit URL\n"
        "- author: Reddit author\n"
        "If the comment is not a real pain point or not relevant, return null."
    )
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
                # Re-instantiate the LLM with the current key
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
                # Fill missing fields
                for field in ['pain_point', 'comment', 'relevance_score', 'url', 'author']:
                    if field not in result or result[field] is None or (isinstance(result[field], str) and result[field].strip() == ""):
                        result[field] = "" if field in ['pain_point', 'comment', 'url', 'author'] else None
                # Ensure relevance_score is int
                if result['relevance_score'] is not None:
                    try:
                        result['relevance_score'] = int(result['relevance_score'])
                    except Exception:
                        result['relevance_score'] = None
                # Save if passes filter
                if (result.get('relevance_score') or 0) >= 5:
                    save_single_comment_append(result, startup_summary.get('keywords', []), filename=filename)
                    return result
                else:
                    failed_filter_count += 1
                    return None
            except Exception as e:
                if ("429" in str(e)) or ("rate limit" in str(e).lower()) or ("model_rate_limit" in str(e)):
                    continue  # Try next key
                print(f"❌ Error processing comment: {e}")
                return None
        print("❌ All API keys exhausted or max retries exceeded for this comment.")
        return None
    # Process all comments in parallel (small batches)
    step = 2
    for i in range(0, len(comments), step):
        group = comments[i:i+step]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_single_comment, group))
        for res in results:
            if res:
                all_top_comments.append(res)
                # Check if we've reached 10 valid comments in the output file
                try:
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        current_comments = json.load(f)
                        if isinstance(current_comments, list) and len(current_comments) >= 10:
                            print(f"✅ Reached 10 valid comments in {filename}. Stopping early.")
                            return all_top_comments
                except Exception:
                    pass
        # If failed filter count exceeds 10, exit early
        if failed_filter_count > 10:
            print(f"❌ More than 10 comments did not pass the filter. Exiting LLM processing early.")
            return all_top_comments
    return all_top_comments

def is_domain_pain_point(comment, keywords):
    text = (comment.get('pain_point') or "") + " " + (comment.get('comment') or "")
    text = text.lower()
    return any(kw.lower() in text for kw in keywords)

def save_single_comment_append(comment: dict, keywords: list, filename: str = "pain_points_llm.json"):
    if (comment.get('relevance_score') or 0) >= 5:
        # Load existing comments if file exists
        try:
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                existing_comments = existing if isinstance(existing, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            existing_comments = []
        # Avoid duplicates by comment URL
        existing_urls = set(c.get('url') for c in existing_comments)
        if comment.get('url') not in existing_urls:
            existing_comments.append(comment)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_comments, f, indent=2, ensure_ascii=False)
            print(f"✅ Appended 1 new LLM top comment to {filepath} (total: {len(existing_comments)})")
        else:
            print(f"[INFO] Comment already exists in {filepath}, skipping append.")
    else:
        print(f"[INFO] Comment did not pass filter, not saving.")

def load_startup_summary(json_path: str) -> dict:
    """Load the startup summary from a JSON file path."""
    filepath = os.path.join(OUTPUT_DIR, json_path) if not os.path.isabs(json_path) else json_path
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    # Example usage
    import argparse
    parser = argparse.ArgumentParser(description="Summarize Reddit pain points and score relevance to a startup.")
    parser.add_argument('--comments', type=str, required=True, help='Path to JSON file with Reddit comments')
    parser.add_argument('--keyword', type=str, required=True, help='Keyword for analysis')
    parser.add_argument('--startup_summary', type=str, required=True, help='Path to startup summary JSON file')
    parser.add_argument('--output', type=str, default='pain_points_llm.json', help='Output JSON file for all top comments (append mode)')
    args = parser.parse_args()

    # Load data
    with open(args.comments, 'r', encoding='utf-8') as f:
        comments = json.load(f)
    json_path = args.startup_summary
    startup_summary = load_startup_summary(json_path)

    # Run LLM summarizer
    top_comments = select_top_comments_with_llm(comments, args.keyword, startup_summary, filename=args.output)
    # The original code had save_all_top_comments_append(top_comments, filename=args.output)
    # This function is not defined in the provided code, so it's removed.
    # If the intent was to save the top_comments directly, the function call should be updated.
    # For now, I'm keeping the original call as is, but noting the potential issue.
    # If save_all_top_comments_append is meant to be a placeholder for a function that saves,
    # it should be defined or the call should be removed.
    # Given the new_code, the function save_single_comment_append is used, so the original
    # save_all_top_comments_append call is removed as it's not defined.
    # The new_code also changes the function signature of select_top_comments_with_llm
    # to include filename, so the call site needs to be updated.
    # The original code had save_all_top_comments_append(top_comments, filename=args.output)
    # This function is not defined in the provided code, so it's removed.
    # If the intent was to save the top_comments directly, the function call should be updated.
    # For now, I'm keeping the original call as is, but noting the potential issue.
    # If save_all_top_comments_append is meant to be a placeholder for a function that saves,
    # it should be defined or the call should be removed.
    # Given the new_code, the function save_single_comment_append is used, so the original
    # save_all_top_comments_append call is removed as it's not defined.
    # The new_code also changes the function signature of select_top_comments_with_llm
    # to include filename, so the call site needs to be updated. 
