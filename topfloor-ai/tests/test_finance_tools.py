"""
Tests for Finance Tools
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path
from app.tools.finance_tools import fetch_market_data, analyze_bank_statement


class TestFetchMarketData:
    """Tests for fetch_market_data function"""
    
    @patch('app.tools.finance_tools.yf.Ticker')
    def test_fetch_market_data_valid_symbol(self, mock_ticker):
        """Test fetching market data for a valid stock symbol"""
        # Create mock historical data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        mock_hist = pd.DataFrame({
            'Close': [150.0 + i for i in range(30)],
            'Volume': [50000000 + i * 1000000 for i in range(30)]
        }, index=dates)
        
        # Mock ticker info
        mock_info = {
            'currency': 'USD',
            'marketCap': 3000000000000,
            'fiftyTwoWeekHigh': 200.0,
            'fiftyTwoWeekLow': 120.0,
            'averageVolume': 55000000,
            'longName': 'Apple Inc.'
        }
        
        # Setup mock
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_hist
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance
        
        result = fetch_market_data("AAPL", "1m", "yahoo")
        
        assert result["status"] == "success"
        assert result["symbol"] == "AAPL"
        assert "current_price" in result
        assert "change" in result
        assert "change_percent" in result
        assert "volume" in result
        assert "historical" in result
        assert "dates" in result["historical"]
        assert "prices" in result["historical"]
        assert "volumes" in result["historical"]
        assert len(result["historical"]["dates"]) == 30
        assert len(result["historical"]["prices"]) == 30
        assert len(result["historical"]["volumes"]) == 30
        assert result["additional_info"]["company_name"] == "Apple Inc."
    
    @patch('app.tools.finance_tools.yf.Ticker')
    def test_fetch_market_data_crypto(self, mock_ticker):
        """Test fetching market data for cryptocurrency"""
        # Create mock historical data
        dates = pd.date_range(end=datetime.now(), periods=5, freq='D')
        mock_hist = pd.DataFrame({
            'Close': [45000.0, 46000.0, 47000.0, 46500.0, 48000.0],
            'Volume': [1000000000, 1100000000, 1050000000, 1200000000, 1150000000]
        }, index=dates)
        
        mock_info = {
            'currency': 'USD',
            'shortName': 'Bitcoin USD'
        }
        
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_hist
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance
        
        result = fetch_market_data("BTC-USD", "1w", "yahoo")
        
        assert result["status"] == "success"
        assert result["symbol"] == "BTC-USD"
        assert "current_price" in result
        assert result["current_price"] == 48000.0
        assert result["change"] == 1500.0  # 48000 - 46500
    
    @patch('app.tools.finance_tools.yf.Ticker')
    def test_fetch_market_data_different_timeframes(self, mock_ticker):
        """Test fetching market data with different timeframes"""
        dates = pd.date_range(end=datetime.now(), periods=10, freq='D')
        mock_hist = pd.DataFrame({
            'Close': [150.0 + i for i in range(10)],
            'Volume': [50000000 + i * 1000000 for i in range(10)]
        }, index=dates)
        
        mock_info = {'currency': 'USD', 'longName': 'Microsoft Corporation'}
        
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_hist
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance
        
        timeframes = ["1d", "1w", "1m", "3m", "1y"]
        
        for timeframe in timeframes:
            result = fetch_market_data("MSFT", timeframe, "yahoo")
            assert result["status"] == "success"
            assert result["timeframe"] == timeframe
    
    @patch('app.tools.finance_tools.yf.Ticker')
    def test_fetch_market_data_invalid_symbol(self, mock_ticker):
        """Test fetching market data for an invalid symbol"""
        # Mock empty dataframe for invalid symbol
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance
        
        result = fetch_market_data("INVALID_SYMBOL_XYZ123", "1m", "yahoo")
        
        assert result["status"] == "error"
        assert "message" in result
        assert result["symbol"] == "INVALID_SYMBOL_XYZ123"
    
    @patch('app.tools.finance_tools.yf.Ticker')
    def test_fetch_market_data_additional_info(self, mock_ticker):
        """Test that additional info is included in the response"""
        dates = pd.date_range(end=datetime.now(), periods=10, freq='D')
        mock_hist = pd.DataFrame({
            'Close': [2800.0 + i * 10 for i in range(10)],
            'Volume': [1000000 + i * 10000 for i in range(10)]
        }, index=dates)
        
        mock_info = {
            'currency': 'USD',
            'marketCap': 2000000000000,
            'fiftyTwoWeekHigh': 3000.0,
            'fiftyTwoWeekLow': 2500.0,
            'averageVolume': 1200000,
            'longName': 'Alphabet Inc.'
        }
        
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_hist
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance
        
        result = fetch_market_data("GOOGL", "1m", "yahoo")
        
        assert result["status"] == "success"
        assert "additional_info" in result
        assert "currency" in result["additional_info"]
        assert result["additional_info"]["currency"] == "USD"
        assert "company_name" in result["additional_info"]
        assert result["additional_info"]["company_name"] == "Alphabet Inc."
        assert "market_cap" in result["additional_info"]
        assert result["additional_info"]["market_cap"] == 2000000000000
    
    @patch('app.tools.finance_tools.yf.Ticker')
    def test_fetch_market_data_exception_handling(self, mock_ticker):
        """Test that exceptions are handled gracefully"""
        mock_ticker.side_effect = Exception("Network error")
        
        result = fetch_market_data("AAPL", "1m", "yahoo")
        
        assert result["status"] == "error"
        assert "message" in result
        assert "Network error" in result["message"]



class TestAnalyzeBankStatement:
    """Tests for analyze_bank_statement function"""
    
    def test_analyze_bank_statement_csv_basic(self):
        """Test analyzing a basic CSV bank statement"""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Description,Amount\n")
            f.write("2026-01-01,Salary Deposit,5000.00\n")
            f.write("2026-01-05,Rent Payment,-1200.00\n")
            f.write("2026-01-10,Grocery Store,-150.00\n")
            f.write("2026-01-15,Gas Station,-50.00\n")
            f.write("2026-01-20,Netflix Subscription,-15.00\n")
            f.write("2026-01-25,Amazon Shopping,-200.00\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            assert result["status"] == "success"
            assert result["total_income"] == 5000.00
            assert result["total_expenses"] == 1615.00
            assert result["net_savings"] == 3385.00
            assert result["savings_rate"] > 0
            assert result["transaction_count"] == 6
            assert "expenses_by_category" in result
            assert "housing" in result["expenses_by_category"]
            assert result["expenses_by_category"]["housing"] == 1200.00
        finally:
            os.unlink(temp_path)
    
    def test_analyze_bank_statement_categorization(self):
        """Test transaction categorization accuracy"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Description,Amount\n")
            f.write("2026-01-01,Payroll Deposit,3000.00\n")
            f.write("2026-01-02,Mortgage Payment,-1000.00\n")
            f.write("2026-01-03,Electric Bill,-100.00\n")
            f.write("2026-01-04,Walmart Grocery,-200.00\n")
            f.write("2026-01-05,Uber Ride,-25.00\n")
            f.write("2026-01-06,Spotify Premium,-10.00\n")
            f.write("2026-01-07,CVS Pharmacy,-30.00\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            assert result["status"] == "success"
            categories = result["expenses_by_category"]
            
            # Check specific categories
            assert "housing" in categories
            assert categories["housing"] == 1000.00
            assert "utilities" in categories
            assert categories["utilities"] == 100.00
            assert "food" in categories
            assert categories["food"] == 200.00
            assert "transportation" in categories
            assert categories["transportation"] == 25.00
            assert "entertainment" in categories or "subscriptions" in categories
            assert "healthcare" in categories
            assert categories["healthcare"] == 30.00
        finally:
            os.unlink(temp_path)
    
    def test_analyze_bank_statement_excel(self):
        """Test analyzing an Excel bank statement"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            # Create Excel file
            df = pd.DataFrame({
                'Date': ['2026-01-01', '2026-01-05', '2026-01-10'],
                'Description': ['Salary', 'Rent', 'Groceries'],
                'Amount': [4000.00, -1500.00, -300.00]
            })
            df.to_excel(temp_path, index=False)
            
            result = analyze_bank_statement(temp_path, "excel")
            
            assert result["status"] == "success"
            assert result["total_income"] == 4000.00
            assert result["total_expenses"] == 1800.00
            assert result["transaction_count"] == 3
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_analyze_bank_statement_file_not_found(self):
        """Test handling of non-existent file"""
        result = analyze_bank_statement("/nonexistent/file.csv", "csv")
        
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()
    
    def test_analyze_bank_statement_empty_file(self):
        """Test handling of empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Description,Amount\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            assert result["status"] == "error"
            assert "empty" in result["message"].lower() or "no" in result["message"].lower()
        finally:
            os.unlink(temp_path)
    
    def test_analyze_bank_statement_missing_columns(self):
        """Test handling of file with missing required columns"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,SomeOtherColumn\n")
            f.write("2026-01-01,Value\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            assert result["status"] == "error"
            assert "column" in result["message"].lower()
        finally:
            os.unlink(temp_path)
    
    def test_analyze_bank_statement_top_expenses(self):
        """Test that top expenses are included in results"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Description,Amount\n")
            f.write("2026-01-01,Salary,5000.00\n")
            f.write("2026-01-02,Rent,-1200.00\n")
            f.write("2026-01-03,Car Payment,-500.00\n")
            f.write("2026-01-04,Groceries,-300.00\n")
            f.write("2026-01-05,Insurance,-250.00\n")
            f.write("2026-01-06,Utilities,-150.00\n")
            f.write("2026-01-07,Gas,-50.00\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            assert result["status"] == "success"
            assert "top_expenses" in result
            assert len(result["top_expenses"]) <= 5
            
            # Top expense should be rent
            if result["top_expenses"]:
                assert result["top_expenses"][0]["amount"] == 1200.00
        finally:
            os.unlink(temp_path)
    
    def test_analyze_bank_statement_top_income(self):
        """Test that top income sources are included in results"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Description,Amount\n")
            f.write("2026-01-01,Salary,5000.00\n")
            f.write("2026-01-15,Bonus,1000.00\n")
            f.write("2026-01-20,Freelance Payment,500.00\n")
            f.write("2026-01-05,Rent,-1200.00\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            assert result["status"] == "success"
            assert "top_income" in result
            assert len(result["top_income"]) > 0
            
            # Top income should be salary
            if result["top_income"]:
                assert result["top_income"][0]["amount"] == 5000.00
        finally:
            os.unlink(temp_path)
    
    def test_analyze_bank_statement_date_range(self):
        """Test that date range is correctly identified"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Description,Amount\n")
            f.write("2026-01-01,Income,1000.00\n")
            f.write("2026-01-15,Expense,-100.00\n")
            f.write("2026-01-31,Expense,-50.00\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            assert result["status"] == "success"
            assert "date_range" in result
            assert "2026-01-01" in result["date_range"]
            assert "2026-01-31" in result["date_range"]
        finally:
            os.unlink(temp_path)
    
    def test_analyze_bank_statement_unsupported_format(self):
        """Test handling of unsupported file format"""
        result = analyze_bank_statement("/path/to/file.txt", "txt")
        
        assert result["status"] == "error"
        assert "unsupported" in result["message"].lower()
    
    def test_analyze_bank_statement_pdf_not_implemented(self):
        """Test that PDF format returns appropriate message"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "pdf")
            
            assert result["status"] == "error"
            assert "pdf" in result["message"].lower()
        finally:
            os.unlink(temp_path)
    
    def test_analyze_bank_statement_various_column_names(self):
        """Test that various column naming conventions are handled"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Transaction Date,Details,Transaction Amount\n")
            f.write("2026-01-01,Salary Deposit,3000.00\n")
            f.write("2026-01-05,Rent Payment,-1000.00\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            assert result["status"] == "success"
            assert result["total_income"] == 3000.00
            assert result["total_expenses"] == 1000.00
        finally:
            os.unlink(temp_path)
    
    def test_analyze_bank_statement_savings_rate_calculation(self):
        """Test savings rate calculation accuracy"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Description,Amount\n")
            f.write("2026-01-01,Income,1000.00\n")
            f.write("2026-01-05,Expense,-700.00\n")
            temp_path = f.name
        
        try:
            result = analyze_bank_statement(temp_path, "csv")
            
            assert result["status"] == "success"
            # Savings rate should be 30% (300/1000)
            assert result["savings_rate"] == 30.0
        finally:
            os.unlink(temp_path)


class TestCreateBudget:
    """Tests for create_budget function"""
    
    def test_create_budget_basic(self):
        """Test basic budget creation with income and expenses"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=5000.0,
            expenses={
                "housing": 1200.0,
                "food": 600.0,
                "transportation": 300.0,
                "utilities": 200.0
            },
            goals={"emergency_fund": 500.0}
        )
        
        assert result["status"] == "success"
        assert result["income"] == 5000.0
        assert result["total_expenses"] == 2300.0
        assert result["total_goals"] == 500.0
        assert result["available"] == 2200.0
        assert "expense_percentages" in result
        assert "recommendations" in result
        assert "budget_health" in result
    
    def test_create_budget_expense_percentages(self):
        """Test that expense percentages are calculated correctly"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=5000.0,
            expenses={
                "housing": 1500.0,  # 30%
                "food": 750.0,      # 15%
                "transportation": 500.0  # 10%
            }
        )
        
        assert result["status"] == "success"
        assert result["expense_percentages"]["housing"] == 30.0
        assert result["expense_percentages"]["food"] == 15.0
        assert result["expense_percentages"]["transportation"] == 10.0
    
    def test_create_budget_high_housing_warning(self):
        """Test that warning is given when housing exceeds 30%"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=5000.0,
            expenses={"housing": 1600.0}  # 32%
        )
        
        assert result["status"] == "success"
        assert any("housing" in rec.lower() and "30%" in rec for rec in result["recommendations"])
    
    def test_create_budget_expenses_exceed_income(self):
        """Test budget when expenses exceed income"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=3000.0,
            expenses={
                "housing": 1500.0,
                "food": 800.0,
                "transportation": 500.0,
                "utilities": 300.0
            }
        )
        
        assert result["status"] == "success"
        assert result["available"] < 0
        assert result["budget_health"] == "critical"
        assert any("exceed income" in rec.lower() for rec in result["recommendations"])
    
    def test_create_budget_excellent_savings(self):
        """Test budget with excellent savings rate (20%+)"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=5000.0,
            expenses={"housing": 1200.0, "food": 500.0}  # Total: 1700, leaving 3300 (66%)
        )
        
        assert result["status"] == "success"
        assert result["available"] == 3300.0
        assert result["budget_health"] == "excellent"
        assert any("great job" in rec.lower() or "20%" in rec for rec in result["recommendations"])
    
    def test_create_budget_no_goals(self):
        """Test budget creation without goals"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=4000.0,
            expenses={"housing": 1000.0, "food": 500.0}
        )
        
        assert result["status"] == "success"
        assert result["total_goals"] == 0
        assert result["available"] == 2500.0
    
    def test_create_budget_empty_goals(self):
        """Test budget creation with empty goals dictionary"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=4000.0,
            expenses={"housing": 1000.0},
            goals={}
        )
        
        assert result["status"] == "success"
        assert result["total_goals"] == 0
    
    def test_create_budget_zero_income(self):
        """Test budget with zero income"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=0.0,
            expenses={"housing": 1000.0}
        )
        
        assert result["status"] == "success"
        assert any("invalid income" in rec.lower() for rec in result["recommendations"])
    
    def test_create_budget_negative_income(self):
        """Test budget with negative income"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=-1000.0,
            expenses={"housing": 500.0}
        )
        
        assert result["status"] == "success"
        assert any("invalid income" in rec.lower() for rec in result["recommendations"])
    
    def test_create_budget_high_food_expenses(self):
        """Test warning for high food expenses (>15%)"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=5000.0,
            expenses={"food": 850.0}  # 17%
        )
        
        assert result["status"] == "success"
        assert any("food" in rec.lower() for rec in result["recommendations"])
    
    def test_create_budget_high_transportation(self):
        """Test warning for high transportation costs (>15%)"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=5000.0,
            expenses={"transportation": 850.0}  # 17%
        )
        
        assert result["status"] == "success"
        assert any("transportation" in rec.lower() for rec in result["recommendations"])
    
    def test_create_budget_good_health(self):
        """Test budget with good health (10-20% savings)"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=5000.0,
            expenses={"housing": 1200.0, "food": 600.0, "other": 2500.0}  # Total: 4300, leaving 700 (14%)
        )
        
        assert result["status"] == "success"
        assert result["budget_health"] == "good"
    
    def test_create_budget_needs_improvement(self):
        """Test budget that needs improvement (<10% savings)"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=5000.0,
            expenses={"housing": 1200.0, "food": 600.0, "other": 2800.0}  # Total: 4600, leaving 400 (8%)
        )
        
        assert result["status"] == "success"
        assert result["budget_health"] == "needs_improvement"
        assert any("10%" in rec for rec in result["recommendations"])
    
    def test_create_budget_with_multiple_goals(self):
        """Test budget with multiple savings goals"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=6000.0,
            expenses={"housing": 1500.0, "food": 700.0},
            goals={
                "emergency_fund": 500.0,
                "vacation": 300.0,
                "retirement": 600.0
            }
        )
        
        assert result["status"] == "success"
        assert result["total_goals"] == 1400.0
        assert result["available"] == 2400.0
    
    def test_create_budget_rounding(self):
        """Test that available amount is properly rounded"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=5000.33,
            expenses={"housing": 1200.11, "food": 600.22}
        )
        
        assert result["status"] == "success"
        assert isinstance(result["available"], float)
        # Check that it's rounded to 2 decimal places
        assert result["available"] == round(5000.33 - 1200.11 - 600.22, 2)
    
    def test_create_budget_timestamp(self):
        """Test that timestamp is included in response"""
        from app.tools.finance_tools import create_budget
        
        result = create_budget(
            income=5000.0,
            expenses={"housing": 1200.0}
        )
        
        assert result["status"] == "success"
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)


