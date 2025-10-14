# test_web_scraper.py

from web_scrape import extract_all_articles
import json

# Load the saved output from the previous module
with open("output_search_results.json") as f:
    search_results = json.load(f)

extracted = extract_all_articles(search_results)

# Save the cleaned text output
with open("cleaned_article_texts.json", "w") as f:
    json.dump(extracted, f, indent=4)

print("Cleaned text saved to cleaned_article_texts.json")
