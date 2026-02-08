"""
Tests for Finance Tools - Error Handling and Rate Limiting
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
import tempfile
import os
from pathlib import Path
from app.tools.finance_tools import (
    fetch_market_data,
    analyze_bank_statement,
    create_budget,
    calculate_financial_metrics,
    forecast_expenses,
    generate_financial_report,
    RateLimiter,
    validate_positive_number,
    validate_string_not_empty
)


class TestRateLimiter:
    """Tests for RateLimiter class"""
    
    def test_rate_limiter_allows_calls_within_limit(self):
        """Test that rate limiter allows calls within the limit"""
        limiter = RateLimiter(max_calls=5, time_window=1)
        
        # Should allow 5 calls
        for _ in range(5):
            assert limiter.is_allowed() is True
        
        # 6th call should be denied
        assert limiter.is_allowed() is False
    
    def test_rate_limiter_resets_after_time_window(self):
        """Test that rate limiter resets after time window"""
        import time
        limiter = RateLimiter(max_calls=2, time_window=1)
        
        # Use up the limit
        assert limiter.is_allowed() is True
        assert limiter.is_allowed() is True
        assert limiter.is_allowed() is False
        
        # Wait for time window to pass
        time.sleep(1.1)
        
        # Should allow calls again
        assert limiter.is_allowed() is True


class TestValidationHelpers:
    """Tests for validation helper functions"""
    
    def test_validate_positive_number_valid(self):
        """Test validation of valid positive number"""
        result = validate_positive_number(100.0, "test_field")
        assert result is None
    
    def test_validate_positive_number_zero(self):
        """Test validation of zero (should be valid)"""
        result = validate_positive_number(0.0, "test_field")
        assert result is None
    
    def test_validate_positive_number_negative(self):
        """Test validation of negative number"""
        result = validate_positive_number(-10.0, "test_field")
        assert result is not None
        assert result["status"] == "error"
        assert "non-negative" in result["message"]
    
    def test_validate_positive_number_none(self):
        """Test validation of None value"""
        result = validate_positive_number(None, "test_field")
        assert result is not None
        assert result["status"] == "error"
        assert "required" in result["message"]
    
    def test_validate_positive_number_invalid_type(self):
        """Test validation of invalid type"""
        result = validate_positive_number("not_a_number", "test_field")
        assert result is not None
        assert result["status"] == "error"
        assert "valid number" in result["message"]
    
    def test_validate_string_not_empty_valid(self):
        """Test validation of valid non-empty string"""
        result = validate_string_not_empty("valid_string", "test_field")
        assert result is None
    
    def test_validate_string_not_empty_empty(self):
        """Test validation of empty string"""
        result = validate_string_not_empty("", "test_field")
        assert result is not None
        assert result["status"] == "error"
        assert "required" in result["message"]
    
    def test_validate_string_not_empty_whitespace(self):
        """Test validation of whitespace-only string"""
        result = validate_string_not_empty("   ", "test_field")
        assert result is not None
        assert result["status"] == "error"
    
    def test_validate_string_not_empty_none(self):
        """Test validation of None value"""
        result = validate_string_not_empty(None, "test_field")
        assert result is not None
        assert result["status"] == "error"


class TestFetchMarketDataErrorHandling:
    """Tests for fetch_market_data error handling"""
    
    def test_fetch_market_data_empty_symbol(self):
        """Test fetching market data with empty symbol"""
        result = fetch_market_data("", "1m", "yahoo")
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_fetch_market_data_invalid_timeframe(self):
        """Test fetching market data with invalid timeframe"""
        result = fetch_market_data("AAPL", "invalid_timeframe", "yahoo")
        
        assert result["status"] == "error"
        assert "invalid timeframe" in result["message"].lower()
    
    def test_fetch_market_data_rate_limiting(self):
        """Test that rate limiting is applied to fetch_market_data"""
        from app.tools.finance_tools import yahoo_finance_limiter
        
        # Reset the rate limiter
        yahoo_finance_limiter.calls = []
        
        # The rate limiter allows 30 calls per 60 seconds
        # We'll just verify that the rate limiter is being used
        # by checking that calls are tracked
        
        with patch('app.tools.finance_tools.yf.Ticker') as mock_ticker:
            dates = pd.date_range(end=datetime.now(), periods=10, freq='D')
            mock_hist = pd.DataFrame({
                'Close': [150.0 + i for i in range(10)],
                'Volume': [50000000 + i * 1000000 for i in range(10)]
            }, index=dates)
            
            mock_info = {'currency': 'USD', 'longName': 'Apple Inc.'}
            
            mock_ticker_instance = MagicMock()
            mock_ticker_instance.history.return_value = mock_hist
            mock_ticker_instance.info = mock_info
            mock_ticker.return_value = mock_ticker_instance
            
            # Make a few calls
            for _ in range(3):
                result = fetch_market_data("AAPL", "1m", "yahoo")
                assert result["status"] == "success"
            
            # Verify calls were tracked by rate limiter
            assert len(yahoo_finance_limiter.calls) >= 3


class TestAnalyzeBankStatementErrorHandling:
    """Tests for analyze_bank_statement error handling"""
    
    def test_analyze_bank_statement_empty_file_path(self):
        """Test analyzing bank statement with empty file path"""
        result = analyze_bank_statement("", "csv")
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_analyze_bank_statement_empty_file_type(self):
        """Test analyzing bank statement with empty file type"""
        result = analyze_bank_statement("/path/to/file.csv", "")
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_analyze_bank_statement_file_size_limit(self):
        """Test analyzing bank statement with file exceeding size limit"""
        # Create a large temporary file (> 50MB)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Write header
            f.write("Date,Description,Amount\n")
            # Write many rows to exceed 50MB
            for i in range(2000000):  # This should create a file > 50MB
                f.write(f"2026-01-01,Transaction {i},100.00\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            # Should fail due to file size
            assert result["status"] == "error"
            assert "size" in result["message"].lower() or "exceed" in result["message"].lower()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_analyze_bank_statement_corrupted_csv(self):
        """Test analyzing corrupted CSV file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Write invalid CSV content
            f.write("This is not a valid CSV file\n")
            f.write("Random text without proper structure\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            # Should handle gracefully
            assert result["status"] == "error"
        finally:
            os.unlink(temp_path)
    
    def test_analyze_bank_statement_too_many_rows(self):
        """Test analyzing bank statement with too many rows"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Description,Amount\n")
            # Write more than 100,000 rows
            for i in range(100001):
                f.write(f"2026-01-01,Transaction {i},100.00\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            # Should fail due to row count
            assert result["status"] == "error"
            assert "too many rows" in result["message"].lower()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestCreateBudgetErrorHandling:
    """Tests for create_budget error handling"""
    
    def test_create_budget_none_income(self):
        """Test creating budget with None income"""
        result = create_budget(None, {"housing": 1000.0})
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_create_budget_invalid_income_type(self):
        """Test creating budget with invalid income type"""
        result = create_budget("not_a_number", {"housing": 1000.0})
        
        assert result["status"] == "error"
        assert "valid number" in result["message"].lower()
    
    def test_create_budget_expenses_not_dict(self):
        """Test creating budget with expenses not being a dictionary"""
        result = create_budget(5000.0, "not_a_dict")
        
        assert result["status"] == "error"
        assert "dictionary" in result["message"].lower()
    
    def test_create_budget_negative_expense(self):
        """Test creating budget with negative expense amount"""
        result = create_budget(5000.0, {"housing": -1000.0})
        
        assert result["status"] == "error"
        assert "non-negative" in result["message"].lower()
    
    def test_create_budget_invalid_expense_amount(self):
        """Test creating budget with invalid expense amount"""
        result = create_budget(5000.0, {"housing": "not_a_number"})
        
        assert result["status"] == "error"
        assert "valid number" in result["message"].lower()
    
    def test_create_budget_goals_not_dict(self):
        """Test creating budget with goals not being a dictionary"""
        result = create_budget(5000.0, {"housing": 1000.0}, goals="not_a_dict")
        
        assert result["status"] == "error"
        assert "dictionary" in result["message"].lower()
    
    def test_create_budget_negative_goal(self):
        """Test creating budget with negative goal amount"""
        result = create_budget(5000.0, {"housing": 1000.0}, goals={"emergency": -500.0})
        
        assert result["status"] == "error"
        assert "non-negative" in result["message"].lower()
    
    def test_create_budget_invalid_goal_amount(self):
        """Test creating budget with invalid goal amount"""
        result = create_budget(5000.0, {"housing": 1000.0}, goals={"emergency": "not_a_number"})
        
        assert result["status"] == "error"
        assert "valid number" in result["message"].lower()


class TestCalculateFinancialMetricsErrorHandling:
    """Tests for calculate_financial_metrics error handling"""
    
    def test_calculate_metrics_data_not_dict(self):
        """Test calculating metrics with data not being a dictionary"""
        result = calculate_financial_metrics("not_a_dict", ["roi"])
        
        assert result["status"] == "error"
        assert "dictionary" in result["message"].lower()
    
    def test_calculate_metrics_metrics_not_list(self):
        """Test calculating metrics with metrics not being a list"""
        result = calculate_financial_metrics({"income": 5000.0}, "not_a_list")
        
        assert result["status"] == "error"
        assert "list" in result["message"].lower()


class TestForecastExpensesErrorHandling:
    """Tests for forecast_expenses error handling"""
    
    def test_forecast_expenses_invalid_months_ahead_type(self):
        """Test forecasting with invalid months_ahead type"""
        result = forecast_expenses([{"month": "2026-01", "total": 3000.0}], months_ahead="not_an_int")
        
        assert result["status"] == "error"
        assert "integer" in result["message"].lower()
    
    def test_forecast_expenses_historical_data_not_list(self):
        """Test forecasting with historical_data not being a list"""
        result = forecast_expenses("not_a_list", months_ahead=3)
        
        assert result["status"] == "error"
        assert "list" in result["message"].lower()


class TestGenerateFinancialReportErrorHandling:
    """Tests for generate_financial_report error handling"""
    
    def test_generate_report_data_not_dict(self):
        """Test generating report with data not being a dictionary"""
        result = generate_financial_report("not_a_dict", "summary")
        
        assert result["status"] == "error"
        assert "dictionary" in result["message"].lower()
    
    def test_generate_report_empty_report_type(self):
        """Test generating report with empty report type"""
        result = generate_financial_report({"income": 5000.0}, "")
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_generate_report_invalid_report_type(self):
        """Test generating report with invalid report type"""
        result = generate_financial_report({"income": 5000.0}, "invalid_type")
        
        assert result["status"] == "error"
        assert "invalid report type" in result["message"].lower()


class TestIntegrationErrorHandling:
    """Integration tests for error handling across multiple functions"""
    
    def test_end_to_end_error_handling(self):
        """Test error handling in a realistic workflow"""
        # Test 1: Invalid market data fetch
        market_result = fetch_market_data("", "1m", "yahoo")
        assert market_result["status"] == "error"
        
        # Test 2: Invalid budget creation
        budget_result = create_budget(None, {})
        assert budget_result["status"] == "error"
        
        # Test 3: Invalid metrics calculation
        metrics_result = calculate_financial_metrics("not_a_dict", ["roi"])
        assert metrics_result["status"] == "error"
        
        # Test 4: Invalid forecast
        forecast_result = forecast_expenses(None, months_ahead=0)
        assert forecast_result["status"] == "error"
        
        # All should fail gracefully with error status
        assert all(r["status"] == "error" for r in [
            market_result, budget_result, metrics_result, forecast_result
        ])
