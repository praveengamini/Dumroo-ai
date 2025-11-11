"""
Utility functions and helpers for the API
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class QueryType(str, Enum):
    """Types of queries supported"""
    FILTER = "filter"
    AGGREGATE = "aggregate"
    SORT = "sort"
    SEARCH = "search"

class ResponseStatus(str, Enum):
    """Response status codes"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    TIMEOUT = "timeout"

def sanitize_error(error: Exception) -> str:
    """
    Sanitize error messages for production
    Prevents leaking sensitive information
    """
    error_str = str(error)
    
    # Remove file paths and sensitive info
    sensitive_patterns = [
        r'/[^/]+\.py',  # File paths
        r'File ".*?"',  # File references
        r'line \d+',    # Line numbers in prod
    ]
    
    for pattern in sensitive_patterns:
        import re
        error_str = re.sub(pattern, '', error_str)
    
    return error_str.strip() or "An error occurred"

def format_response(
    data: Any = None,
    status: ResponseStatus = ResponseStatus.SUCCESS,
    message: str = "",
    error: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Format API response consistently
    """
    response = {
        "status": status.value,
        "timestamp": datetime.now().isoformat(),
        "data": data,
    }
    
    if message:
        response["message"] = message
    
    if error:
        response["error"] = error
    
    response.update(kwargs)
    return response

def calculate_statistics(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate basic statistics from query results"""
    if not data:
        return {"total": 0}
    
    stats = {
        "total": len(data),
        "fields": list(data[0].keys()) if data else [],
    }
    
    # Calculate numeric statistics
    for field in stats["fields"]:
        try:
            values = [
                float(row.get(field, 0)) 
                for row in data 
                if row.get(field) is not None
            ]
            
            if values:
                stats[f"{field}_stats"] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "count": len(values)
                }
        except (ValueError, TypeError):
            pass
    
    return stats

def paginate_results(
    data: List[Dict[str, Any]],
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """Paginate query results"""
    total = len(data)
    total_pages = (total + page_size - 1) // page_size
    
    if page < 1 or page > total_pages:
        page = 1
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "data": data[start:end],
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }

def merge_similar_queries(history: List[str], threshold: float = 0.8) -> List[str]:
    """
    Merge similar queries in history to reduce context size
    Uses simple string similarity
    """
    if len(history) <= 1:
        return history
    
    def similarity(s1: str, s2: str) -> float:
        """Simple similarity calculation"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, s1, s2).ratio()
    
    merged = [history[0]]
    for current in history[1:]:
        if not any(similarity(current, prev) > threshold for prev in merged):
            merged.append(current)
    
    return merged

def validate_csv_structure(df) -> bool:
    """Validate that CSV has expected structure"""
    required_columns = {"grade", "class"}
    available_columns = set(df.columns.str.lower())
    
    return required_columns.issubset(available_columns)

def get_column_types(df) -> Dict[str, str]:
    """Get data types of DataFrame columns"""
    return {col: str(dtype) for col, dtype in df.dtypes.items()}

def estimate_query_complexity(query: str) -> str:
    """Estimate query complexity: simple, medium, complex"""
    keywords_simple = ["show", "list", "get"]
    keywords_medium = ["count", "average", "group"]
    keywords_complex = ["join", "merge", "aggregate"]
    
    query_lower = query.lower()
    
    complexity_score = sum(
        1 for kw in keywords_complex if kw in query_lower
    ) * 3
    complexity_score += sum(
        1 for kw in keywords_medium if kw in query_lower
    ) * 2
    complexity_score += sum(
        1 for kw in keywords_simple if kw in query_lower
    ) * 1
    
    if complexity_score >= 5:
        return "complex"
    elif complexity_score >= 2:
        return "medium"
    else:
        return "simple"

class QueryCache:
    """Simple query result cache"""
    
    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            self.hits += 1
            return self.cache[key]["data"]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache"""
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]["timestamp"]
            )
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "data": value,
            "timestamp": datetime.now().timestamp(),
            "ttl": ttl
        }
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": (self.hits / total * 100) if total > 0 else 0,
        }

# Global cache instance
query_cache = QueryCache()
