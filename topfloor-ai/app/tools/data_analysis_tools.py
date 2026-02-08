"""
Data Analysis Tools - Tools for data ingestion, analysis, and visualization

This module provides tools for the Data Analyst Agent to perform:
- Data loading from various sources (CSV, JSON, Excel)
- Data cleaning and preprocessing
- Statistical analysis
- Data visualization
- Dashboard creation
- Report generation
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging
import pandas as pd
import numpy as np
from pathlib import Path
import json
import re
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

logger = logging.getLogger(__name__)


def validate_positive_number(value: float, field_name: str) -> Optional[Dict[str, Any]]:
    """
    Validate that a number is positive
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Error dict if invalid, None if valid
    """
    if value is None:
        return {
            "status": "error",
            "message": f"{field_name} is required"
        }
    
    try:
        value = float(value)
        if value < 0:
            return {
                "status": "error",
                "message": f"{field_name} must be non-negative, got {value}"
            }
    except (ValueError, TypeError):
        return {
            "status": "error",
            "message": f"{field_name} must be a valid number, got {value}"
        }
    
    return None


def validate_string_not_empty(value: str, field_name: str) -> Optional[Dict[str, Any]]:
    """
    Validate that a string is not empty
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Error dict if invalid, None if valid
    """
    if not value or not isinstance(value, str) or not value.strip():
        return {
            "status": "error",
            "message": f"{field_name} is required and must be a non-empty string"
        }
    
    return None


def load_dataset(
    source: str,
    format: str = "csv",
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Load dataset from various sources (file path, URL) in multiple formats.
    
    Args:
        source: File path or URL to the data source
        format: Data format ('csv', 'json', 'excel', 'xlsx', 'xls')
        options: Optional dictionary of format-specific options
        
    Returns:
        Dataset information including row count, columns, data types, preview, and summary
        
    Example:
        >>> result = load_dataset("/path/to/data.csv", "csv")
        >>> print(result["rows"])
        1000
    """
    try:
        # Validate inputs
        validation_error = validate_string_not_empty(source, "source")
        if validation_error:
            return validation_error
        
        validation_error = validate_string_not_empty(format, "format")
        if validation_error:
            return validation_error
        
        logger.info(f"Loading dataset from {source} (format: {format})")
        
        # Validate format
        valid_formats = ["csv", "json", "excel", "xlsx", "xls"]
        if format.lower() not in valid_formats:
            return {
                "status": "error",
                "message": f"Unsupported format: {format}. Supported formats: {', '.join(valid_formats)}",
                "source": source
            }
        
        options = options or {}
        df = None
        
        # Check if source is URL or file path
        is_url = source.startswith("http://") or source.startswith("https://")
        
        # Validate file exists if not URL
        if not is_url:
            file_path = Path(source)
            if not file_path.exists():
                return {
                    "status": "error",
                    "message": f"File not found: {source}",
                    "source": source
                }
            
            # Validate file size (max 100MB)
            max_file_size = 100 * 1024 * 1024  # 100MB
            if file_path.stat().st_size > max_file_size:
                return {
                    "status": "error",
                    "message": f"File size exceeds maximum allowed size of 100MB",
                    "source": source
                }
        
        # Load data based on format
        if format.lower() == "csv":
            try:
                df = pd.read_csv(source, **options)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(source, encoding='latin-1', **options)
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Failed to read CSV file with multiple encodings: {str(e)}",
                        "source": source
                    }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to read CSV file: {str(e)}",
                    "source": source
                }
        
        elif format.lower() == "json":
            try:
                df = pd.read_json(source, **options)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to read JSON file: {str(e)}",
                    "source": source
                }
        
        elif format.lower() in ["excel", "xlsx", "xls"]:
            try:
                df = pd.read_excel(source, **options)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to read Excel file: {str(e)}",
                    "source": source
                }
        
        if df is None or df.empty:
            return {
                "status": "error",
                "message": "No data found in source or source is empty",
                "source": source
            }
        
        # Validate row count (max 1,000,000 rows)
        max_rows = 1000000
        if len(df) > max_rows:
            return {
                "status": "error",
                "message": f"Dataset contains too many rows ({len(df)}). Maximum allowed: {max_rows}",
                "source": source
            }
        
        # Get data types
        dtypes_dict = {}
        for col, dtype in df.dtypes.items():
            dtypes_dict[str(col)] = str(dtype)
        
        # Get preview (first 10 rows)
        preview = df.head(10).to_dict(orient='records')
        
        # Get summary statistics for numeric columns
        summary = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            desc = df[numeric_cols].describe()
            summary = desc.to_dict()
        
        # Detect missing values
        missing_values = {}
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_values[str(col)] = int(missing_count)
        
        return {
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": dtypes_dict,
            "preview": preview,
            "summary": summary,
            "missing_values": missing_values,
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            "status": "success",
            "message": f"Dataset loaded successfully from {source}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error loading dataset from {source}: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to load dataset: {str(e)}",
            "source": source,
            "timestamp": datetime.now().isoformat()
        }


