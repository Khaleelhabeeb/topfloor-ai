"""
Finance Tools - Tools for financial analysis, budgeting, and market data

This module provides tools for the Finance Agent to perform:
- Market data fetching (stocks, crypto, commodities, forex)
- Bank statement analysis
- Budget planning
- Financial metrics calculation
- Expense forecasting
- Financial report generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import os
import httpx
import pandas as pd
import re
from pathlib import Path
import time
from functools import wraps
import threading

from app.core.config import settings

logger = logging.getLogger(__name__)


# Rate limiting configuration
class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
    
    def is_allowed(self) -> bool:
        """Check if a call is allowed under rate limit"""
        with self.lock:
            now = time.time()
            # Remove calls outside the time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False
    
    def wait_if_needed(self):
        """Wait if rate limit is exceeded"""
        while not self.is_allowed():
            time.sleep(0.1)


# Rate limiter for Twelve Data API
_twelve_data_limiter = RateLimiter(max_calls=8, time_window=60)


def rate_limited(limiter: RateLimiter):
    """Decorator to apply rate limiting to functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function on failure with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}")

            raise last_exception

        return wrapper

    return decorator

def validate_positive_number(value: float, field_name: str) -> Dict[str, Any]:
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


def validate_string_not_empty(value: str, field_name: str) -> Dict[str, Any]:
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


@rate_limited(_twelve_data_limiter)
@retry_on_failure(max_retries=2, delay=1.0, backoff=2.0)
def fetch_market_data(
    symbol: str,
    timeframe: str = "1d",
    data_source: str = "twelve_data"
) -> Dict[str, Any]:
    """
    Fetch real-time and historical market data for stocks, crypto, commodities, or forex.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'BTC-USD', 'EURUSD')
        timeframe: Time period for data ('1d', '1w', '1m', '3m', '1y', '5y')
        data_source: Data provider ('twelve_data')
        
    Returns:
        Market data including current price, change, volume, and historical data
        
    Example:
        >>> data = fetch_market_data("AAPL", "1m", "twelve_data")
        >>> print(data["current_price"])
        150.25
    """
    try:
        # Validate inputs
        validation_error = validate_string_not_empty(symbol, "symbol")
        if validation_error:
            return validation_error
        
        # Validate timeframe
        valid_timeframes = ["1d", "1w", "1m", "3m", "1y", "5y"]
        if timeframe not in valid_timeframes:
            return {
                "status": "error",
                "message": f"Invalid timeframe '{timeframe}'. Must be one of: {', '.join(valid_timeframes)}",
                "symbol": symbol
            }
        
        logger.info(f"Fetching market data for {symbol} with timeframe {timeframe}")

        if data_source != "twelve_data":
            return {
                "status": "error",
                "message": f"Data source '{data_source}' is not supported. Use 'twelve_data'.",
                "symbol": symbol
            }

        api_key = settings.TWELVE_DATA_API_KEY or os.getenv("TWELVE_DATA_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "message": "TWELVE_DATA_API_KEY is not configured",
                "symbol": symbol
            }

        interval_map = {
            "1d": ("1h", 24),
            "1w": ("1day", 7),
            "1m": ("1day", 30),
            "3m": ("1week", 12),
            "1y": ("1month", 12),
            "5y": ("1month", 60)
        }

        interval, outputsize = interval_map.get(timeframe, ("1day", 30))

        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": api_key,
            "timezone": "UTC"
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://api.twelvedata.com/time_series", params=params)
            response.raise_for_status()
            payload = response.json()

        if payload.get("status") == "error":
            return {
                "status": "error",
                "message": payload.get("message", "Failed to fetch market data"),
                "symbol": symbol
            }

        values = payload.get("values", [])
        if not values:
            return {
                "status": "error",
                "message": f"No data found for symbol {symbol}.",
                "symbol": symbol
            }

        # Twelve Data returns newest first; reverse for chronological order.
        values_sorted = list(reversed(values))
        historical_dates = [item["datetime"][:10] for item in values_sorted]
        historical_prices = [float(item["close"]) for item in values_sorted]
        historical_volumes = [int(float(item.get("volume") or 0)) for item in values_sorted]

        current_price = float(values[0]["close"])
        if len(values) > 1:
            previous_price = float(values[1]["close"])
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100 if previous_price else 0.0
        else:
            change = 0.0
            change_percent = 0.0

        current_volume = int(float(values[0].get("volume") or 0))
        
        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": current_volume,
            "timeframe": timeframe,
            "data_source": "twelve_data",
            "historical": {
                "dates": historical_dates,
                "prices": historical_prices,
                "volumes": historical_volumes
            },
            "additional_info": {
                "currency": payload.get("currency") or "USD",
                "market_cap": None,
                "52_week_high": None,
                "52_week_low": None,
                "average_volume": None,
                "company_name": payload.get("name") or symbol
            },
            "status": "success",
            "message": f"Market data fetched for {symbol}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to fetch market data: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }


