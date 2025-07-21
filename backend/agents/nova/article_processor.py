import re
from typing import Dict, Any


def summarize_article_data(article_data, max_chars_per_article=800):
    """
    Summarize article data while preserving key facts, numbers, and points.
    
    Args:
        article_data: Dictionary mapping URLs to content (which might be lists)
        max_chars_per_article: Maximum characters per article summary
    
    Returns:
        Dictionary with summarized content
    """
    import re
    summarized_data = {}
    
    for url, content_data in article_data.items():
        try:
            # Handle case where content is a list
            if isinstance(content_data, list):
                # Convert list items to strings and join them
                content_text = ""
                for item in content_data:
                    if isinstance(item, dict) and "extracted_text" in item:
                        # If it's a dict with extracted_text, use that
                        content_text += item.get("extracted_text", "") + "\n\n"
                    elif isinstance(item, str):
                        # If it's already a string, use it directly
                        content_text += item + "\n\n"
                    else:
                        # Otherwise, try to convert to string
                        content_text += str(item) + "\n\n"
            else:
                # If it's not a list, try to use it as is or convert to string
                content_text = str(content_data)
            
            # Skip if we ended up with no usable content
            if not content_text.strip():
                summarized_data[url] = "No usable content available"
                continue
                
            # Extract first sentence as title
            first_sentence = content_text.split('.')[0] + '.' if '.' in content_text else content_text[:100]
            
            # Extract numerical facts using regex
            numerical_facts = re.findall(r'\b\d+(?:\.\d+)?%?\s+[a-zA-Z\s]+', content_text)
            stats = ' '.join(numerical_facts[:10])  # Take first 10 stats
            
            # Get first and last paragraph for context
            paragraphs = content_text.split('\n\n')
            intro = paragraphs[0] if paragraphs else ""
            conclusion = paragraphs[-1] if len(paragraphs) > 1 else ""
            
            # Create summary with key components
            summary = f"{first_sentence}\n\nKEY STATS: {stats}\n\nINTRO: {intro[:300]}...\n\nCONCLUSION: {conclusion[:300]}..."
            
            # Ensure summary is within length limit
            if len(summary) > max_chars_per_article:
                summary = summary[:max_chars_per_article] + "..."
            
            summarized_data[url] = summary
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            summarized_data[url] = f"Error processing content: {str(e)[:100]}"
    
    return summarized_data