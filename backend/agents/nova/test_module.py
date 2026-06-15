# test_web_search.py

from web_search import run_web_search_agent
from query_generator import generate_queries
from pprint import pprint
import json

# Sample input for RuralCare
sample_input = {
    "startup_name": "RuralCare",
    "one_liner": "Bringing healthcare to rural India through telemedicine.",
    "problem_statement": "Rural India faces a shortage of healthcare professionals and limited access to medical facilities, leading to delayed or inadequate treatment.",
    "solution_summary": "RuralCare connects rural patients with certified doctors via telemedicine, providing consultations, prescriptions, and health monitoring.",
    "product_type": "app",
    "target_customer": "Rural populations in India, especially in remote and underserved areas.",
    "customer_pain_points": "Lack of access to healthcare professionals, Limited medical infrastructure, Long travel times to nearest clinic, High healthcare costs",
    "key_features": "Virtual doctor consultations, Digital prescriptions, Health monitoring tools, Emergency response integration",
    "unique_selling_point": "Affordable, accessible healthcare at the fingertips of rural populations with multilingual support for diverse regions.",
    "why_now": "The increasing mobile phone penetration and internet access in rural India makes telemedicine a feasible solution for bridging the healthcare gap."
}

# Generate search queries
sample_queries = generate_queries(sample_input)

# Run web search agent with the generated queries
res = run_web_search_agent(sample_queries)

# Saving the result to an output file
output_file_path = "output_search_results.json"

with open(output_file_path, "w") as file:
    json.dump(res, file, indent=4)

print(f"Results saved to {output_file_path}")
