"""
Access control module for role-based data filtering
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def filter_data_by_role(data: pd.DataFrame, admin_role: dict) -> pd.DataFrame:
    """
    Filter dataset based on user role (grade and class)
    
    Args:
        data: pandas DataFrame of student records
        admin_role: Dictionary with 'grade' and 'class' keys (None means no filter)
        
    Returns:
        Filtered DataFrame based on role permissions
    """
    if data.empty:
        logger.warning("Received empty data")
        return pd.DataFrame()
    
    filtered_df = data.copy()
    
    # Apply grade filter (only if not None)
    if admin_role.get("grade") is not None:
        grade = admin_role.get("grade")
        filtered_df = filtered_df[filtered_df["grade"] == grade]
        logger.info(f"Applied grade filter: {grade}")
    else:
        logger.info("No grade filter applied (All Grades)")
    
    # Apply class filter (only if not None)
    if admin_role.get("class") is not None:
        class_name = admin_role.get("class")
        filtered_df = filtered_df[filtered_df["class"] == class_name]
        logger.info(f"Applied class filter: {class_name}")
    else:
        logger.info("No class filter applied (All Classes)")
    
    logger.info(f"Filtered from {len(data)} to {len(filtered_df)} records")
    return filtered_df