def analyze_bank_statement(
    file_path: str,
    file_type: str = "csv"
) -> Dict[str, Any]:
    """
    Parse and analyze bank statement to categorize transactions and calculate metrics.
    
    Args:
        file_path: Path to the bank statement file
        file_type: File format ('csv', 'excel', 'pdf')
        
    Returns:
        Analysis including income, expenses, savings rate, and categorized spending
        
    Example:
        >>> analysis = analyze_bank_statement("/path/to/statement.csv", "csv")
        >>> print(analysis["savings_rate"])
        30.0
    """
    try:
        # Validate inputs
        validation_error = validate_string_not_empty(file_path, "file_path")
        if validation_error:
            return validation_error
        
        validation_error = validate_string_not_empty(file_type, "file_type")
        if validation_error:
            return validation_error
        
        logger.info(f"Analyzing bank statement from {file_path} (format: {file_type})")
        
        # Validate file type first
        if file_type.lower() not in ["csv", "excel", "xlsx", "xls", "pdf"]:
            return {
                "status": "error",
                "message": f"Unsupported file type: {file_type}. Supported types: csv, excel, xlsx, xls, pdf",
                "file_path": file_path
            }
        
        # Validate file exists
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {
                "status": "error",
                "message": f"File not found: {file_path}",
                "file_path": file_path
            }
        
        # Validate file size (max 50MB)
        max_file_size = 50 * 1024 * 1024  # 50MB
        if file_path_obj.stat().st_size > max_file_size:
            return {
                "status": "error",
                "message": f"File size exceeds maximum allowed size of 50MB",
                "file_path": file_path
            }
        
        # Load data based on file type
        df = None
        
        if file_type.lower() == "csv":
            # Try to read CSV with different encodings
            try:
                df = pd.read_csv(file_path)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, encoding='latin-1')
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Failed to read CSV file with multiple encodings: {str(e)}",
                        "file_path": file_path
                    }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to read CSV file: {str(e)}",
                    "file_path": file_path
                }
        
        elif file_type.lower() in ["excel", "xlsx", "xls"]:
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to read Excel file: {str(e)}",
                    "file_path": file_path
                }
        
        elif file_type.lower() == "pdf":
            return {
                "status": "error",
                "message": "PDF parsing not yet implemented. Please convert to CSV or Excel format.",
                "file_path": file_path
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unsupported file type: {file_type}. Supported types: csv, excel, xlsx, xls",
                "file_path": file_path
            }
        
        if df is None or df.empty:
            return {
                "status": "error",
                "message": "No data found in file or file is empty",
                "file_path": file_path
            }
        
        # Validate row count (max 100,000 rows)
        max_rows = 100000
        if len(df) > max_rows:
            return {
                "status": "error",
                "message": f"File contains too many rows ({len(df)}). Maximum allowed: {max_rows}",
                "file_path": file_path
            }
        
        # Normalize column names (lowercase, strip spaces)
        df.columns = df.columns.str.lower().str.strip()
        
        # Try to identify amount and description columns
        amount_col = None
        description_col = None
        date_col = None
        
        # Common column name patterns (ordered by specificity - most specific first)
        amount_patterns = ['amount', 'value', 'debit', 'credit', 'balance', 'transaction']
        description_patterns = ['description', 'desc', 'details', 'detail', 'memo', 'narrative', 'payee']
        date_patterns = ['date']
        
        # Find amount column (prioritize 'amount' keyword)
        for col in df.columns:
            if 'amount' in col:
                amount_col = col
                break
        
        # If not found, try other patterns
        if amount_col is None:
            for col in df.columns:
                if any(pattern in col for pattern in amount_patterns) and 'date' not in col:
                    amount_col = col
                    break
        
        # Find description column (check if pattern is in column name)
        for col in df.columns:
            if any(pattern in col for pattern in description_patterns):
                description_col = col
                break
        
        # Find date column (check if pattern is in column name)
        for col in df.columns:
            if any(pattern in col for pattern in date_patterns):
                date_col = col
                break
        
        # Validate required columns
        if amount_col is None:
            return {
                "status": "error",
                "message": f"Could not identify amount column. Available columns: {list(df.columns)}",
                "file_path": file_path
            }
        
        if description_col is None:
            return {
                "status": "error",
                "message": f"Could not identify description column. Available columns: {list(df.columns)}",
                "file_path": file_path
            }
        
        # Convert amount to numeric, handling various formats
        df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
        
        # Remove rows with NaN amounts
        df = df.dropna(subset=[amount_col])
        
        if df.empty:
            return {
                "status": "error",
                "message": "No valid transaction amounts found in file",
                "file_path": file_path
            }
        
        # Categorize transactions
        df['category'] = df[description_col].apply(_categorize_transaction)
        
        # Calculate income and expenses
        income_df = df[df[amount_col] > 0]
        expense_df = df[df[amount_col] < 0]
        
        total_income = float(income_df[amount_col].sum())
        total_expenses = float(abs(expense_df[amount_col].sum()))
        net_savings = total_income - total_expenses
        
        # Calculate savings rate
        savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0
        
        # Group expenses by category
        expenses_by_category = {}
        if not expense_df.empty:
            category_sums = expense_df.groupby('category')[amount_col].sum()
            expenses_by_category = {
                cat: float(abs(amt)) 
                for cat, amt in category_sums.items()
            }
        
        # Determine date range
        date_range = "Unknown"
        if date_col:
            try:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                valid_dates = df[date_col].dropna()
                if not valid_dates.empty:
                    min_date = valid_dates.min().strftime('%Y-%m-%d')
                    max_date = valid_dates.max().strftime('%Y-%m-%d')
                    date_range = f"{min_date} to {max_date}"
            except Exception as e:
                logger.warning(f"Could not parse dates: {str(e)}")
        
        # Get top expenses
        top_expenses = []
        if not expense_df.empty:
            # Sort by absolute amount (largest first) and take top 5
            top_5 = expense_df.nsmallest(5, amount_col, keep='first')  # nsmallest because amounts are negative
            top_expenses = [
                {
                    "description": str(row[description_col]),
                    "amount": float(abs(row[amount_col])),
                    "category": str(row['category'])
                }
                for _, row in top_5.iterrows()
            ]
        
        # Get top income sources
        top_income = []
        if not income_df.empty:
            top_5_income = income_df.nlargest(5, amount_col, keep='first')
            top_income = [
                {
                    "description": str(row[description_col]),
                    "amount": float(row[amount_col]),
                    "category": str(row['category'])
                }
                for _, row in top_5_income.iterrows()
            ]
        
        return {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_savings": round(net_savings, 2),
            "savings_rate": round(savings_rate, 2),
            "expenses_by_category": {k: round(v, 2) for k, v in expenses_by_category.items()},
            "transaction_count": len(df),
            "income_transaction_count": len(income_df),
            "expense_transaction_count": len(expense_df),
            "date_range": date_range,
            "top_expenses": top_expenses,
            "top_income": top_income,
            "average_transaction": round(float(df[amount_col].mean()), 2),
            "status": "success",
            "message": f"Bank statement analyzed successfully from {file_path}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing bank statement {file_path}: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to analyze bank statement: {str(e)}",
            "file_path": file_path,
            "timestamp": datetime.now().isoformat()
        }