def clean_data(
    data: Union[pd.DataFrame, Dict[str, Any]],
    operations: List[str]
) -> Dict[str, Any]:
    """
    Clean and preprocess data by handling missing values, outliers, and formatting issues.
    
    Args:
        data: DataFrame or dictionary representation of data
        operations: List of cleaning operations to perform
                   ('remove_duplicates', 'fill_missing', 'remove_outliers', 'normalize_columns')
        
    Returns:
        Cleaned data information and statistics about changes made
        
    Example:
        >>> result = clean_data(df, ["remove_duplicates", "fill_missing"])
        >>> print(result["rows_removed"])
        5
    """
    try:
        # Validate inputs
        if data is None:
            return {
                "status": "error",
                "message": "data is required"
            }
        
        if not isinstance(operations, list):
            return {
                "status": "error",
                "message": "operations must be a list"
            }
        
        # Convert dict to DataFrame if needed
        if isinstance(data, dict):
            try:
                df = pd.DataFrame(data)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to convert data to DataFrame: {str(e)}"
                }
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            return {
                "status": "error",
                "message": "data must be a DataFrame or dictionary"
            }
        
        if df.empty:
            return {
                "status": "error",
                "message": "Data is empty"
            }
        
        logger.info(f"Cleaning data with operations: {operations}")
        
        initial_rows = len(df)
        initial_cols = len(df.columns)
        changes = []
        
        # Valid operations
        valid_operations = [
            "remove_duplicates",
            "fill_missing",
            "remove_outliers",
            "normalize_columns",
            "drop_empty_columns",
            "drop_empty_rows"
        ]
        
        # Validate operations
        for op in operations:
            if op not in valid_operations:
                return {
                    "status": "error",
                    "message": f"Invalid operation: {op}. Valid operations: {', '.join(valid_operations)}"
                }
        
        # Perform operations
        if "remove_duplicates" in operations:
            before = len(df)
            df = df.drop_duplicates()
            removed = before - len(df)
            if removed > 0:
                changes.append(f"Removed {removed} duplicate rows")
        
        if "fill_missing" in operations:
            missing_before = df.isna().sum().sum()
            
            # Fill numeric columns with median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isna().any():
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
            
            # Fill categorical columns with mode
            categorical_cols = df.select_dtypes(include=['object', 'string']).columns
            for col in categorical_cols:
                if df[col].isna().any():
                    mode_val = df[col].mode()
                    if len(mode_val) > 0:
                        df[col] = df[col].fillna(mode_val[0])
                    else:
                        df[col] = df[col].fillna("Unknown")
            
            missing_after = df.isna().sum().sum()
            filled = missing_before - missing_after
            if filled > 0:
                changes.append(f"Filled {filled} missing values")
        
        if "remove_outliers" in operations:
            before = len(df)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            
            removed = before - len(df)
            if removed > 0:
                changes.append(f"Removed {removed} outlier rows")
        
        if "normalize_columns" in operations:
            # Normalize column names: lowercase, replace spaces with underscores
            old_cols = df.columns.tolist()
            df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('[^a-z0-9_]', '', regex=True)
            new_cols = df.columns.tolist()
            
            renamed_count = sum(1 for old, new in zip(old_cols, new_cols) if old != new)
            if renamed_count > 0:
                changes.append(f"Normalized {renamed_count} column names")
        
        if "drop_empty_columns" in operations:
            before = len(df.columns)
            df = df.dropna(axis=1, how='all')
            removed = before - len(df.columns)
            if removed > 0:
                changes.append(f"Dropped {removed} empty columns")
        
        if "drop_empty_rows" in operations:
            before = len(df)
            df = df.dropna(axis=0, how='all')
            removed = before - len(df)
            if removed > 0:
                changes.append(f"Dropped {removed} empty rows")
        
        final_rows = len(df)
        final_cols = len(df.columns)
        
        return {
            "initial_rows": initial_rows,
            "initial_columns": initial_cols,
            "final_rows": final_rows,
            "final_columns": final_cols,
            "rows_removed": initial_rows - final_rows,
            "columns_removed": initial_cols - final_cols,
            "changes": changes,
            "operations_performed": operations,
            "status": "success",
            "message": f"Data cleaned successfully with {len(operations)} operations",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error cleaning data: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to clean data: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def analyze_data(
    data: Union[pd.DataFrame, Dict[str, Any]],
    analysis_type: str
) -> Dict[str, Any]:
    """
    Perform statistical analysis on data (descriptive stats, correlations, distributions).
    
    Args:
        data: DataFrame or dictionary representation of data
        analysis_type: Type of analysis ('descriptive', 'correlation', 'distribution')
        
    Returns:
        Analysis results with statistical metrics
        
    Example:
        >>> result = analyze_data(df, "descriptive")
        >>> print(result["mean"])
        {'column1': 50.5, 'column2': 100.2}
    """
    try:
        # Validate inputs
        if data is None:
            return {
                "status": "error",
                "message": "data is required"
            }
        
        validation_error = validate_string_not_empty(analysis_type, "analysis_type")
        if validation_error:
            return validation_error
        
        # Convert dict to DataFrame if needed
        if isinstance(data, dict):
            try:
                df = pd.DataFrame(data)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to convert data to DataFrame: {str(e)}"
                }
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            return {
                "status": "error",
                "message": "data must be a DataFrame or dictionary"
            }
        
        if df.empty:
            return {
                "status": "error",
                "message": "Data is empty"
            }
        
        logger.info(f"Performing {analysis_type} analysis on data")
        
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return {
                "status": "error",
                "message": "No numeric columns found in data for analysis"
            }
        
        numeric_df = df[numeric_cols]
        
        if analysis_type == "descriptive":
            # Calculate descriptive statistics
            mean_dict = numeric_df.mean().to_dict()
            median_dict = numeric_df.median().to_dict()
            std_dict = numeric_df.std().to_dict()
            min_dict = numeric_df.min().to_dict()
            max_dict = numeric_df.max().to_dict()
            
            return {
                "analysis_type": "descriptive",
                "mean": mean_dict,
                "median": median_dict,
                "std": std_dict,
                "min": min_dict,
                "max": max_dict,
                "count": len(df),
                "columns_analyzed": list(numeric_cols),
                "status": "success",
                "message": "Descriptive analysis completed successfully",
                "timestamp": datetime.now().isoformat()
            }
        
        elif analysis_type == "correlation":
            # Calculate correlation matrix
            if len(numeric_cols) < 2:
                return {
                    "status": "error",
                    "message": "At least 2 numeric columns required for correlation analysis"
                }
            
            corr_matrix = numeric_df.corr()
            corr_dict = corr_matrix.to_dict()
            
            # Find strong correlations (|r| > 0.7)
            strong_correlations = []
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            "column1": col1,
                            "column2": col2,
                            "correlation": round(float(corr_value), 4),
                            "strength": "strong positive" if corr_value > 0 else "strong negative"
                        })
            
            return {
                "analysis_type": "correlation",
                "correlation_matrix": corr_dict,
                "strong_correlations": strong_correlations,
                "columns_analyzed": list(numeric_cols),
                "status": "success",
                "message": "Correlation analysis completed successfully",
                "timestamp": datetime.now().isoformat()
            }
        
        elif analysis_type == "distribution":
            # Calculate distribution statistics
            skewness_dict = numeric_df.skew().to_dict()
            kurtosis_dict = numeric_df.kurtosis().to_dict()
            
            # Interpret skewness and kurtosis
            interpretations = {}
            for col in numeric_cols:
                skew = skewness_dict[col]
                kurt = kurtosis_dict[col]
                
                if abs(skew) < 0.5:
                    skew_interp = "approximately symmetric"
                elif skew > 0:
                    skew_interp = "right-skewed (positive)"
                else:
                    skew_interp = "left-skewed (negative)"
                
                if abs(kurt) < 0.5:
                    kurt_interp = "normal distribution"
                elif kurt > 0:
                    kurt_interp = "heavy-tailed (leptokurtic)"
                else:
                    kurt_interp = "light-tailed (platykurtic)"
                
                interpretations[col] = {
                    "skewness_interpretation": skew_interp,
                    "kurtosis_interpretation": kurt_interp
                }
            
            return {
                "analysis_type": "distribution",
                "skewness": skewness_dict,
                "kurtosis": kurtosis_dict,
                "interpretations": interpretations,
                "columns_analyzed": list(numeric_cols),
                "status": "success",
                "message": "Distribution analysis completed successfully",
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {
                "status": "error",
                "message": f"Invalid analysis type: {analysis_type}. Valid types: descriptive, correlation, distribution"
            }
    
    except Exception as e:
        logger.error(f"Error analyzing data: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to analyze data: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def create_visualization(
    data: Union[pd.DataFrame, Dict[str, Any]],
    chart_type: str,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create data visualization render payloads.
    
    Args:
        data: DataFrame or dictionary representation of data
        chart_type: Type of chart ('line', 'bar', 'scatter', 'pie', 'heatmap', 'histogram', 'box')
        config: Optional configuration dictionary with chart-specific options:
            - x: Column name for x-axis (required for most charts)
            - y: Column name(s) for y-axis (required for most charts, can be list)
            - title: Chart title
            - xlabel: X-axis label
            - ylabel: Y-axis label
            - color: Column for color grouping
            - size: Column for size (scatter plots)
            - interactive: Optional hint for frontend rendering
            - format: Optional output format hint for frontend
            - figsize: Optional size hint
            - dpi: Optional resolution hint
        
    Returns:
        Dictionary with chart render payload
        
    Example:
        >>> result = create_visualization(df, "line", {"x": "date", "y": "value", "title": "Sales Over Time"})
        >>> print(result["render_type"])
        chart
        
        >>> # SVG format
        >>> result = create_visualization(df, "bar", {"x": "category", "y": "value", "format": "svg"})
        >>> print(result["render_type"])
        chart
    """
    try:
        # Validate inputs
        if data is None:
            return {
                "status": "error",
                "message": "data is required"
            }
        
        validation_error = validate_string_not_empty(chart_type, "chart_type")
        if validation_error:
            return validation_error
        
        # Convert dict to DataFrame if needed
        if isinstance(data, dict):
            try:
                df = pd.DataFrame(data)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to convert data to DataFrame: {str(e)}"
                }
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            return {
                "status": "error",
                "message": "data must be a DataFrame or dictionary"
            }
        
        if df.empty:
            return {
                "status": "error",
                "message": "Data is empty"
            }
        
        # Default config
        config = config or {}
        title = config.get("title", f"{chart_type.capitalize()} Chart")
        
        # Validate chart type
        valid_chart_types = ["line", "bar", "scatter", "pie", "heatmap", "histogram", "box"]
        if chart_type.lower() not in valid_chart_types:
            return {
                "status": "error",
                "message": f"Invalid chart type: {chart_type}. Valid types: {', '.join(valid_chart_types)}"
            }
        
        return {
            "status": "success",
            "render_type": "chart",
            "chart_type": chart_type,
            "data": df.to_dict(orient="records"),
            "config": config,
            "title": title,
            "render_hint": "frontend",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        import traceback
        logger.error(f"Error creating visualization: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"Failed to create visualization: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def _create_plotly_chart(
    df: pd.DataFrame,
    chart_type: str,
    config: Dict[str, Any]
) -> go.Figure:
    """Create interactive chart using Plotly"""
    x = config.get("x")
    y = config.get("y")
    title = config.get("title", f"{chart_type.capitalize()} Chart")
    xlabel = config.get("xlabel", x or "")
    ylabel = config.get("ylabel", y or "")
    color = config.get("color")
    
    if chart_type == "line":
        if not x or not y:
            raise ValueError("Line chart requires 'x' and 'y' in config")
        
        # Support multiple y columns
        y_cols = [y] if isinstance(y, str) else y
        fig = go.Figure()
        
        for y_col in y_cols:
            if y_col not in df.columns:
                raise ValueError(f"Column '{y_col}' not found in data")
            fig.add_trace(go.Scatter(
                x=df[x],
                y=df[y_col],
                mode='lines+markers',
                name=y_col
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=xlabel,
            yaxis_title=ylabel
        )
    
    elif chart_type == "bar":
        if not x or not y:
            raise ValueError("Bar chart requires 'x' and 'y' in config")
        
        if x not in df.columns or y not in df.columns:
            raise ValueError(f"Columns '{x}' or '{y}' not found in data")
        
        fig = px.bar(df, x=x, y=y, color=color, title=title)
        fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
    
    elif chart_type == "scatter":
        if not x or not y:
            raise ValueError("Scatter chart requires 'x' and 'y' in config")
        
        if x not in df.columns or y not in df.columns:
            raise ValueError(f"Columns '{x}' or '{y}' not found in data")
        
        size = config.get("size")
        fig = px.scatter(df, x=x, y=y, color=color, size=size, title=title)
        fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
    
    elif chart_type == "pie":
        if not x or not y:
            raise ValueError("Pie chart requires 'x' (labels) and 'y' (values) in config")
        
        if x not in df.columns or y not in df.columns:
            raise ValueError(f"Columns '{x}' or '{y}' not found in data")
        
        fig = px.pie(df, names=x, values=y, title=title)
    
    elif chart_type == "heatmap":
        # For heatmap, use all numeric columns or specified columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise ValueError("Heatmap requires at least 2 numeric columns")
        
        corr_matrix = df[numeric_cols].corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0
        ))
        fig.update_layout(title=title)
    
    elif chart_type == "histogram":
        if not x:
            raise ValueError("Histogram requires 'x' in config")
        
        if x not in df.columns:
            raise ValueError(f"Column '{x}' not found in data")
        
        fig = px.histogram(df, x=x, color=color, title=title)
        fig.update_layout(xaxis_title=xlabel, yaxis_title="Count")
    
    elif chart_type == "box":
        if not y:
            raise ValueError("Box plot requires 'y' in config")
        
        if y not in df.columns:
            raise ValueError(f"Column '{y}' not found in data")
        
        fig = px.box(df, x=x, y=y, color=color, title=title)
        fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
    
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
    return fig


def generate_chart(
    data: Dict[str, Any],
    chart_type: str,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build a chart render payload without generating files.

    Args:
        data: Chart data (x/y arrays, labels/values, or series)
        chart_type: Type of chart ('line', 'bar', 'scatter', 'pie', 'heatmap', 'histogram', 'box')
        config: Optional chart configuration (title, labels, colors)

    Returns:
        Dictionary with chart render payload for frontend rendering
    """
    validation_error = validate_string_not_empty(chart_type, "chart_type")
    if validation_error:
        return validation_error

    if not isinstance(data, dict):
        return {
            "status": "error",
            "message": "data must be a dictionary"
        }

    config = config or {}

    return {
        "status": "success",
        "render_type": "chart",
        "chart_type": chart_type,
        "data": data,
        "config": config,
        "render_hint": "frontend",
        "timestamp": datetime.now().isoformat()
    }


def _create_matplotlib_chart(
    df: pd.DataFrame,
    chart_type: str,
    config: Dict[str, Any],
    file_path: str
) -> None:
    """Create static chart using Matplotlib"""
    x = config.get("x")
    y = config.get("y")
    title = config.get("title", f"{chart_type.capitalize()} Chart")
    xlabel = config.get("xlabel", x or "")
    ylabel = config.get("ylabel", y or "")
    figsize = config.get("figsize", (10, 6))
    dpi = config.get("dpi", 300)
    color = config.get("color")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    if chart_type == "line":
        if not x or not y:
            raise ValueError("Line chart requires 'x' and 'y' in config")
        
        # Support multiple y columns
        y_cols = [y] if isinstance(y, str) else y
        
        for y_col in y_cols:
            if y_col not in df.columns:
                raise ValueError(f"Column '{y_col}' not found in data")
            # Use values to avoid recursion issues
            x_data = df[x].values
            y_data = df[y_col].values
            # Note: marker='o' causes recursion issues with Python 3.14 + matplotlib
            ax.plot(x_data, y_data, label=y_col)
        
        if len(y_cols) > 1:
            ax.legend()
    
    elif chart_type == "bar":
        if not x or not y:
            raise ValueError("Bar chart requires 'x' and 'y' in config")
        
        if x not in df.columns or y not in df.columns:
            raise ValueError(f"Columns '{x}' or '{y}' not found in data")
        
        x_data = df[x].values
        y_data = df[y].values
        ax.bar(x_data, y_data)
    
    elif chart_type == "scatter":
        if not x or not y:
            raise ValueError("Scatter chart requires 'x' and 'y' in config")
        
        if x not in df.columns or y not in df.columns:
            raise ValueError(f"Columns '{x}' or '{y}' not found in data")
        
        size = config.get("size")
        sizes = df[size].values * 10 if size and size in df.columns else 50
        
        x_data = df[x].values
        y_data = df[y].values
        
        if color and color in df.columns:
            # Color by category
            for category in df[color].unique():
                mask = df[color] == category
                cat_x = df[x][mask].values
                cat_y = df[y][mask].values
                ax.scatter(cat_x, cat_y, label=str(category), alpha=0.6)
            ax.legend()
        else:
            ax.scatter(x_data, y_data, s=sizes, alpha=0.6)
    
    elif chart_type == "pie":
        if not x or not y:
            raise ValueError("Pie chart requires 'x' (labels) and 'y' (values) in config")
        
        if x not in df.columns or y not in df.columns:
            raise ValueError(f"Columns '{x}' or '{y}' not found in data")
        
        labels = df[x].values
        values = df[y].values
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
    
    elif chart_type == "heatmap":
        # For heatmap, use all numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise ValueError("Heatmap requires at least 2 numeric columns")
        
        corr_matrix = df[numeric_cols].corr()
        im = ax.imshow(corr_matrix.values, cmap='RdBu', aspect='auto', vmin=-1, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(corr_matrix.columns)))
        ax.set_yticks(np.arange(len(corr_matrix.columns)))
        ax.set_xticklabels(corr_matrix.columns.values, rotation=45, ha='right')
        ax.set_yticklabels(corr_matrix.columns.values)
        
        # Add colorbar
        plt.colorbar(im, ax=ax)
        
        # Add correlation values
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=8)
    
    elif chart_type == "histogram":
        if not x:
            raise ValueError("Histogram requires 'x' in config")
        
        if x not in df.columns:
            raise ValueError(f"Column '{x}' not found in data")
        
        bins = config.get("bins", 30)
        x_data = df[x].values
        ax.hist(x_data, bins=bins, edgecolor='black', alpha=0.7)
        ylabel = "Frequency"
    
    elif chart_type == "box":
        if not y:
            raise ValueError("Box plot requires 'y' in config")
        
        if y not in df.columns:
            raise ValueError(f"Column '{y}' not found in data")
        
        if x and x in df.columns:
            # Grouped box plot
            groups = df[x].unique()
            data_to_plot = [df[df[x] == group][y].dropna().values for group in groups]
            ax.boxplot(data_to_plot, tick_labels=groups)
        else:
            # Single box plot
            y_data = df[y].dropna().values
            ax.boxplot(y_data)
    
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
    # Set labels and title
    ax.set_title(title, fontsize=14, fontweight='bold')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    
    # Save figure (skip tight_layout due to Python 3.14 compatibility issues)
    plt.savefig(file_path, dpi=dpi)
    plt.close(fig)


