import pandas as pd
import logging

logger = logging.getLogger(__name__)

def filter_data_by_role(data: pd.DataFrame, admin_role: dict) -> pd.DataFrame:
    """Role-based filtering"""
    if data.empty:
        logger.warning("Empty data received")
        return pd.DataFrame()

    df = data.copy()

    if admin_role.get("grade") is not None:
        df = df[df["grade"] == admin_role["grade"]]
    if admin_role.get("class") is not None:
        col = "class" if "class" in df.columns else "class_name"
        df = df[df[col] == admin_role["class"]]

    return df