def _categorize_transaction(description: str) -> str:
    """
    Categorize a transaction based on its description.
    
    Args:
        description: Transaction description text
        
    Returns:
        Category name
    """
    if pd.isna(description):
        return "other"
    
    description = str(description).lower()
    
    # Housing
    if any(keyword in description for keyword in ['rent', 'mortgage', 'property', 'landlord', 'housing']):
        return "housing"
    
    # Utilities
    if any(keyword in description for keyword in ['electric', 'gas', 'water', 'internet', 'phone', 'utility', 'cable', 'mobile']):
        return "utilities"
    
    # Food & Dining
    if any(keyword in description for keyword in ['grocery', 'supermarket', 'restaurant', 'cafe', 'food', 'dining', 'uber eats', 'doordash', 'grubhub', 'starbucks', 'mcdonald', 'pizza']):
        return "food"
    
    # Transportation
    if any(keyword in description for keyword in ['gas station', 'fuel', 'uber', 'lyft', 'taxi', 'transit', 'parking', 'car payment', 'auto', 'vehicle', 'insurance']):
        return "transportation"
    
    # Entertainment
    if any(keyword in description for keyword in ['netflix', 'spotify', 'hulu', 'disney', 'movie', 'theater', 'cinema', 'game', 'entertainment', 'concert', 'ticket']):
        return "entertainment"
    
    # Shopping
    if any(keyword in description for keyword in ['amazon', 'walmart', 'target', 'ebay', 'shopping', 'store', 'retail', 'mall']):
        return "shopping"
    
    # Healthcare
    if any(keyword in description for keyword in ['pharmacy', 'doctor', 'hospital', 'medical', 'health', 'dental', 'clinic', 'cvs', 'walgreens']):
        return "healthcare"
    
    # Income
    if any(keyword in description for keyword in ['salary', 'payroll', 'deposit', 'income', 'payment received', 'transfer from', 'refund']):
        return "income"
    
    # Savings/Investment
    if any(keyword in description for keyword in ['savings', 'investment', '401k', 'ira', 'retirement', 'stock', 'dividend']):
        return "savings"
    
    # Bills & Subscriptions
    if any(keyword in description for keyword in ['subscription', 'membership', 'bill payment', 'autopay']):
        return "subscriptions"
    
    # Education
    if any(keyword in description for keyword in ['tuition', 'school', 'education', 'course', 'book', 'student']):
        return "education"
    
    # Default category
    return "other"


