# nova/query_generator.py
#Returns dict/json full of search queries based on "key_info"

from langchain_together import Together
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# 🔐 Together API key
import os
os.environ["TOGETHER_API_KEY"] = "5d8cf27da8aaea81911f8a381a3feee5a89624aa2f3c25aecaec88d3a080a8a8"

# 📌 Define LLM
llm = Together(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.7,
    max_tokens=512
)

# 🧠 Prompt Template
prompt_template = PromptTemplate(
    input_variables=["key_info"],
    template="""
You are a startup research assistant. Based on the following context, generate 5 specific, diverse, and high-intent Google search queries that a startup founder would use to conduct market research for validating their idea.

Each query must focus on uncovering factual information about market size, customer demand, existing competition, industry trends, and potential risks.

Context:
{key_info}

Respond ONLY with a JSON list of strings. No markdown, no extra commentary.

"""
)

# 🔄 LangChain LLMChain
query_chain = prompt_template | llm

# 🚀 Generator Function
def generate_queries(key_strings: dict) -> list:
    context_str = "\n".join([f"{k}: {v}" for k, v in key_strings.items()])
    response = query_chain.invoke({"key_info": context_str})
    
    # Clean the response
    if isinstance(response, str):
        # Remove markdown formatting
        clean_response = response.replace("```json", "").replace("```", "").strip()
        
        try:
            # Try to parse as JSON/list
            import json
            return json.loads(clean_response)
        except json.JSONDecodeError:
            # If not valid JSON, split by lines and clean up
            return [line.strip() for line in clean_response.splitlines() 
                   if line.strip() and not line.startswith("[") and not line.startswith("]")]
    
    return []

