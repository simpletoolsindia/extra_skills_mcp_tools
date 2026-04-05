"""Pandas MCP - Data manipulation and analysis for LLM agents."""

from __future__ import annotations

import os
import json
from typing import Optional, List, Dict, Any, Union

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def _error_response(msg: str) -> dict:
    return {"result": None, "error": msg}


def create_dataframe(
    data: Union[List[Dict], Dict, str],
    name: str = "df",
) -> dict:
    """
    Create a pandas DataFrame.

    Args:
        data: List of dicts, dict with lists, or JSON string
        name: DataFrame name for reference

    Returns:
        dict with keys: df_id, shape, columns, preview, error
    """
    if not PANDAS_AVAILABLE:
        return _error_response("pandas not installed")

    try:
        # Parse input
        if isinstance(data, str):
            data = json.loads(data)

        if isinstance(data, dict):
            # Dict of lists
            df = pd.DataFrame(data)
        elif isinstance(data, list):
            # List of dicts
            df = pd.DataFrame(data)
        else:
            return _error_response("Invalid data format")

        # Generate ID
        import hashlib
        df_id = hashlib.md5(str(data).encode()).hexdigest()[:8]

        return {
            "df_id": df_id,
            "shape": list(df.shape),
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "preview": df.head(5).to_dict(orient='records'),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "error": None,
        }
    except Exception as e:
        return _error_response(str(e))


def describe_dataframe(df_id: str, data: List[Dict]) -> dict:
    """Get statistical description of DataFrame."""
    if not PANDAS_AVAILABLE:
        return _error_response("pandas not installed")

    try:
        df = pd.DataFrame(data)

        # Get numeric columns stats
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        stats = {}
        if numeric_cols:
            stats['numeric'] = df[numeric_cols].describe().to_dict()

        if categorical_cols:
            stats['categorical'] = {}
            for col in categorical_cols:
                stats['categorical'][col] = {
                    'unique_count': df[col].nunique(),
                    'top_values': df[col].value_counts().head(5).to_dict(),
                }

        return {
            "shape": list(df.shape),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "missing_values": df.isnull().sum().to_dict(),
            "statistics": stats,
            "error": None,
        }
    except Exception as e:
        return _error_response(str(e))


def filter_dataframe(
    data: List[Dict],
    conditions: str,
) -> dict:
    """
    Filter DataFrame with conditions.

    Args:
        data: List of dicts (DataFrame rows)
        conditions: JSON string with filter conditions

    Example conditions:
    {"column": "age", "operator": ">", "value": 25}
    {"column": "name", "operator": "contains", "value": "John"}
    {"column": "status", "operator": "in", "value": ["active", "pending"]}
    """
    if not PANDAS_AVAILABLE:
        return _error_response("pandas not installed")

    try:
        df = pd.DataFrame(data)
        conditions = json.loads(conditions)

        if isinstance(conditions, dict):
            conditions = [conditions]

        for cond in conditions:
            col = cond.get("column")
            op = cond.get("operator")
            val = cond.get("value")

            if col not in df.columns:
                return _error_response(f"Column '{col}' not found")

            if op == ">":
                df = df[df[col] > val]
            elif op == "<":
                df = df[df[col] < val]
            elif op == ">=":
                df = df[df[col] >= val]
            elif op == "<=":
                df = df[df[col] <= val]
            elif op == "==":
                df = df[df[col] == val]
            elif op == "!=":
                df = df[df[col] != val]
            elif op == "contains":
                df = df[df[col].astype(str).str.contains(str(val), case=False, na=False)]
            elif op == "startswith":
                df = df[df[col].astype(str).str.startswith(str(val))]
            elif op == "endswith":
                df = df[df[col].astype(str).str.endswith(str(val))]
            elif op == "in":
                df = df[df[col].isin(val)]
            elif op == "not_in":
                df = df[~df[col].isin(val)]
            elif op == "is_null":
                df = df[df[col].isnull()]
            elif op == "not_null":
                df = df[df[col].notnull()]

        return {
            "result": df.to_dict(orient='records'),
            "shape": list(df.shape),
            "filtered_count": len(df),
            "error": None,
        }
    except Exception as e:
        return _error_response(str(e))


