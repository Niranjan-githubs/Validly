# config.py
from pydantic import BaseModel, Field  # Import from pydantic directly (v2)
from typing import Dict, Any
from langchain.prompts import PromptTemplate

class LangChainSchema(BaseModel):
    prompt_template: PromptTemplate
    
    model_config = {"arbitrary_types_allowed": True}  # This is the v2 syntax
    
    def create_prompt(self, data: Dict[str, Any]) -> str:
        """Format the prompt template with the given data"""
        return self.prompt_template.format(**data)