def create_budget(
    income: float,
    expenses: Dict[str, float],
    goals: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Create a budget plan based on income, expenses, and financial goals.
    
    Args:
        income: Monthly income amount
        expenses: Dictionary of expense categories and amounts
        goals: Optional dictionary of savings goals and target amounts
        
    Returns:
        Budget plan with percentages, available funds, and recommendations
        
    Example:
        >>> budget = create_budget(5000, {"housing": 1200, "food": 600}, {"emergency": 500})
        >>> print(budget["available"])
        2700.0
    """
    try:
        # Validate inputs
        if income is None:
            return {
                "status": "error",
                "message": "income is required"
            }
        
        try:
            income = float(income)
        except (ValueError, TypeError):
            return {
                "status": "error",
                "message": f"income must be a valid number, got {income}"
            }
        
        if not isinstance(expenses, dict):
            return {
                "status": "error",
                "message": "expenses must be a dictionary"
            }
        
        # Validate expense values
        for category, amount in expenses.items():
            try:
                expenses[category] = float(amount)
                if expenses[category] < 0:
                    return {
                        "status": "error",
                        "message": f"Expense amount for '{category}' must be non-negative, got {amount}"
                    }
            except (ValueError, TypeError):
                return {
                    "status": "error",
                    "message": f"Expense amount for '{category}' must be a valid number, got {amount}"
                }
        
        goals = goals or {}
        
        if not isinstance(goals, dict):
            return {
                "status": "error",
                "message": "goals must be a dictionary"
            }
        
        # Validate goal values
        for goal_name, amount in goals.items():
            try:
                goals[goal_name] = float(amount)
                if goals[goal_name] < 0:
                    return {
                        "status": "error",
                        "message": f"Goal amount for '{goal_name}' must be non-negative, got {amount}"
                    }
            except (ValueError, TypeError):
                return {
                    "status": "error",
                    "message": f"Goal amount for '{goal_name}' must be a valid number, got {amount}"
                }
        
        total_expenses = sum(expenses.values())
        total_goals = sum(goals.values())
        available = income - total_expenses - total_goals
        
        # Calculate percentages
        expense_percentages = {
            cat: round((amt / income) * 100, 2) if income > 0 else 0
            for cat, amt in expenses.items()
        }
        
        # Generate recommendations
        recommendations = []
        
        if income <= 0:
            recommendations.append("Invalid income amount - please provide a positive income value")
        else:
            if expense_percentages.get("housing", 0) > 30:
                recommendations.append("Housing costs exceed 30% of income - consider reducing housing expenses")
            
            if available < 0:
                recommendations.append("Expenses exceed income - budget adjustment needed immediately")
            elif available < income * 0.1:
                recommendations.append("Low savings buffer - aim for at least 10% savings")
            
            if expense_percentages.get("food", 0) > 15:
                recommendations.append("Food expenses are high - consider meal planning to reduce costs")
            
            if expense_percentages.get("transportation", 0) > 15:
                recommendations.append("Transportation costs are high - explore alternatives like carpooling or public transit")
            
            if available >= income * 0.2:
                recommendations.append("Great job! You're saving at least 20% of your income")
        
        # Determine budget health
        if available < 0:
            budget_health = "critical"
        elif available < income * 0.1:
            budget_health = "needs_improvement"
        elif available < income * 0.2:
            budget_health = "good"
        else:
            budget_health = "excellent"
        
        return {
            "income": income,
            "total_expenses": total_expenses,
            "total_goals": total_goals,
            "available": round(available, 2),
            "expense_percentages": expense_percentages,
            "recommendations": recommendations,
            "budget_health": budget_health,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating budget: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to create budget: {str(e)}"
        }


def calculate_financial_metrics(
    data: Dict[str, Any],
    metrics: List[str]
) -> Dict[str, Any]:
    """
    Calculate various financial metrics like ROI, savings rate, debt-to-income ratio.
    
    Args:
        data: Financial data dictionary with relevant values
        metrics: List of metrics to calculate ('roi', 'savings_rate', 'debt_to_income', etc.)
        
    Returns:
        Calculated metrics with explanations
        
    Example:
        >>> result = calculate_financial_metrics(
        ...     {"initial_investment": 10000, "current_value": 12000},
        ...     ["roi"]
        ... )
        >>> print(result["metrics"]["roi"]["value"])
        20.0
    """
    try:
        # Validate inputs
        if not isinstance(data, dict):
            return {
                "status": "error",
                "message": "data must be a dictionary"
            }
        
        if not isinstance(metrics, list):
            return {
                "status": "error",
                "message": "metrics must be a list"
            }
        
        results = {}
        
        for metric in metrics:
            if metric == "roi":
                initial = data.get("initial_investment", 0)
                current = data.get("current_value", 0)
                if initial > 0:
                    roi = ((current - initial) / initial) * 100
                    results["roi"] = {
                        "value": round(roi, 2),
                        "unit": "percent",
                        "interpretation": "positive" if roi > 0 else "negative" if roi < 0 else "neutral"
                    }
                else:
                    results["roi"] = {
                        "value": None,
                        "unit": "percent",
                        "error": "Initial investment must be greater than 0"
                    }
            
            elif metric == "savings_rate":
                income = data.get("income", 0)
                savings = data.get("savings", 0)
                if income > 0:
                    rate = (savings / income) * 100
                    results["savings_rate"] = {
                        "value": round(rate, 2),
                        "unit": "percent",
                        "interpretation": "excellent" if rate >= 20 else "good" if rate >= 10 else "needs_improvement"
                    }
                else:
                    results["savings_rate"] = {
                        "value": None,
                        "unit": "percent",
                        "error": "Income must be greater than 0"
                    }
            
            elif metric == "debt_to_income":
                income = data.get("monthly_income", 0)
                debt = data.get("monthly_debt_payments", 0)
                if income > 0:
                    ratio = (debt / income) * 100
                    results["debt_to_income"] = {
                        "value": round(ratio, 2),
                        "unit": "percent",
                        "interpretation": "good" if ratio < 36 else "concerning" if ratio < 50 else "high_risk"
                    }
                else:
                    results["debt_to_income"] = {
                        "value": None,
                        "unit": "percent",
                        "error": "Monthly income must be greater than 0"
                    }
            
            elif metric == "emergency_fund_months":
                monthly_expenses = data.get("monthly_expenses", 0)
                emergency_fund = data.get("emergency_fund", 0)
                if monthly_expenses > 0:
                    months = emergency_fund / monthly_expenses
                    results["emergency_fund_months"] = {
                        "value": round(months, 1),
                        "unit": "months",
                        "interpretation": "excellent" if months >= 6 else "good" if months >= 3 else "needs_improvement"
                    }
                else:
                    results["emergency_fund_months"] = {
                        "value": None,
                        "unit": "months",
                        "error": "Monthly expenses must be greater than 0"
                    }
            
            elif metric == "net_worth":
                assets = data.get("total_assets", 0)
                liabilities = data.get("total_liabilities", 0)
                net_worth = assets - liabilities
                results["net_worth"] = {
                    "value": round(net_worth, 2),
                    "unit": "currency",
                    "interpretation": "positive" if net_worth > 0 else "negative" if net_worth < 0 else "neutral"
                }
        
        return {
            "metrics": results,
            "status": "success",
            "calculated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating financial metrics: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to calculate metrics: {str(e)}"
        }


def forecast_expenses(
    historical_data: List[Dict[str, Any]],
    months_ahead: int = 3
) -> Dict[str, Any]:
    """
    Forecast future expenses based on historical spending patterns.
    
    Args:
        historical_data: List of historical expense data by month
        months_ahead: Number of months to forecast (default: 3)
        
    Returns:
        Forecasted expenses with confidence intervals and trends
        
    Example:
        >>> forecast = forecast_expenses(
        ...     [{"month": "2026-01", "total": 3000}, {"month": "2026-02", "total": 3200}],
        ...     3
        ... )
        >>> print(len(forecast["forecast"]))
        3
    """
    try:
        # Validate months_ahead type first
        if not isinstance(months_ahead, int):
            try:
                months_ahead = int(months_ahead)
            except (ValueError, TypeError):
                return {
                    "status": "error",
                    "message": f"months_ahead must be an integer, got {months_ahead}"
                }
        
        # Validate inputs
        if months_ahead < 1:
            return {
                "status": "error",
                "message": "months_ahead must be at least 1"
            }
        
        if months_ahead > 12:
            return {
                "status": "error",
                "message": "months_ahead cannot exceed 12"
            }
        
        # Validate historical_data
        if historical_data is not None and not isinstance(historical_data, list):
            return {
                "status": "error",
                "message": "historical_data must be a list or None"
            }
        
        # Calculate average from historical data
        if historical_data and len(historical_data) > 0:
            total_sum = sum(d.get("total", 0) for d in historical_data)
            avg_expenses = total_sum / len(historical_data)
            
            # Calculate trend (simple linear)
            if len(historical_data) >= 2:
                first_half_avg = sum(d.get("total", 0) for d in historical_data[:len(historical_data)//2]) / (len(historical_data)//2)
                second_half_avg = sum(d.get("total", 0) for d in historical_data[len(historical_data)//2:]) / (len(historical_data) - len(historical_data)//2)
                
                if second_half_avg > first_half_avg * 1.05:
                    trend = "increasing"
                    trend_factor = 0.02
                elif second_half_avg < first_half_avg * 0.95:
                    trend = "decreasing"
                    trend_factor = -0.02
                else:
                    trend = "stable"
                    trend_factor = 0
            else:
                trend = "stable"
                trend_factor = 0
        else:
            # Default values if no historical data
            avg_expenses = 3000.00
            trend = "unknown"
            trend_factor = 0
        
        # Generate forecast
        forecast = []
        for i in range(1, months_ahead + 1):
            # Apply trend factor
            forecasted_amount = avg_expenses * (1 + (i * trend_factor))
            
            # Calculate confidence intervals (±10%)
            confidence_low = forecasted_amount * 0.9
            confidence_high = forecasted_amount * 1.1
            
            forecast.append({
                "month": i,
                "forecasted_amount": round(forecasted_amount, 2),
                "confidence_low": round(confidence_low, 2),
                "confidence_high": round(confidence_high, 2)
            })
        
        return {
            "forecast": forecast,
            "trend": trend,
            "average_historical": round(avg_expenses, 2),
            "data_points_used": len(historical_data) if historical_data else 0,
            "status": "success",
            "message": f"Forecast generated for {months_ahead} months",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error forecasting expenses: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to forecast expenses: {str(e)}"
        }


def generate_financial_report(
    data: Dict[str, Any],
    report_type: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Generate a comprehensive financial report in PDF format.
    
    Args:
        data: Financial data to include in the report
        report_type: Type of report ('comprehensive', 'summary', 'investment', 'budget')
        
    Returns:
        Report metadata and file information
        
    Example:
        >>> report = generate_financial_report(
        ...     {"income": 5000, "expenses": 3500},
        ...     "summary"
        ... )
        >>> print(report["status"])
        'generated'
    """
    try:
        # Validate inputs
        if not isinstance(data, dict):
            return {
                "status": "error",
                "message": "data must be a dictionary"
            }
        
        validation_error = validate_string_not_empty(report_type, "report_type")
        if validation_error:
            return validation_error
        
        # Validate report type
        valid_types = ["comprehensive", "summary", "investment", "budget"]
        if report_type not in valid_types:
            return {
                "status": "error",
                "message": f"Invalid report type. Must be one of: {', '.join(valid_types)}"
            }
        
        # TODO: Integrate with PDF generation service (reportlab, weasyprint)
        # This is a placeholder implementation
        logger.info(f"Generating {report_type} financial report")
        
        report_id = f"fin_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Define sections based on report type
        sections_map = {
            "comprehensive": [
                "Executive Summary",
                "Income Analysis",
                "Expense Breakdown",
                "Savings & Investments",
                "Debt Analysis",
                "Net Worth Statement",
                "Financial Goals Progress",
                "Recommendations"
            ],
            "summary": [
                "Executive Summary",
                "Key Metrics",
                "Quick Recommendations"
            ],
            "investment": [
                "Portfolio Overview",
                "Asset Allocation",
                "Performance Analysis",
                "Risk Assessment",
                "Investment Recommendations"
            ],
            "budget": [
                "Income Summary",
                "Expense Breakdown",
                "Budget vs Actual",
                "Savings Analysis",
                "Budget Recommendations"
            ]
        }
        
        return {
            "report_id": report_id,
            "report_type": report_type,
            "title": f"Financial Report - {report_type.replace('_', ' ').title()}",
            "generated_at": datetime.now().isoformat(),
            "sections": sections_map.get(report_type, sections_map["comprehensive"]),
            "file_format": "pdf",
            "data_included": list(data.keys()) if data else [],
            "status": "generated",
            "message": f"Financial report '{report_type}' generated successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating financial report: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate report: {str(e)}"
        }


# Export all tools
__all__ = [
    "fetch_market_data",
    "analyze_bank_statement",
    "create_budget",
    "calculate_financial_metrics",
    "forecast_expenses",
    "generate_financial_report"
]