class TestCalculateFinancialMetrics:
    """Tests for calculate_financial_metrics function"""
    
    def test_calculate_roi_positive(self):
        """Test ROI calculation with positive returns"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "initial_investment": 10000.0,
                "current_value": 12000.0
            },
            metrics=["roi"]
        )
        
        assert result["status"] == "success"
        assert "metrics" in result
        assert "roi" in result["metrics"]
        assert result["metrics"]["roi"]["value"] == 20.0
        assert result["metrics"]["roi"]["unit"] == "percent"
        assert result["metrics"]["roi"]["interpretation"] == "positive"
    
    def test_calculate_roi_negative(self):
        """Test ROI calculation with negative returns"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "initial_investment": 10000.0,
                "current_value": 8000.0
            },
            metrics=["roi"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["roi"]["value"] == -20.0
        assert result["metrics"]["roi"]["interpretation"] == "negative"
    
    def test_calculate_roi_zero_initial_investment(self):
        """Test ROI calculation with zero initial investment"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "initial_investment": 0.0,
                "current_value": 5000.0
            },
            metrics=["roi"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["roi"]["value"] is None
        assert "error" in result["metrics"]["roi"]
    
    def test_calculate_savings_rate_excellent(self):
        """Test savings rate calculation with excellent rate (>=20%)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "income": 5000.0,
                "savings": 1200.0
            },
            metrics=["savings_rate"]
        )
        
        assert result["status"] == "success"
        assert "savings_rate" in result["metrics"]
        assert result["metrics"]["savings_rate"]["value"] == 24.0
        assert result["metrics"]["savings_rate"]["unit"] == "percent"
        assert result["metrics"]["savings_rate"]["interpretation"] == "excellent"
    
    def test_calculate_savings_rate_good(self):
        """Test savings rate calculation with good rate (10-20%)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "income": 5000.0,
                "savings": 750.0
            },
            metrics=["savings_rate"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["savings_rate"]["value"] == 15.0
        assert result["metrics"]["savings_rate"]["interpretation"] == "good"
    
    def test_calculate_savings_rate_needs_improvement(self):
        """Test savings rate calculation with low rate (<10%)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "income": 5000.0,
                "savings": 250.0
            },
            metrics=["savings_rate"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["savings_rate"]["value"] == 5.0
        assert result["metrics"]["savings_rate"]["interpretation"] == "needs_improvement"
    
    def test_calculate_savings_rate_zero_income(self):
        """Test savings rate calculation with zero income"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "income": 0.0,
                "savings": 500.0
            },
            metrics=["savings_rate"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["savings_rate"]["value"] is None
        assert "error" in result["metrics"]["savings_rate"]
    
    def test_calculate_debt_to_income_good(self):
        """Test debt-to-income ratio with good ratio (<36%)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "monthly_income": 5000.0,
                "monthly_debt_payments": 1500.0
            },
            metrics=["debt_to_income"]
        )
        
        assert result["status"] == "success"
        assert "debt_to_income" in result["metrics"]
        assert result["metrics"]["debt_to_income"]["value"] == 30.0
        assert result["metrics"]["debt_to_income"]["unit"] == "percent"
        assert result["metrics"]["debt_to_income"]["interpretation"] == "good"
    
    def test_calculate_debt_to_income_concerning(self):
        """Test debt-to-income ratio with concerning ratio (36-50%)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "monthly_income": 5000.0,
                "monthly_debt_payments": 2000.0
            },
            metrics=["debt_to_income"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["debt_to_income"]["value"] == 40.0
        assert result["metrics"]["debt_to_income"]["interpretation"] == "concerning"
    
    def test_calculate_debt_to_income_high_risk(self):
        """Test debt-to-income ratio with high risk ratio (>=50%)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "monthly_income": 5000.0,
                "monthly_debt_payments": 2750.0
            },
            metrics=["debt_to_income"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["debt_to_income"]["value"] == 55.0
        assert result["metrics"]["debt_to_income"]["interpretation"] == "high_risk"
    
    def test_calculate_debt_to_income_zero_income(self):
        """Test debt-to-income ratio with zero income"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "monthly_income": 0.0,
                "monthly_debt_payments": 1000.0
            },
            metrics=["debt_to_income"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["debt_to_income"]["value"] is None
        assert "error" in result["metrics"]["debt_to_income"]
    
    def test_calculate_emergency_fund_excellent(self):
        """Test emergency fund calculation with excellent coverage (>=6 months)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "monthly_expenses": 3000.0,
                "emergency_fund": 20000.0
            },
            metrics=["emergency_fund_months"]
        )
        
        assert result["status"] == "success"
        assert "emergency_fund_months" in result["metrics"]
        assert result["metrics"]["emergency_fund_months"]["value"] == 6.7
        assert result["metrics"]["emergency_fund_months"]["unit"] == "months"
        assert result["metrics"]["emergency_fund_months"]["interpretation"] == "excellent"
    
    def test_calculate_emergency_fund_good(self):
        """Test emergency fund calculation with good coverage (3-6 months)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "monthly_expenses": 3000.0,
                "emergency_fund": 12000.0
            },
            metrics=["emergency_fund_months"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["emergency_fund_months"]["value"] == 4.0
        assert result["metrics"]["emergency_fund_months"]["interpretation"] == "good"
    
    def test_calculate_emergency_fund_needs_improvement(self):
        """Test emergency fund calculation with low coverage (<3 months)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "monthly_expenses": 3000.0,
                "emergency_fund": 5000.0
            },
            metrics=["emergency_fund_months"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["emergency_fund_months"]["value"] == 1.7
        assert result["metrics"]["emergency_fund_months"]["interpretation"] == "needs_improvement"
    
    def test_calculate_emergency_fund_zero_expenses(self):
        """Test emergency fund calculation with zero expenses"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "monthly_expenses": 0.0,
                "emergency_fund": 10000.0
            },
            metrics=["emergency_fund_months"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["emergency_fund_months"]["value"] is None
        assert "error" in result["metrics"]["emergency_fund_months"]
    
    def test_calculate_net_worth_positive(self):
        """Test net worth calculation with positive net worth"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "total_assets": 500000.0,
                "total_liabilities": 200000.0
            },
            metrics=["net_worth"]
        )
        
        assert result["status"] == "success"
        assert "net_worth" in result["metrics"]
        assert result["metrics"]["net_worth"]["value"] == 300000.0
        assert result["metrics"]["net_worth"]["unit"] == "currency"
        assert result["metrics"]["net_worth"]["interpretation"] == "positive"
    
    def test_calculate_net_worth_negative(self):
        """Test net worth calculation with negative net worth"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "total_assets": 100000.0,
                "total_liabilities": 150000.0
            },
            metrics=["net_worth"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["net_worth"]["value"] == -50000.0
        assert result["metrics"]["net_worth"]["interpretation"] == "negative"
    
    def test_calculate_net_worth_zero(self):
        """Test net worth calculation with zero net worth"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "total_assets": 100000.0,
                "total_liabilities": 100000.0
            },
            metrics=["net_worth"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["net_worth"]["value"] == 0.0
        assert result["metrics"]["net_worth"]["interpretation"] == "neutral"
    
    def test_calculate_multiple_metrics(self):
        """Test calculating multiple metrics at once"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "initial_investment": 10000.0,
                "current_value": 12000.0,
                "income": 5000.0,
                "savings": 1000.0,
                "monthly_income": 5000.0,
                "monthly_debt_payments": 1500.0,
                "monthly_expenses": 3000.0,
                "emergency_fund": 15000.0,
                "total_assets": 200000.0,
                "total_liabilities": 100000.0
            },
            metrics=["roi", "savings_rate", "debt_to_income", "emergency_fund_months", "net_worth"]
        )
        
        assert result["status"] == "success"
        assert "metrics" in result
        assert len(result["metrics"]) == 5
        assert "roi" in result["metrics"]
        assert "savings_rate" in result["metrics"]
        assert "debt_to_income" in result["metrics"]
        assert "emergency_fund_months" in result["metrics"]
        assert "net_worth" in result["metrics"]
    
    def test_calculate_empty_metrics_list(self):
        """Test with empty metrics list"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={"income": 5000.0},
            metrics=[]
        )
        
        assert result["status"] == "success"
        assert "metrics" in result
        assert len(result["metrics"]) == 0
    
    def test_calculate_unknown_metric(self):
        """Test with unknown metric (should be ignored)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={"income": 5000.0, "savings": 1000.0},
            metrics=["savings_rate", "unknown_metric"]
        )
        
        assert result["status"] == "success"
        assert "savings_rate" in result["metrics"]
        assert "unknown_metric" not in result["metrics"]
    
    def test_calculate_metrics_missing_data(self):
        """Test metrics calculation with missing required data"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={},
            metrics=["roi"]
        )
        
        assert result["status"] == "success"
        assert "roi" in result["metrics"]
        assert result["metrics"]["roi"]["value"] is None
        assert "error" in result["metrics"]["roi"]
    
    def test_calculate_metrics_timestamp(self):
        """Test that timestamp is included in response"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={"income": 5000.0, "savings": 1000.0},
            metrics=["savings_rate"]
        )
        
        assert result["status"] == "success"
        assert "calculated_at" in result
        assert isinstance(result["calculated_at"], str)
    
    def test_calculate_roi_neutral(self):
        """Test ROI calculation with no change (neutral)"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "initial_investment": 10000.0,
                "current_value": 10000.0
            },
            metrics=["roi"]
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["roi"]["value"] == 0.0
        assert result["metrics"]["roi"]["interpretation"] == "neutral"
    
    def test_calculate_metrics_rounding(self):
        """Test that metric values are properly rounded"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        result = calculate_financial_metrics(
            data={
                "initial_investment": 10000.0,
                "current_value": 10333.33
            },
            metrics=["roi"]
        )
        
        assert result["status"] == "success"
        # ROI should be 3.33% (rounded to 2 decimal places)
        assert result["metrics"]["roi"]["value"] == 3.33
    
    def test_calculate_savings_rate_exact_boundary(self):
        """Test savings rate at exact boundary values"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        # Test at 20% boundary (excellent)
        result = calculate_financial_metrics(
            data={"income": 5000.0, "savings": 1000.0},
            metrics=["savings_rate"]
        )
        assert result["metrics"]["savings_rate"]["value"] == 20.0
        assert result["metrics"]["savings_rate"]["interpretation"] == "excellent"
        
        # Test at 10% boundary (good)
        result = calculate_financial_metrics(
            data={"income": 5000.0, "savings": 500.0},
            metrics=["savings_rate"]
        )
        assert result["metrics"]["savings_rate"]["value"] == 10.0
        assert result["metrics"]["savings_rate"]["interpretation"] == "good"
    
    def test_calculate_debt_to_income_exact_boundary(self):
        """Test debt-to-income at exact boundary values"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        # Test at 36% boundary
        result = calculate_financial_metrics(
            data={"monthly_income": 5000.0, "monthly_debt_payments": 1800.0},
            metrics=["debt_to_income"]
        )
        assert result["metrics"]["debt_to_income"]["value"] == 36.0
        assert result["metrics"]["debt_to_income"]["interpretation"] == "concerning"
        
        # Test at 50% boundary
        result = calculate_financial_metrics(
            data={"monthly_income": 5000.0, "monthly_debt_payments": 2500.0},
            metrics=["debt_to_income"]
        )
        assert result["metrics"]["debt_to_income"]["value"] == 50.0
        assert result["metrics"]["debt_to_income"]["interpretation"] == "high_risk"
    
    def test_calculate_emergency_fund_exact_boundary(self):
        """Test emergency fund at exact boundary values"""
        from app.tools.finance_tools import calculate_financial_metrics
        
        # Test at 6 months boundary
        result = calculate_financial_metrics(
            data={"monthly_expenses": 3000.0, "emergency_fund": 18000.0},
            metrics=["emergency_fund_months"]
        )
        assert result["metrics"]["emergency_fund_months"]["value"] == 6.0
        assert result["metrics"]["emergency_fund_months"]["interpretation"] == "excellent"
        
        # Test at 3 months boundary
        result = calculate_financial_metrics(
            data={"monthly_expenses": 3000.0, "emergency_fund": 9000.0},
            metrics=["emergency_fund_months"]
        )
        assert result["metrics"]["emergency_fund_months"]["value"] == 3.0
        assert result["metrics"]["emergency_fund_months"]["interpretation"] == "good"



class TestForecastExpenses:
    """Tests for forecast_expenses function"""
    
    def test_forecast_expenses_basic(self):
        """Test basic expense forecasting with historical data"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3000.0},
            {"month": "2026-02", "total": 3200.0},
            {"month": "2026-03", "total": 3100.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=3)
        
        assert result["status"] == "success"
        assert "forecast" in result
        assert len(result["forecast"]) == 3
        assert "trend" in result
        assert "average_historical" in result
        assert result["data_points_used"] == 3
    
    def test_forecast_expenses_structure(self):
        """Test that forecast structure contains required fields"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3000.0},
            {"month": "2026-02", "total": 3000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=2)
        
        assert result["status"] == "success"
        for forecast_item in result["forecast"]:
            assert "month" in forecast_item
            assert "forecasted_amount" in forecast_item
            assert "confidence_low" in forecast_item
            assert "confidence_high" in forecast_item
    
    def test_forecast_expenses_increasing_trend(self):
        """Test forecasting with increasing expense trend"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2025-09", "total": 2500.0},
            {"month": "2025-10", "total": 2600.0},
            {"month": "2025-11", "total": 2700.0},
            {"month": "2025-12", "total": 2800.0},
            {"month": "2026-01", "total": 2900.0},
            {"month": "2026-02", "total": 3000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=3)
        
        assert result["status"] == "success"
        assert result["trend"] == "increasing"
        # Forecasted amounts should generally increase
        assert result["forecast"][0]["forecasted_amount"] > 0
    
    def test_forecast_expenses_decreasing_trend(self):
        """Test forecasting with decreasing expense trend"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2025-09", "total": 3500.0},
            {"month": "2025-10", "total": 3400.0},
            {"month": "2025-11", "total": 3300.0},
            {"month": "2025-12", "total": 3200.0},
            {"month": "2026-01", "total": 3100.0},
            {"month": "2026-02", "total": 3000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=3)
        
        assert result["status"] == "success"
        assert result["trend"] == "decreasing"
    
    def test_forecast_expenses_stable_trend(self):
        """Test forecasting with stable expense trend"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2025-11", "total": 3000.0},
            {"month": "2025-12", "total": 3050.0},
            {"month": "2026-01", "total": 2980.0},
            {"month": "2026-02", "total": 3020.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=3)
        
        assert result["status"] == "success"
        assert result["trend"] == "stable"
    
    def test_forecast_expenses_confidence_intervals(self):
        """Test that confidence intervals are calculated correctly"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3000.0},
            {"month": "2026-02", "total": 3000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=2)
        
        assert result["status"] == "success"
        for forecast_item in result["forecast"]:
            forecasted = forecast_item["forecasted_amount"]
            low = forecast_item["confidence_low"]
            high = forecast_item["confidence_high"]
            
            # Confidence low should be ~90% of forecasted
            assert abs(low - forecasted * 0.9) < 0.01
            # Confidence high should be ~110% of forecasted
            assert abs(high - forecasted * 1.1) < 0.01
            # Low should be less than forecasted, which should be less than high
            assert low < forecasted < high
    
    def test_forecast_expenses_single_month(self):
        """Test forecasting for a single month ahead"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3000.0},
            {"month": "2026-02", "total": 3100.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=1)
        
        assert result["status"] == "success"
        assert len(result["forecast"]) == 1
        assert result["forecast"][0]["month"] == 1
    
    def test_forecast_expenses_twelve_months(self):
        """Test forecasting for maximum 12 months ahead"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2025-01", "total": 3000.0},
            {"month": "2025-02", "total": 3100.0},
            {"month": "2025-03", "total": 3050.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=12)
        
        assert result["status"] == "success"
        assert len(result["forecast"]) == 12
        assert result["forecast"][0]["month"] == 1
        assert result["forecast"][11]["month"] == 12
    
    def test_forecast_expenses_empty_historical_data(self):
        """Test forecasting with empty historical data"""
        from app.tools.finance_tools import forecast_expenses
        
        result = forecast_expenses([], months_ahead=3)
        
        assert result["status"] == "success"
        assert "forecast" in result
        assert len(result["forecast"]) == 3
        assert result["data_points_used"] == 0
        assert result["trend"] == "unknown"
        # Should use default average
        assert result["average_historical"] == 3000.0
    
    def test_forecast_expenses_none_historical_data(self):
        """Test forecasting with None as historical data"""
        from app.tools.finance_tools import forecast_expenses
        
        result = forecast_expenses(None, months_ahead=3)
        
        assert result["status"] == "success"
        assert "forecast" in result
        assert len(result["forecast"]) == 3
        assert result["data_points_used"] == 0
    
    def test_forecast_expenses_single_data_point(self):
        """Test forecasting with only one historical data point"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3500.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=3)
        
        assert result["status"] == "success"
        assert result["data_points_used"] == 1
        assert result["average_historical"] == 3500.0
        assert result["trend"] == "stable"
    
    def test_forecast_expenses_invalid_months_ahead_zero(self):
        """Test forecasting with zero months ahead"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=0)
        
        assert result["status"] == "error"
        assert "must be at least 1" in result["message"]
    
    def test_forecast_expenses_invalid_months_ahead_negative(self):
        """Test forecasting with negative months ahead"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=-1)
        
        assert result["status"] == "error"
        assert "must be at least 1" in result["message"]
    
    def test_forecast_expenses_invalid_months_ahead_too_large(self):
        """Test forecasting with more than 12 months ahead"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=13)
        
        assert result["status"] == "error"
        assert "cannot exceed 12" in result["message"]
    
    def test_forecast_expenses_default_months_ahead(self):
        """Test forecasting with default months_ahead parameter (3)"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3000.0},
            {"month": "2026-02", "total": 3100.0}
        ]
        
        result = forecast_expenses(historical_data)
        
        assert result["status"] == "success"
        assert len(result["forecast"]) == 3
    
    def test_forecast_expenses_average_calculation(self):
        """Test that average is calculated correctly from historical data"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 2000.0},
            {"month": "2026-02", "total": 3000.0},
            {"month": "2026-03", "total": 4000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=1)
        
        assert result["status"] == "success"
        # Average should be (2000 + 3000 + 4000) / 3 = 3000
        assert result["average_historical"] == 3000.0
    
    def test_forecast_expenses_rounding(self):
        """Test that forecasted amounts are properly rounded"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3333.33},
            {"month": "2026-02", "total": 3333.33}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=2)
        
        assert result["status"] == "success"
        for forecast_item in result["forecast"]:
            # Check that values are rounded to 2 decimal places
            assert forecast_item["forecasted_amount"] == round(forecast_item["forecasted_amount"], 2)
            assert forecast_item["confidence_low"] == round(forecast_item["confidence_low"], 2)
            assert forecast_item["confidence_high"] == round(forecast_item["confidence_high"], 2)
    
    def test_forecast_expenses_timestamp(self):
        """Test that timestamp is included in response"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=1)
        
        assert result["status"] == "success"
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)
    
    def test_forecast_expenses_message(self):
        """Test that success message is included"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01", "total": 3000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=5)
        
        assert result["status"] == "success"
        assert "message" in result
        assert "5 months" in result["message"]
    
    def test_forecast_expenses_missing_total_field(self):
        """Test handling of historical data with missing 'total' field"""
        from app.tools.finance_tools import forecast_expenses
        
        historical_data = [
            {"month": "2026-01"},  # Missing 'total'
            {"month": "2026-02", "total": 3000.0}
        ]
        
        result = forecast_expenses(historical_data, months_ahead=2)
        
        # Should handle gracefully, treating missing as 0
        assert result["status"] == "success"
        assert "forecast" in result
    
    def test_forecast_expenses_large_historical_dataset(self):
        """Test forecasting with large historical dataset"""
        from app.tools.finance_tools import forecast_expenses
        
        # Create 24 months of historical data
        historical_data = [
            {"month": f"2024-{i:02d}", "total": 3000.0 + (i * 50)}
            for i in range(1, 13)
        ] + [
            {"month": f"2025-{i:02d}", "total": 3600.0 + (i * 50)}
            for i in range(1, 13)
        ]
        
        result = forecast_expenses(historical_data, months_ahead=6)
        
        assert result["status"] == "success"
        assert result["data_points_used"] == 24
        assert len(result["forecast"]) == 6
        assert result["trend"] == "increasing"
    
    def test_forecast_expenses_exception_handling(self):
        """Test that exceptions are handled gracefully"""
        from app.tools.finance_tools import forecast_expenses
        
        # Pass invalid data type that might cause exception
        result = forecast_expenses("invalid_data", months_ahead=3)
        
        assert result["status"] == "error"
        assert "message" in result