def aggregate_data(
    data: List[Dict],
    group_by: List[str],
    aggregations: Dict[str, str],
) -> dict:
    """
    Aggregate DataFrame data.

    Args:
        data: List of dicts
        group_by: Columns to group by
        aggregations: Dict of {column: function} e.g. {"amount": "sum", "count": "count"}

    Available functions: sum, mean, median, min, max, count, std, first, last
    """
    if not PANDAS_AVAILABLE:
        return _error_response("pandas not installed")

    try:
        df = pd.DataFrame(data)

        # Build aggregation dict
        agg_dict = {}
        for col, func in aggregations.items():
            if col in df.columns:
                agg_dict[col] = func

        result = df.groupby(group_by).agg(agg_dict).reset_index()

        return {
            "result": result.to_dict(orient='records'),
            "shape": list(result.shape),
            "columns": result.columns.tolist(),
            "error": None,
        }
    except Exception as e:
        return _error_response(str(e))


def sort_dataframe(
    data: List[Dict],
    column: str,
    ascending: bool = True,
) -> dict:
    """Sort DataFrame by column."""
    if not PANDAS_AVAILABLE:
        return _error_response("pandas not installed")

    try:
        df = pd.DataFrame(data)

        if column not in df.columns:
            return _error_response(f"Column '{column}' not found")

        result = df.sort_values(by=column, ascending=ascending)

        return {
            "result": result.to_dict(orient='records'),
            "shape": list(result.shape),
            "error": None,
        }
    except Exception as e:
        return _error_response(str(e))


def pivot_data(
    data: List[Dict],
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "sum",
) -> dict:
    """Create pivot table."""
    if not PANDAS_AVAILABLE:
        return _error_response("pandas not installed")

    try:
        df = pd.DataFrame(data)

        result = pd.pivot_table(
            df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
        ).reset_index()

        return {
            "result": result.to_dict(orient='records'),
            "shape": list(result.shape),
            "error": None,
        }
    except Exception as e:
        return _error_response(str(e))


def join_dataframes(
    left: List[Dict],
    right: List[Dict],
    on_left: str,
    on_right: str,
    how: str = "inner",
) -> dict:
    """Join two DataFrames."""
    if not PANDAS_AVAILABLE:
        return _error_response("pandas not installed")

    try:
        df_left = pd.DataFrame(left)
        df_right = pd.DataFrame(right)

        result = pd.merge(df_left, df_right, left_on=on_left, right_on=on_right, how=how)

        return {
            "result": result.to_dict(orient='records'),
            "shape": list(result.shape),
            "left_rows": len(df_left),
            "right_rows": len(df_right),
            "error": None,
        }
    except Exception as e:
        return _error_response(str(e))


def compute_correlation(
    data: List[Dict],
    columns: Optional[List[str]] = None,
) -> dict:
    """Compute correlation matrix."""
    if not PANDAS_AVAILABLE:
        return _error_response("pandas not installed")

    try:
        df = pd.DataFrame(data)

        if columns:
            df = df[columns]

        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return _error_response("No numeric columns found")

        corr = numeric_df.corr()

        return {
            "correlation": corr.to_dict(),
            "columns": numeric_df.columns.tolist(),
            "error": None,
        }
    except Exception as e:
        return _error_response(str(e))


def detect_outliers(
    data: List[Dict],
    column: str,
    method: str = "iqr",
    threshold: float = 1.5,
) -> dict:
    """
    Detect outliers in numeric column.

    Methods: iqr (Interquartile Range), zscore
    """
    if not PANDAS_AVAILABLE:
        return _error_response("pandas not installed")

    try:
        df = pd.DataFrame(data)

        if column not in df.columns:
            return _error_response(f"Column '{column}' not found")

        if method == "iqr":
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - threshold * IQR
            upper = Q3 + threshold * IQR
            outliers = df[(df[column] < lower) | (df[column] > upper)]
        elif method == "zscore":
            z = np.abs((df[column] - df[column].mean()) / df[column].std())
            outliers = df[z > threshold]
        else:
            return _error_response(f"Unknown method: {method}")

        return {
            "outliers": outliers.to_dict(orient='records'),
            "outlier_count": len(outliers),
            "total_count": len(df),
            "percentage": round(len(outliers) / len(df) * 100, 2),
            "error": None,
        }
    except Exception as e:
        return _error_response(str(e))