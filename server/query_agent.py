import google.generativeai as genai
import os
import re
import logging
from dotenv import load_dotenv
from typing import List

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Configure Gemini
genai.configure(api_key=api_key)


class QueryAgent:
    """
    Simple agent that asks Gemini to generate executable pandas code.
    No JSON parsing, no complex logic - just direct code execution.
    """
    
    def __init__(self):
        # Use the model that works - gemini-flash-latest
        self.model = genai.GenerativeModel("gemini-flash-latest")
        logger.info("✅ Gemini model initialized: gemini-flash-latest")

    def get_pandas_query(self, user_query: str, schema: List[str], sample_rows: str = "") -> str:
        """
        Ask Gemini to generate pandas code that answers the user's query.
        
        Args:
            user_query: Natural language question from user
            schema: List of column names in the dataframe
            sample_rows: Sample data for context (optional)
        
        Returns:
            Executable pandas code as a string
        """
        
        prompt = f"""You are a pandas expert. Convert the user's natural language query into executable pandas code.

INPUT DATAFRAME: `df`
Columns: {', '.join(schema)}

{sample_rows}

IMPORTANT RULES:
1. Return ONLY executable Python code - no markdown, no explanations, no comments
2. The code MUST create a variable called `result_df` with the answer
3. Use pandas operations on the input dataframe `df`
4. For column "class", use backticks in query(): df.query("`class` == 'A'")
5. For string comparisons, use single quotes: 'Yes', 'No', 'A', 'B'

COMMON PATTERNS:

Simple filters:
- "Students in grade 8" → result_df = df[df['grade'] == 8]
- "Homework not submitted" → result_df = df[df['homework_submitted'] == 'No']
- "Class A students" → result_df = df[df['class'] == 'A']

Rankings:
- "Who is the topper?" → result_df = df.nlargest(1, 'quiz_score')
- "2nd highest scorer" → result_df = df.nlargest(2, 'quiz_score').tail(1)
- "Lowest scorer" → result_df = df.nsmallest(1, 'quiz_score')
- "Top 5 students" → result_df = df.nlargest(5, 'quiz_score')

Complex filters:
- "Grade 8 with score > 80" → result_df = df[(df['grade'] == 8) & (df['quiz_score'] > 80)]
- Multiple conditions → result_df = df[(condition1) & (condition2) & (condition3)]

Grouping:
- "Topper in each class" → result_df = df.loc[df.groupby('class')['quiz_score'].idxmax()]
- "Average by class" → result_df = df.groupby('class')['quiz_score'].mean().reset_index()

Sorting:
- "All students by score" → result_df = df.sort_values('quiz_score', ascending=False)

Statistics:
- "Count by class" → result_df = df.groupby('class').size().reset_index(name='count')
- "Total/Average/Max/Min" → Use .sum(), .mean(), .max(), .min()

USER QUERY: {user_query}

PANDAS CODE:"""

        try:
            logger.info(f"🔄 Calling Gemini API for query: {user_query}")
            response = self.model.generate_content(prompt)
            
            # Check if response is valid
            if not response or not response.text:
                logger.error("❌ Gemini returned empty response")
                raise ValueError("Empty response from Gemini")
            
            code = response.text.strip()
            logger.info(f"📥 Raw Gemini response:\n{code}")
            
            # Clean up markdown code fences
            code = re.sub(r'^```(?:python)?\s*', '', code, flags=re.MULTILINE)
            code = re.sub(r'\s*```$', '', code, flags=re.MULTILINE)
            code = code.strip()
            
            # Remove comment lines and empty lines
            lines = code.split('\n')
            code_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    code_lines.append(line)
            
            code = '\n'.join(code_lines)
            
            # Ensure result_df is in the code
            if 'result_df' not in code:
                logger.warning("⚠️ Gemini didn't create result_df, wrapping code")
                code = f"result_df = {code}"
            
            logger.info(f"✅ Generated pandas code:\n{code}")
            return code
            
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}", exc_info=True)
            # Fallback: return empty dataframe
            logger.error("⚠️ Using fallback: empty dataframe")
            return "result_df = df.head(0)"