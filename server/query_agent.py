import google.generativeai as genai
import os
import logging
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from typing import List, Optional

logger = logging.getLogger(__name__)
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.warning("GOOGLE_API_KEY not set in environment")

genai.configure(api_key=api_key)

class QueryAgent:
    """AI-powered query agent using Google Gemini"""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize the query agent
        
        Args:
            max_history: Maximum number of conversation turns to keep
        """
        self.chat_history: List[str] = []
        self.max_history = max_history
        self.model = genai.GenerativeModel("gemini-flash-latest")
        logger.info("QueryAgent initialized with Gemini Flash model")

    def get_condition(self, user_query: str, schema: List[str]) -> str:
        """
        Convert natural language query to pandas filter condition
        
        Args:
            user_query: Natural language question
            schema: List of available column names
            
        Returns:
            Valid pandas filter condition string
            
        Raises:
            Exception: If condition generation fails
        """
        try:
            schema_str = ", ".join(schema)
            context = "\n".join(self.chat_history[-self.max_history:])

            prompt = f"""You are an expert data analyst. Convert the user's natural language question into a valid Pandas DataFrame filter condition.

Dataset columns: {schema_str}

Important rules:
1. Return ONLY the condition string, no explanations
2. Use pandas-compatible syntax (column == value, column > value, etc.)
3. Use & for AND, | for OR operations
4. String comparisons should use == or !=
5. For Yes/No values in string columns, use == 'Yes' or == 'No'
6. If the question is ambiguous, make reasonable assumptions
7. Return empty string if query cannot be converted to a condition

Conversation context:
{context}

User question: {user_query}

Return ONLY the filter condition, nothing else. If you cannot create a condition, return an empty string."""

            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # Clean up the result
            if result.startswith('```'):
                result = result.split('\n', 1)[1]
            if result.endswith('```'):
                result = result.rsplit('\n', 1)[0]
            
            result = result.strip().strip("'\"")
            
            if result.lower() in ['no condition', 'n/a', 'none']:
                result = ""
            
            logger.info(f"Generated condition: {result}")

            # Store in conversation memory
            self.chat_history.append(f"User: {user_query}")
            self.chat_history.append(f"Filter: {result}")

            return result
            
        except Exception as e:
            logger.error(f"Error generating condition: {str(e)}")
            return ""

