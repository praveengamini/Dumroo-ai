import google.generativeai as genai
import os, re, json, logging
from dotenv import load_dotenv
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
try:
    genai.configure(api_key=api_key)
    GEMINI_OK = True
except Exception:
    GEMINI_OK = False
    logger.warning("Gemini not initialized — using local rules")

class QueryAgent:
    def __init__(self, max_history: int = 10):
        self.chat_history = []
        self.max_history = max_history
        self.model = genai.GenerativeModel("gemini-flash-latest") if GEMINI_OK else None

    # ---------------------------
    # 🔧 Rule-based fallback
    # ---------------------------
    def _rule_based(self, q: str, columns: List[str]) -> Dict[str, Any]:
        q = q.lower()
        colset = [c.lower() for c in columns]

        if any(x in q for x in ["highest", "topper", "best", "maximum", "top mark", "high score"]):
            return {"type": "agg", "op": "global_max", "column": "quiz_score" if "quiz_score" in colset else columns[-1]}
        if any(x in q for x in ["lowest", "least", "minimum", "weak"]):
            return {"type": "agg", "op": "global_min", "column": "quiz_score" if "quiz_score" in colset else columns[-1]}
        if "not submitted" in q or "didn't" in q or "not done" in q or "no homework" in q:
            return {"type": "filter", "expr": "homework_submitted == 'No'"}
        if "submitted" in q and "not" not in q:
            return {"type": "filter", "expr": "homework_submitted == 'Yes'"}
        if "absent" in q:
            if "attendance" in colset:
                return {"type": "filter", "expr": "attendance == 'Absent'"}
        if re.search(r"\bgrade\s*\d+\b", q):
            num = re.findall(r"\d+", q)[0]
            return {"type": "filter", "expr": f"grade == {num}"}
        return {"type": "filter", "expr": ""}

    # ---------------------------
    # ⚙️ Main processing
    # ---------------------------
    def get_condition(self, user_query: str, schema: List[str]) -> Dict[str, Any]:
        q = user_query.strip()
        if not q:
            return {"raw": "", "parsed": {"type": "filter", "expr": ""}}

        if not self.model:
            parsed = self._rule_based(q, schema)
            return {"raw": json.dumps(parsed), "parsed": parsed}

        try:
            prompt = f"""
You are a precise data filter generator.
Given dataset columns: {', '.join(schema)}

Return EITHER:
1️⃣ Plain pandas-style condition: e.g. quiz_score > 90 and homework_submitted == 'No'
2️⃣ OR JSON object like: {{"type":"agg","op":"global_max","column":"quiz_score"}}

NEVER wrap JSON inside text or code fences.
User: {q}
"""
            response = self.model.generate_content(prompt)
            result = (response.text or "").strip()

            # 🧹 Cleanup
            result = result.strip("`").replace("```json", "").replace("```", "").strip()
            # Remove nested "json\n{...}" junk
            if "json" in result.lower() and "{" in result:
                result = result[result.index("{") : result.rindex("}") + 1]

            # Try parsing JSON
            try:
                parsed = json.loads(result)
                if isinstance(parsed, dict):
                    return {"raw": result, "parsed": parsed}
            except Exception:
                pass

            # fallback if Gemini returned a string expression
            parsed = {"type": "filter", "expr": result}
            return {"raw": result, "parsed": parsed}

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            parsed = self._rule_based(q, schema)
            return {"raw": json.dumps(parsed), "parsed": parsed}