def build_dashboard(
    components: List[Dict[str, Any]],
    layout: Optional[Dict[str, Any]] = None,
    title: str = "Interactive Dashboard",
    output_dir: str = "/tmp"
) -> Dict[str, Any]:
    """
    Build a dashboard render payload with multiple visualizations.
    
    Args:
        components: List of component dictionaries, each containing:
            - type: Component type ('chart', 'table', 'metric', 'text')
            - data: Data for the component (DataFrame or dict)
            - config: Component-specific configuration
            For 'chart' type:
                - chart_type: Type of chart ('line', 'bar', 'scatter', 'pie', etc.)
                - x, y: Column names for axes
                - title: Chart title
            For 'table' type:
                - columns: List of columns to display (optional, defaults to all)
                - max_rows: Maximum rows to display (default: 100)
            For 'metric' type:
                - value: Numeric value to display
                - label: Label for the metric
                - format: Format string (e.g., '${:,.2f}', '{:.1%}')
            For 'text' type:
                - content: Text content (supports HTML)
        layout: Optional layout configuration:
            - columns: Number of columns in grid (default: 2)
            - theme: Color theme ('light', 'dark', default: 'light')
        title: Dashboard title
        output_dir: Ignored (kept for backward compatibility)
        
    Returns:
        Dictionary with dashboard render payload
        
    Example:
        >>> components = [
        ...     {
        ...         "type": "metric",
        ...         "config": {"value": 1250, "label": "Total Sales", "format": "${:,.0f}"}
        ...     },
        ...     {
        ...         "type": "chart",
        ...         "data": df,
        ...         "config": {"chart_type": "line", "x": "date", "y": "sales", "title": "Sales Trend"}
        ...     },
        ...     {
        ...         "type": "table",
        ...         "data": df,
        ...         "config": {"columns": ["date", "sales", "profit"], "max_rows": 10}
        ...     }
        ... ]
        >>> result = build_dashboard(components, title="Sales Dashboard")
        >>> print(result["render_type"])
        dashboard
    """
    try:
        # Validate inputs
        if not components or not isinstance(components, list):
            return {
                "status": "error",
                "message": "components must be a non-empty list"
            }
        
        validation_error = validate_string_not_empty(title, "title")
        if validation_error:
            return validation_error
        
        logger.info(f"Building dashboard with {len(components)} components")
        
        # Default layout
        layout = layout or {}
        columns = layout.get("columns", 2)
        theme = layout.get("theme", "light")
        
        # Validate theme
        if theme not in ["light", "dark"]:
            return {
                "status": "error",
                "message": f"Invalid theme: {theme}. Valid themes: light, dark"
            }
        
        normalized_components = []
        for component in components:
            if not isinstance(component, dict):
                continue
            normalized = dict(component)
            data = normalized.get("data")
            if isinstance(data, pd.DataFrame):
                normalized["data"] = data.to_dict(orient="records")
            normalized_components.append(normalized)

        return {
            "status": "success",
            "render_type": "dashboard",
            "title": title,
            "layout": {"columns": columns, "theme": theme},
            "components": normalized_components,
            "component_count": len(normalized_components),
            "render_hint": "frontend",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error building dashboard: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to build dashboard: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def _generate_dashboard_header(title: str, theme: str) -> str:
    """Generate HTML header with CSS styling"""
    bg_color = "#ffffff" if theme == "light" else "#1a1a1a"
    text_color = "#333333" if theme == "light" else "#e0e0e0"
    card_bg = "#f8f9fa" if theme == "light" else "#2d2d2d"
    border_color = "#dee2e6" if theme == "light" else "#404040"
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: {bg_color};
            color: {text_color};
            padding: 20px;
            line-height: 1.6;
        }}
        
        .dashboard-title {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 30px;
            text-align: center;
            color: {text_color};
        }}
        
        .dashboard-grid {{
            display: grid;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .component {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .component.error {{
            background-color: #fee;
            border-color: #fcc;
            color: #c00;
        }}
        
        .component-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: {text_color};
        }}
        
        .metric-container {{
            text-align: center;
            padding: 20px;
        }}
        
        .metric-value {{
            font-size: 48px;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            font-size: 16px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .table-container {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        th {{
            background-color: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid {border_color};
        }}
        
        tr:hover {{
            background-color: {'#f1f3f5' if theme == 'light' else '#3a3a3a'};
        }}
        
        .text-content {{
            font-size: 14px;
            line-height: 1.8;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid {border_color};
            color: #6c757d;
            font-size: 12px;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr !important;
            }}
        }}
    </style>
</head>
<body>"""


def _generate_chart_component(component: Dict[str, Any], idx: int) -> str:
    """Generate HTML for a chart component using Plotly"""
    data = component.get("data")
    config = component.get("config", {})
    
    # Convert dict to DataFrame if needed
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("Chart component requires 'data' as DataFrame or dictionary")
    
    if df.empty:
        raise ValueError("Chart data is empty")
    
    chart_type = config.get("chart_type", "line")
    x = config.get("x")
    y = config.get("y")
    chart_title = config.get("title", f"Chart {idx + 1}")
    color = config.get("color")
    
    # Create Plotly figure
    fig = _create_plotly_chart(df, chart_type, config)
    
    # Convert to HTML div
    chart_html = fig.to_html(include_plotlyjs=False, div_id=f"chart_{idx}")
    
    return f"""<div class="component">
    <div class="component-title">{chart_title}</div>
    {chart_html}
</div>"""


def _generate_table_component(component: Dict[str, Any], idx: int) -> str:
    """Generate HTML for a table component"""
    data = component.get("data")
    config = component.get("config", {})
    
    # Convert dict to DataFrame if needed
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("Table component requires 'data' as DataFrame or dictionary")
    
    if df.empty:
        raise ValueError("Table data is empty")
    
    table_title = config.get("title", f"Table {idx + 1}")
    columns = config.get("columns", list(df.columns))
    max_rows = config.get("max_rows", 100)
    
    # Filter columns
    df_display = df[columns].head(max_rows)
    
    # Generate table HTML
    table_html = '<div class="table-container"><table>'
    
    # Header
    table_html += '<thead><tr>'
    for col in df_display.columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr></thead>'
    
    # Body
    table_html += '<tbody>'
    for _, row in df_display.iterrows():
        table_html += '<tr>'
        for val in row:
            # Format value
            if pd.isna(val):
                formatted_val = ''
            elif isinstance(val, (int, np.integer)):
                formatted_val = f'{val:,}'
            elif isinstance(val, (float, np.floating)):
                formatted_val = f'{val:,.2f}'
            else:
                formatted_val = str(val)
            table_html += f'<td>{formatted_val}</td>'
        table_html += '</tr>'
    table_html += '</tbody>'
    
    table_html += '</table></div>'
    
    # Add row count info
    if len(df) > max_rows:
        table_html += f'<p style="margin-top: 10px; font-size: 12px; color: #6c757d;">Showing {max_rows} of {len(df)} rows</p>'
    
    return f"""<div class="component">
    <div class="component-title">{table_title}</div>
    {table_html}
</div>"""


def _generate_metric_component(component: Dict[str, Any], idx: int) -> str:
    """Generate HTML for a metric component"""
    config = component.get("config", {})
    
    value = config.get("value")
    label = config.get("label", f"Metric {idx + 1}")
    format_str = config.get("format", "{:,.2f}")
    
    if value is None:
        raise ValueError("Metric component requires 'value' in config")
    
    # Format value
    try:
        if isinstance(format_str, str) and '{' in format_str:
            formatted_value = format_str.format(value)
        else:
            formatted_value = str(value)
    except Exception:
        formatted_value = str(value)
    
    return f"""<div class="component">
    <div class="metric-container">
        <div class="metric-value">{formatted_value}</div>
        <div class="metric-label">{label}</div>
    </div>
</div>"""


def _generate_text_component(component: Dict[str, Any], idx: int) -> str:
    """Generate HTML for a text component"""
    config = component.get("config", {})
    
    content = config.get("content", "")
    text_title = config.get("title", "")
    
    if not content:
        raise ValueError("Text component requires 'content' in config")
    
    title_html = f'<div class="component-title">{text_title}</div>' if text_title else ''
    
    return f"""<div class="component">
    {title_html}
    <div class="text-content">{content}</div>
</div>"""


def _generate_dashboard_footer() -> str:
    """Generate HTML footer"""
    return f"""
    <div class="footer">
        Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | TopFloor AI Platform
    </div>
</body>
</html>"""


# Export all tools
__all__ = [
    "load_dataset",
    "clean_data",
    "analyze_data",
    "create_visualization",
    "generate_chart",
    "build_dashboard"
]