class TestGenerateFinancialReport:
    """Tests for generate_financial_report function"""
    
    def test_generate_financial_report_comprehensive(self):
        """Test generating a comprehensive financial report"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {
            "income": 5000.0,
            "expenses": 3500.0,
            "savings": 1500.0,
            "investments": 50000.0
        }
        
        result = generate_financial_report(data, "comprehensive")
        
        assert result["status"] == "generated"
        assert result["report_type"] == "comprehensive"
        assert "report_id" in result
        assert "title" in result
        assert "generated_at" in result
        assert "sections" in result
        assert len(result["sections"]) > 0
        assert "file_format" in result
        assert result["file_format"] == "pdf"
    
    def test_generate_financial_report_summary(self):
        """Test generating a summary financial report"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {
            "income": 5000.0,
            "expenses": 3500.0
        }
        
        result = generate_financial_report(data, "summary")
        
        assert result["status"] == "generated"
        assert result["report_type"] == "summary"
        assert "sections" in result
        # Summary should have fewer sections than comprehensive
        assert "Executive Summary" in result["sections"]
        assert "Key Metrics" in result["sections"]
    
    def test_generate_financial_report_investment(self):
        """Test generating an investment financial report"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {
            "portfolio_value": 100000.0,
            "returns": 8.5,
            "risk_score": 6
        }
        
        result = generate_financial_report(data, "investment")
        
        assert result["status"] == "generated"
        assert result["report_type"] == "investment"
        assert "sections" in result
        assert "Portfolio Overview" in result["sections"]
        assert "Performance Analysis" in result["sections"]
    
    def test_generate_financial_report_budget(self):
        """Test generating a budget financial report"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {
            "income": 5000.0,
            "expenses": {
                "housing": 1200.0,
                "food": 600.0,
                "transportation": 300.0
            }
        }
        
        result = generate_financial_report(data, "budget")
        
        assert result["status"] == "generated"
        assert result["report_type"] == "budget"
        assert "sections" in result
        assert "Income Summary" in result["sections"]
        assert "Expense Breakdown" in result["sections"]
        assert "Budget vs Actual" in result["sections"]
    
    def test_generate_financial_report_default_type(self):
        """Test generating report with default type (comprehensive)"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"income": 5000.0}
        
        result = generate_financial_report(data)
        
        assert result["status"] == "generated"
        assert result["report_type"] == "comprehensive"
    
    def test_generate_financial_report_report_id_format(self):
        """Test that report ID follows expected format"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"income": 5000.0}
        
        result = generate_financial_report(data, "summary")
        
        assert result["status"] == "generated"
        assert "report_id" in result
        assert result["report_id"].startswith("fin_report_")
        # Should contain timestamp
        assert len(result["report_id"]) > len("fin_report_")
    
    def test_generate_financial_report_title_format(self):
        """Test that report title is properly formatted"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"income": 5000.0}
        
        result = generate_financial_report(data, "investment")
        
        assert result["status"] == "generated"
        assert "title" in result
        assert "Financial Report" in result["title"]
        assert "Investment" in result["title"]
    
    def test_generate_financial_report_data_included(self):
        """Test that data_included field lists all data keys"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {
            "income": 5000.0,
            "expenses": 3500.0,
            "savings": 1500.0
        }
        
        result = generate_financial_report(data, "summary")
        
        assert result["status"] == "generated"
        assert "data_included" in result
        assert "income" in result["data_included"]
        assert "expenses" in result["data_included"]
        assert "savings" in result["data_included"]
    
    def test_generate_financial_report_empty_data(self):
        """Test generating report with empty data dictionary"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {}
        
        result = generate_financial_report(data, "summary")
        
        assert result["status"] == "generated"
        assert "data_included" in result
        assert len(result["data_included"]) == 0
    
    def test_generate_financial_report_timestamp(self):
        """Test that timestamp is included in response"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"income": 5000.0}
        
        result = generate_financial_report(data, "summary")
        
        assert result["status"] == "generated"
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)
        assert "generated_at" in result
        assert isinstance(result["generated_at"], str)
    
    def test_generate_financial_report_message(self):
        """Test that success message is included"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"income": 5000.0}
        
        result = generate_financial_report(data, "budget")
        
        assert result["status"] == "generated"
        assert "message" in result
        assert "generated successfully" in result["message"].lower()
        assert "budget" in result["message"].lower()
    
    def test_generate_financial_report_all_types(self):
        """Test generating all report types"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"income": 5000.0, "expenses": 3500.0}
        report_types = ["comprehensive", "summary", "investment", "budget"]
        
        for report_type in report_types:
            result = generate_financial_report(data, report_type)
            assert result["status"] == "generated"
            assert result["report_type"] == report_type
            assert "sections" in result
            assert len(result["sections"]) > 0
    
    def test_generate_financial_report_sections_comprehensive(self):
        """Test that comprehensive report has all expected sections"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"income": 5000.0}
        
        result = generate_financial_report(data, "comprehensive")
        
        assert result["status"] == "generated"
        expected_sections = [
            "Executive Summary",
            "Income Analysis",
            "Expense Breakdown",
            "Savings & Investments",
            "Debt Analysis",
            "Net Worth Statement",
            "Financial Goals Progress",
            "Recommendations"
        ]
        
        for section in expected_sections:
            assert section in result["sections"]
    
    def test_generate_financial_report_sections_summary(self):
        """Test that summary report has expected sections"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"income": 5000.0}
        
        result = generate_financial_report(data, "summary")
        
        assert result["status"] == "generated"
        expected_sections = [
            "Executive Summary",
            "Key Metrics",
            "Quick Recommendations"
        ]
        
        for section in expected_sections:
            assert section in result["sections"]
    
    def test_generate_financial_report_sections_investment(self):
        """Test that investment report has expected sections"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"portfolio_value": 100000.0}
        
        result = generate_financial_report(data, "investment")
        
        assert result["status"] == "generated"
        expected_sections = [
            "Portfolio Overview",
            "Asset Allocation",
            "Performance Analysis",
            "Risk Assessment",
            "Investment Recommendations"
        ]
        
        for section in expected_sections:
            assert section in result["sections"]
    
    def test_generate_financial_report_sections_budget(self):
        """Test that budget report has expected sections"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"income": 5000.0}
        
        result = generate_financial_report(data, "budget")
        
        assert result["status"] == "generated"
        expected_sections = [
            "Income Summary",
            "Expense Breakdown",
            "Budget vs Actual",
            "Savings Analysis",
            "Budget Recommendations"
        ]
        
        for section in expected_sections:
            assert section in result["sections"]
    
    def test_generate_financial_report_complex_data(self):
        """Test generating report with complex nested data"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {
            "income": 5000.0,
            "expenses": {
                "housing": 1200.0,
                "food": 600.0,
                "transportation": 300.0
            },
            "investments": {
                "stocks": 30000.0,
                "bonds": 20000.0,
                "crypto": 5000.0
            },
            "debts": {
                "mortgage": 200000.0,
                "car_loan": 15000.0
            }
        }
        
        result = generate_financial_report(data, "comprehensive")
        
        assert result["status"] == "generated"
        assert "data_included" in result
        assert "income" in result["data_included"]
        assert "expenses" in result["data_included"]
        assert "investments" in result["data_included"]
        assert "debts" in result["data_included"]
    
    def test_generate_financial_report_unique_report_ids(self):
        """Test that each report gets a unique ID"""
        from app.tools.finance_tools import generate_financial_report
        import time
        
        data = {"income": 5000.0}
        
        result1 = generate_financial_report(data, "summary")
        time.sleep(1.1)  # Delay to ensure different timestamp (resolution is 1 second)
        result2 = generate_financial_report(data, "summary")
        
        assert result1["status"] == "generated"
        assert result2["status"] == "generated"
        # Report IDs should be different due to timestamp
        assert result1["report_id"] != result2["report_id"]
    
    def test_generate_financial_report_file_format(self):
        """Test that file format is always PDF"""
        from app.tools.finance_tools import generate_financial_report
        
        data = {"income": 5000.0}
        
        for report_type in ["comprehensive", "summary", "investment", "budget"]:
            result = generate_financial_report(data, report_type)
            assert result["status"] == "generated"
            assert result["file_format"] == "pdf"
