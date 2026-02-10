"""
Tests for Data Analysis Tools
"""

import pytest

pytest.skip("Data analysis features are disabled (pandas/matplotlib removed).", allow_module_level=True)
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from app.tools.data_analysis_tools import load_dataset, clean_data, analyze_data


class TestLoadDataset:
    """Tests for load_dataset function"""
    
    def test_load_dataset_csv_basic(self):
        """Test loading a basic CSV file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age,salary\n")
            f.write("Alice,30,50000\n")
            f.write("Bob,25,45000\n")
            f.write("Charlie,35,60000\n")
            temp_path = f.name
        
        try:
            result = load_dataset(temp_path, "csv")
            
            assert result["status"] == "success"
            assert result["rows"] == 3
            assert len(result["columns"]) == 3
            assert "name" in result["columns"]
            assert "age" in result["columns"]
            assert "salary" in result["columns"]
            assert "preview" in result
            assert len(result["preview"]) == 3
            assert "dtypes" in result
            assert "summary" in result
            assert "missing_values" in result
            assert "memory_usage_mb" in result
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_json_basic(self):
        """Test loading a basic JSON file"""
        import json
        
        data = [
            {"name": "Alice", "age": 30, "salary": 50000},
            {"name": "Bob", "age": 25, "salary": 45000},
            {"name": "Charlie", "age": 35, "salary": 60000}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            result = load_dataset(temp_path, "json")
            
            assert result["status"] == "success"
            assert result["rows"] == 3
            assert len(result["columns"]) == 3
            assert "name" in result["columns"]
            assert "age" in result["columns"]
            assert "salary" in result["columns"]
            assert "preview" in result
            assert len(result["preview"]) == 3
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_excel_basic(self):
        """Test loading a basic Excel file"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [30, 25, 35],
            'salary': [50000, 45000, 60000]
        })
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            df.to_excel(temp_path, index=False)
            result = load_dataset(temp_path, "excel")
            
            assert result["status"] == "success"
            assert result["rows"] == 3
            assert len(result["columns"]) == 3
            assert "name" in result["columns"]
            assert "age" in result["columns"]
            assert "salary" in result["columns"]
            assert "preview" in result
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_xlsx_format(self):
        """Test loading Excel file with xlsx format specifier"""
        df = pd.DataFrame({
            'product': ['A', 'B', 'C'],
            'price': [10.5, 20.0, 15.75]
        })
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            df.to_excel(temp_path, index=False)
            result = load_dataset(temp_path, "xlsx")
            
            assert result["status"] == "success"
            assert result["rows"] == 3
            assert "product" in result["columns"]
            assert "price" in result["columns"]
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_csv_with_missing_values(self):
        """Test loading CSV with missing values"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age,salary\n")
            f.write("Alice,30,50000\n")
            f.write("Bob,,45000\n")
            f.write("Charlie,35,\n")
            temp_path = f.name
        
        try:
            result = load_dataset(temp_path, "csv")
            
            assert result["status"] == "success"
            assert result["rows"] == 3
            assert "missing_values" in result
            assert len(result["missing_values"]) > 0
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_csv_with_options(self):
        """Test loading CSV with custom options"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name;age;salary\n")
            f.write("Alice;30;50000\n")
            f.write("Bob;25;45000\n")
            temp_path = f.name
        
        try:
            result = load_dataset(temp_path, "csv", options={"sep": ";"})
            
            assert result["status"] == "success"
            assert result["rows"] == 2
            assert "name" in result["columns"]
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_empty_file(self):
        """Test handling of empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age,salary\n")
            temp_path = f.name
        
        try:
            result = load_dataset(temp_path, "csv")
            
            assert result["status"] == "error"
            assert "empty" in result["message"].lower()
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_file_not_found(self):
        """Test handling of non-existent file"""
        result = load_dataset("/nonexistent/file.csv", "csv")
        
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()
    
    def test_load_dataset_unsupported_format(self):
        """Test handling of unsupported file format"""
        result = load_dataset("/path/to/file.txt", "txt")
        
        assert result["status"] == "error"
        assert "unsupported" in result["message"].lower()
    
    def test_load_dataset_invalid_json(self):
        """Test handling of invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json content")
            temp_path = f.name
        
        try:
            result = load_dataset(temp_path, "json")
            
            assert result["status"] == "error"
            assert "failed" in result["message"].lower()
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_empty_source(self):
        """Test handling of empty source parameter"""
        result = load_dataset("", "csv")
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_load_dataset_empty_format(self):
        """Test handling of empty format parameter"""
        result = load_dataset("/path/to/file.csv", "")
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    @patch('pandas.read_csv')
    def test_load_dataset_from_url(self, mock_read_csv):
        """Test loading dataset from URL"""
        # Mock the pandas read_csv to return a DataFrame
        mock_df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'age': [30, 25]
        })
        mock_read_csv.return_value = mock_df
        
        result = load_dataset("https://example.com/data.csv", "csv")
        
        assert result["status"] == "success"
        assert result["rows"] == 2
        assert "name" in result["columns"]
        mock_read_csv.assert_called_once()
    
    def test_load_dataset_summary_statistics(self):
        """Test that summary statistics are included for numeric columns"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age,salary\n")
            f.write("Alice,30,50000\n")
            f.write("Bob,25,45000\n")
            f.write("Charlie,35,60000\n")
            temp_path = f.name
        
        try:
            result = load_dataset(temp_path, "csv")
            
            assert result["status"] == "success"
            assert "summary" in result
            assert len(result["summary"]) > 0
            # Check that numeric columns have summary stats
            assert "age" in result["summary"]
            assert "salary" in result["summary"]
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_preview_limit(self):
        """Test that preview is limited to 10 rows"""
        # Create a CSV with more than 10 rows
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("id,value\n")
            for i in range(20):
                f.write(f"{i},{i*10}\n")
            temp_path = f.name
        
        try:
            result = load_dataset(temp_path, "csv")
            
            assert result["status"] == "success"
            assert result["rows"] == 20
            assert len(result["preview"]) == 10  # Preview should be limited to 10
        finally:
            os.unlink(temp_path)


class TestCleanData:
    """Tests for clean_data function"""
    
    def test_clean_data_remove_duplicates(self):
        """Test removing duplicate rows"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Alice', 'Charlie'],
            'age': [30, 25, 30, 35]
        })
        
        result = clean_data(df, ["remove_duplicates"])
        
        assert result["status"] == "success"
        assert result["rows_removed"] == 1
        assert result["final_rows"] == 3
        assert "Removed 1 duplicate rows" in result["changes"]
    
    def test_clean_data_fill_missing_numeric(self):
        """Test filling missing values in numeric columns with median"""
        df = pd.DataFrame({
            'age': [30, None, 28, 35, 32],
            'salary': [50000, 45000, None, 60000, 55000]
        })
        
        result = clean_data(df, ["fill_missing"])
        
        assert result["status"] == "success"
        assert len(result["changes"]) > 0
        assert any("filled" in change.lower() for change in result["changes"])
    
    def test_clean_data_fill_missing_categorical(self):
        """Test filling missing values in categorical columns with mode"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', None, 'Charlie', 'Alice'],
            'city': ['NYC', None, 'NYC', 'LA', 'NYC']
        })
        
        result = clean_data(df, ["fill_missing"])
        
        assert result["status"] == "success"
        assert len(result["changes"]) > 0
    
    def test_clean_data_remove_outliers(self):
        """Test removing outliers using IQR method"""
        df = pd.DataFrame({
            'age': [25, 30, 35, 40, 45, 100],  # 100 is an outlier
            'salary': [40000, 50000, 60000, 70000, 80000, 200000]  # 200000 is an outlier
        })
        
        result = clean_data(df, ["remove_outliers"])
        
        assert result["status"] == "success"
        assert result["rows_removed"] > 0
        assert any("outlier" in change.lower() for change in result["changes"])
    
    def test_clean_data_normalize_columns(self):
        """Test normalizing column names"""
        df = pd.DataFrame({
            'First Name': ['Alice', 'Bob'],
            'Age (years)': [30, 25],
            'Annual Salary': [50000, 45000]
        })
        
        result = clean_data(df, ["normalize_columns"])
        
        assert result["status"] == "success"
        assert any("normalized" in change.lower() for change in result["changes"])
    
    def test_clean_data_drop_empty_columns(self):
        """Test dropping completely empty columns"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [30, 25, 35],
            'empty_col': [None, None, None]
        })
        
        result = clean_data(df, ["drop_empty_columns"])
        
        assert result["status"] == "success"
        assert result["columns_removed"] == 1
        assert any("empty columns" in change.lower() for change in result["changes"])
    
    def test_clean_data_drop_empty_rows(self):
        """Test dropping completely empty rows"""
        df = pd.DataFrame({
            'name': ['Alice', None, 'Charlie'],
            'age': [30, None, 35],
            'salary': [50000, None, 60000]
        })
        
        result = clean_data(df, ["drop_empty_rows"])
        
        assert result["status"] == "success"
        assert result["rows_removed"] == 1
    
    def test_clean_data_multiple_operations(self):
        """Test performing multiple cleaning operations"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Alice', None],
            'age': [30, None, 30, 35],
            'salary': [50000, 45000, 50000, None]
        })
        
        result = clean_data(df, ["remove_duplicates", "fill_missing"])
        
        assert result["status"] == "success"
        assert len(result["operations_performed"]) == 2
        assert result["rows_removed"] >= 1
    
    def test_clean_data_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        df = pd.DataFrame()
        
        result = clean_data(df, ["remove_duplicates"])
        
        assert result["status"] == "error"
        assert "empty" in result["message"].lower()
    
    def test_clean_data_invalid_operation(self):
        """Test handling of invalid operation"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'age': [30, 25]
        })
        
        result = clean_data(df, ["invalid_operation"])
        
        assert result["status"] == "error"
        assert "invalid operation" in result["message"].lower()
    
    def test_clean_data_dict_input(self):
        """Test clean_data with dictionary input"""
        data = {
            'name': ['Alice', 'Bob', 'Alice'],
            'age': [30, 25, 30]
        }
        
        result = clean_data(data, ["remove_duplicates"])
        
        assert result["status"] == "success"
        assert result["rows_removed"] == 1
    
    def test_clean_data_none_input(self):
        """Test handling of None input"""
        result = clean_data(None, ["remove_duplicates"])
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_clean_data_invalid_operations_type(self):
        """Test handling of invalid operations type"""
        df = pd.DataFrame({'name': ['Alice', 'Bob']})
        
        result = clean_data(df, "remove_duplicates")
        
        assert result["status"] == "error"
        assert "must be a list" in result["message"].lower()
    
    def test_clean_data_no_duplicates(self):
        """Test remove_duplicates when there are no duplicates"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [30, 25, 35]
        })
        
        result = clean_data(df, ["remove_duplicates"])
        
        assert result["status"] == "success"
        assert result["rows_removed"] == 0
    
    def test_clean_data_no_outliers(self):
        """Test remove_outliers when there are no outliers"""
        df = pd.DataFrame({
            'age': [25, 30, 35, 40, 45],
            'salary': [40000, 50000, 60000, 70000, 80000]
        })
        
        result = clean_data(df, ["remove_outliers"])
        
        assert result["status"] == "success"
        # May or may not remove rows depending on IQR calculation


class TestAnalyzeData:
    """Tests for analyze_data function"""
    
    def test_analyze_data_descriptive(self):
        """Test descriptive statistical analysis"""
        df = pd.DataFrame({
            'age': [25, 30, 35, 40, 45],
            'salary': [40000, 50000, 60000, 70000, 80000]
        })
        
        result = analyze_data(df, "descriptive")
        
        assert result["status"] == "success"
        assert "mean" in result
        assert "median" in result
        assert "std" in result
        assert "min" in result
        assert "max" in result
        assert result["mean"]["age"] == 35.0
        assert result["mean"]["salary"] == 60000.0
    
    def test_analyze_data_correlation(self):
        """Test correlation analysis"""
        df = pd.DataFrame({
            'age': [25, 30, 35, 40, 45],
            'salary': [40000, 50000, 60000, 70000, 80000],
            'experience': [2, 5, 8, 12, 15]
        })
        
        result = analyze_data(df, "correlation")
        
        assert result["status"] == "success"
        assert "correlation_matrix" in result
        assert "age" in result["correlation_matrix"]
    
    def test_analyze_data_no_numeric_columns(self):
        """Test analysis with no numeric columns"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'city': ['NYC', 'LA', 'Chicago']
        })
        
        result = analyze_data(df, "descriptive")
        
        assert result["status"] == "error"
        assert "numeric" in result["message"].lower()


class TestCreateVisualization:
    """Tests for create_visualization function"""
    
    def test_create_visualization_line_chart_matplotlib(self):
        """Test creating a line chart with matplotlib"""
        df = pd.DataFrame({
            'date': ['2024-01', '2024-02', '2024-03', '2024-04'],
            'sales': [100, 150, 120, 180]
        })
        
        result = create_visualization(
            df,
            "line",
            {"x": "date", "y": "sales", "title": "Sales Over Time"}
        )
        
        assert result["status"] == "success"
        assert result["chart_type"] == "line"
        assert result["file_type"] == "png"
        assert result["interactive"] is False
        assert os.path.exists(result["file_path"])
        assert result["file_size_bytes"] > 0
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_bar_chart_matplotlib(self):
        """Test creating a bar chart with matplotlib"""
        df = pd.DataFrame({
            'category': ['A', 'B', 'C', 'D'],
            'value': [25, 40, 30, 45]
        })
        
        result = create_visualization(
            df,
            "bar",
            {"x": "category", "y": "value", "title": "Category Values"}
        )
        
        assert result["status"] == "success"
        assert result["chart_type"] == "bar"
        assert result["file_type"] == "png"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_scatter_chart_matplotlib(self):
        """Test creating a scatter chart with matplotlib"""
        df = pd.DataFrame({
            'x_val': [1, 2, 3, 4, 5],
            'y_val': [2, 4, 5, 4, 6]
        })
        
        result = create_visualization(
            df,
            "scatter",
            {"x": "x_val", "y": "y_val", "title": "Scatter Plot"}
        )
        
        assert result["status"] == "success"
        assert result["chart_type"] == "scatter"
        assert result["file_type"] == "png"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_pie_chart_matplotlib(self):
        """Test creating a pie chart with matplotlib"""
        df = pd.DataFrame({
            'category': ['A', 'B', 'C'],
            'value': [30, 45, 25]
        })
        
        result = create_visualization(
            df,
            "pie",
            {"x": "category", "y": "value", "title": "Distribution"}
        )
        
        assert result["status"] == "success"
        assert result["chart_type"] == "pie"
        assert result["file_type"] == "png"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_heatmap_matplotlib(self):
        """Test creating a heatmap with matplotlib"""
        df = pd.DataFrame({
            'var1': [1, 2, 3, 4, 5],
            'var2': [2, 4, 6, 8, 10],
            'var3': [5, 4, 3, 2, 1]
        })
        
        result = create_visualization(
            df,
            "heatmap",
            {"title": "Correlation Heatmap"}
        )
        
        assert result["status"] == "success"
        assert result["chart_type"] == "heatmap"
        assert result["file_type"] == "png"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_histogram_matplotlib(self):
        """Test creating a histogram with matplotlib"""
        df = pd.DataFrame({
            'values': [1, 2, 2, 3, 3, 3, 4, 4, 5]
        })
        
        result = create_visualization(
            df,
            "histogram",
            {"x": "values", "title": "Value Distribution"}
        )
        
        assert result["status"] == "success"
        assert result["chart_type"] == "histogram"
        assert result["file_type"] == "png"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_box_plot_matplotlib(self):
        """Test creating a box plot with matplotlib"""
        df = pd.DataFrame({
            'values': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        })
        
        result = create_visualization(
            df,
            "box",
            {"y": "values", "title": "Box Plot"}
        )
        
        assert result["status"] == "success"
        assert result["chart_type"] == "box"
        assert result["file_type"] == "png"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_line_chart_plotly(self):
        """Test creating an interactive line chart with plotly"""
        df = pd.DataFrame({
            'date': ['2024-01', '2024-02', '2024-03', '2024-04'],
            'sales': [100, 150, 120, 180]
        })
        
        result = create_visualization(
            df,
            "line",
            {"x": "date", "y": "sales", "title": "Sales Over Time", "interactive": True}
        )
        
        assert result["status"] == "success"
        assert result["chart_type"] == "line"
        assert result["file_type"] == "html"
        assert result["interactive"] is True
        assert os.path.exists(result["file_path"])
        assert result["file_path"].endswith(".html")
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_bar_chart_plotly(self):
        """Test creating an interactive bar chart with plotly"""
        df = pd.DataFrame({
            'category': ['A', 'B', 'C', 'D'],
            'value': [25, 40, 30, 45]
        })
        
        result = create_visualization(
            df,
            "bar",
            {"x": "category", "y": "value", "title": "Category Values", "interactive": True}
        )
        
        assert result["status"] == "success"
        assert result["chart_type"] == "bar"
        assert result["file_type"] == "html"
        assert result["interactive"] is True
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_multiple_y_columns(self):
        """Test creating a line chart with multiple y columns"""
        df = pd.DataFrame({
            'date': ['2024-01', '2024-02', '2024-03'],
            'sales': [100, 150, 120],
            'profit': [20, 30, 25]
        })
        
        result = create_visualization(
            df,
            "line",
            {"x": "date", "y": ["sales", "profit"], "title": "Sales and Profit"}
        )
        
        assert result["status"] == "success"
        assert result["chart_type"] == "line"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_custom_output_dir(self):
        """Test creating visualization with custom output directory"""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            df = pd.DataFrame({
                'x': [1, 2, 3],
                'y': [4, 5, 6]
            })
            
            result = create_visualization(
                df,
                "line",
                {"x": "x", "y": "y", "output_dir": temp_dir}
            )
            
            assert result["status"] == "success"
            assert result["file_path"].startswith(temp_dir)
            assert os.path.exists(result["file_path"])
    
    def test_create_visualization_custom_figsize_dpi(self):
        """Test creating visualization with custom figsize and dpi"""
        df = pd.DataFrame({
            'x': [1, 2, 3],
            'y': [4, 5, 6]
        })
        
        result = create_visualization(
            df,
            "line",
            {"x": "x", "y": "y", "figsize": (12, 8), "dpi": 150}
        )
        
        assert result["status"] == "success"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        df = pd.DataFrame()
        
        result = create_visualization(df, "line", {"x": "x", "y": "y"})
        
        assert result["status"] == "error"
        assert "empty" in result["message"].lower()
    
    def test_create_visualization_invalid_chart_type(self):
        """Test handling of invalid chart type"""
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        
        result = create_visualization(df, "invalid_type", {"x": "x", "y": "y"})
        
        assert result["status"] == "error"
        assert "invalid chart type" in result["message"].lower()
    
    def test_create_visualization_missing_required_column(self):
        """Test handling of missing required column"""
        df = pd.DataFrame({'x': [1, 2, 3]})
        
        result = create_visualization(df, "line", {"x": "x", "y": "nonexistent"})
        
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()
    
    def test_create_visualization_missing_x_config(self):
        """Test handling of missing x in config for line chart"""
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        
        result = create_visualization(df, "line", {"y": "y"})
        
        assert result["status"] == "error"
        assert "requires" in result["message"].lower()
    
    def test_create_visualization_missing_y_config(self):
        """Test handling of missing y in config for line chart"""
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        
        result = create_visualization(df, "line", {"x": "x"})
        
        assert result["status"] == "error"
        assert "requires" in result["message"].lower()
    
    def test_create_visualization_heatmap_insufficient_columns(self):
        """Test heatmap with insufficient numeric columns"""
        df = pd.DataFrame({'x': [1, 2, 3]})
        
        result = create_visualization(df, "heatmap", {})
        
        assert result["status"] == "error"
        assert "at least 2" in result["message"].lower()
    
    def test_create_visualization_dict_input(self):
        """Test create_visualization with dictionary input"""
        data = {
            'x': [1, 2, 3, 4],
            'y': [2, 4, 6, 8]
        }
        
        result = create_visualization(data, "line", {"x": "x", "y": "y"})
        
        assert result["status"] == "success"
        assert result["chart_type"] == "line"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_none_input(self):
        """Test handling of None input"""
        result = create_visualization(None, "line", {"x": "x", "y": "y"})
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_create_visualization_empty_chart_type(self):
        """Test handling of empty chart_type"""
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        
        result = create_visualization(df, "", {"x": "x", "y": "y"})
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_create_visualization_scatter_with_color(self):
        """Test scatter plot with color grouping"""
        df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 5, 4, 6],
            'category': ['A', 'A', 'B', 'B', 'A']
        })
        
        result = create_visualization(
            df,
            "scatter",
            {"x": "x", "y": "y", "color": "category"}
        )
        
        assert result["status"] == "success"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_create_visualization_box_plot_grouped(self):
        """Test grouped box plot"""
        df = pd.DataFrame({
            'category': ['A', 'A', 'A', 'B', 'B', 'B'],
            'value': [1, 2, 3, 4, 5, 6]
        })
        
        result = create_visualization(
            df,
            "box",
            {"x": "category", "y": "value"}
        )
        
        assert result["status"] == "success"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])


# Import the new function
from app.tools.data_analysis_tools import create_visualization, build_dashboard


class TestBuildDashboard:
    """Tests for build_dashboard function"""
    
    def test_build_dashboard_basic(self):
        """Test creating a basic dashboard with multiple components"""
        df = pd.DataFrame({
            'date': ['2024-01', '2024-02', '2024-03'],
            'sales': [100, 150, 120],
            'profit': [20, 30, 25]
        })
        
        components = [
            {
                "type": "metric",
                "config": {
                    "value": 370,
                    "label": "Total Sales",
                    "format": "${:,.0f}"
                }
            },
            {
                "type": "chart",
                "data": df,
                "config": {
                    "chart_type": "line",
                    "x": "date",
                    "y": "sales",
                    "title": "Sales Trend"
                }
            },
            {
                "type": "table",
                "data": df,
                "config": {
                    "title": "Sales Data",
                    "columns": ["date", "sales", "profit"]
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Sales Dashboard"
        )
        
        assert result["status"] == "success"
        assert result["file_type"] == "html"
        assert result["component_count"] == 3
        assert result["title"] == "Sales Dashboard"
        assert os.path.exists(result["file_path"])
        assert result["file_path"].endswith(".html")
        assert result["file_size_bytes"] > 0
        
        # Verify HTML content
        with open(result["file_path"], 'r') as f:
            html_content = f.read()
            assert "Sales Dashboard" in html_content
            assert "Total Sales" in html_content
            assert "Sales Trend" in html_content
            assert "plotly" in html_content.lower()
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_metric_component(self):
        """Test dashboard with metric components"""
        components = [
            {
                "type": "metric",
                "config": {
                    "value": 1250.50,
                    "label": "Revenue",
                    "format": "${:,.2f}"
                }
            },
            {
                "type": "metric",
                "config": {
                    "value": 0.85,
                    "label": "Conversion Rate",
                    "format": "{:.1%}"
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Metrics Dashboard"
        )
        
        assert result["status"] == "success"
        assert result["component_count"] == 2
        assert os.path.exists(result["file_path"])
        
        # Verify HTML content
        with open(result["file_path"], 'r') as f:
            html_content = f.read()
            assert "Revenue" in html_content
            assert "Conversion Rate" in html_content
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_chart_component(self):
        """Test dashboard with chart components"""
        df = pd.DataFrame({
            'category': ['A', 'B', 'C', 'D'],
            'value': [25, 40, 30, 45]
        })
        
        components = [
            {
                "type": "chart",
                "data": df,
                "config": {
                    "chart_type": "bar",
                    "x": "category",
                    "y": "value",
                    "title": "Category Distribution"
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Chart Dashboard"
        )
        
        assert result["status"] == "success"
        assert result["component_count"] == 1
        assert os.path.exists(result["file_path"])
        
        # Verify HTML content
        with open(result["file_path"], 'r') as f:
            html_content = f.read()
            assert "Category Distribution" in html_content
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_table_component(self):
        """Test dashboard with table component"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [30, 25, 35],
            'salary': [50000, 45000, 60000]
        })
        
        components = [
            {
                "type": "table",
                "data": df,
                "config": {
                    "title": "Employee Data",
                    "columns": ["name", "age", "salary"],
                    "max_rows": 10
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Table Dashboard"
        )
        
        assert result["status"] == "success"
        assert result["component_count"] == 1
        assert os.path.exists(result["file_path"])
        
        # Verify HTML content
        with open(result["file_path"], 'r') as f:
            html_content = f.read()
            assert "Employee Data" in html_content
            assert "Alice" in html_content
            assert "Bob" in html_content
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_text_component(self):
        """Test dashboard with text component"""
        components = [
            {
                "type": "text",
                "config": {
                    "title": "Summary",
                    "content": "<p>This is a <strong>summary</strong> of the analysis.</p>"
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Text Dashboard"
        )
        
        assert result["status"] == "success"
        assert result["component_count"] == 1
        assert os.path.exists(result["file_path"])
        
        # Verify HTML content
        with open(result["file_path"], 'r') as f:
            html_content = f.read()
            assert "Summary" in html_content
            assert "summary" in html_content
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_custom_layout(self):
        """Test dashboard with custom layout"""
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        
        components = [
            {
                "type": "chart",
                "data": df,
                "config": {"chart_type": "line", "x": "x", "y": "y", "title": "Chart 1"}
            },
            {
                "type": "chart",
                "data": df,
                "config": {"chart_type": "bar", "x": "x", "y": "y", "title": "Chart 2"}
            },
            {
                "type": "chart",
                "data": df,
                "config": {"chart_type": "scatter", "x": "x", "y": "y", "title": "Chart 3"}
            }
        ]
        
        layout = {
            "columns": 3,
            "theme": "dark"
        }
        
        result = build_dashboard(
            components=components,
            layout=layout,
            title="Custom Layout Dashboard"
        )
        
        assert result["status"] == "success"
        assert result["layout"]["columns"] == 3
        assert result["layout"]["theme"] == "dark"
        assert os.path.exists(result["file_path"])
        
        # Verify HTML content has dark theme
        with open(result["file_path"], 'r') as f:
            html_content = f.read()
            assert "#1a1a1a" in html_content  # Dark background color
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_light_theme(self):
        """Test dashboard with light theme"""
        components = [
            {
                "type": "metric",
                "config": {"value": 100, "label": "Test Metric"}
            }
        ]
        
        layout = {"theme": "light"}
        
        result = build_dashboard(
            components=components,
            layout=layout,
            title="Light Theme Dashboard"
        )
        
        assert result["status"] == "success"
        assert result["layout"]["theme"] == "light"
        assert os.path.exists(result["file_path"])
        
        # Verify HTML content has light theme
        with open(result["file_path"], 'r') as f:
            html_content = f.read()
            assert "#ffffff" in html_content  # Light background color
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_custom_output_dir(self):
        """Test dashboard with custom output directory"""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            components = [
                {
                    "type": "metric",
                    "config": {"value": 42, "label": "Answer"}
                }
            ]
            
            result = build_dashboard(
                components=components,
                title="Custom Dir Dashboard",
                output_dir=temp_dir
            )
            
            assert result["status"] == "success"
            assert result["file_path"].startswith(temp_dir)
            assert os.path.exists(result["file_path"])
    
    def test_build_dashboard_dict_data(self):
        """Test dashboard with dictionary data instead of DataFrame"""
        data = {
            'x': [1, 2, 3, 4],
            'y': [10, 20, 15, 25]
        }
        
        components = [
            {
                "type": "chart",
                "data": data,
                "config": {
                    "chart_type": "line",
                    "x": "x",
                    "y": "y",
                    "title": "Line Chart"
                }
            },
            {
                "type": "table",
                "data": data,
                "config": {
                    "title": "Data Table"
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Dict Data Dashboard"
        )
        
        assert result["status"] == "success"
        assert result["component_count"] == 2
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_table_max_rows(self):
        """Test table component with max_rows limit"""
        # Create DataFrame with more than max_rows
        df = pd.DataFrame({
            'id': range(1, 21),
            'value': range(100, 120)
        })
        
        components = [
            {
                "type": "table",
                "data": df,
                "config": {
                    "title": "Limited Table",
                    "max_rows": 5
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Limited Table Dashboard"
        )
        
        assert result["status"] == "success"
        assert os.path.exists(result["file_path"])
        
        # Verify HTML shows row limit message
        with open(result["file_path"], 'r') as f:
            html_content = f.read()
            assert "Showing 5 of 20 rows" in html_content
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_empty_components(self):
        """Test handling of empty components list"""
        result = build_dashboard(
            components=[],
            title="Empty Dashboard"
        )
        
        assert result["status"] == "error"
        assert "non-empty list" in result["message"].lower()
    
    def test_build_dashboard_none_components(self):
        """Test handling of None components"""
        result = build_dashboard(
            components=None,
            title="None Dashboard"
        )
        
        assert result["status"] == "error"
        assert "non-empty list" in result["message"].lower()
    
    def test_build_dashboard_invalid_components_type(self):
        """Test handling of invalid components type"""
        result = build_dashboard(
            components="invalid",
            title="Invalid Dashboard"
        )
        
        assert result["status"] == "error"
        assert "non-empty list" in result["message"].lower()
    
    def test_build_dashboard_empty_title(self):
        """Test handling of empty title"""
        components = [
            {
                "type": "metric",
                "config": {"value": 100, "label": "Test"}
            }
        ]
        
        result = build_dashboard(
            components=components,
            title=""
        )
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_build_dashboard_invalid_theme(self):
        """Test handling of invalid theme"""
        components = [
            {
                "type": "metric",
                "config": {"value": 100, "label": "Test"}
            }
        ]
        
        layout = {"theme": "invalid_theme"}
        
        result = build_dashboard(
            components=components,
            layout=layout,
            title="Invalid Theme Dashboard"
        )
        
        assert result["status"] == "error"
        assert "invalid theme" in result["message"].lower()
    
    def test_build_dashboard_component_without_type(self):
        """Test handling of component without type field"""
        components = [
            {
                "config": {"value": 100}
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Missing Type Dashboard"
        )
        
        # Should succeed but skip the invalid component
        assert result["status"] == "success"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_invalid_component_type(self):
        """Test handling of invalid component type"""
        components = [
            {
                "type": "invalid_type",
                "config": {}
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Invalid Component Dashboard"
        )
        
        # Should succeed but skip the invalid component
        assert result["status"] == "success"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_chart_missing_data(self):
        """Test chart component with missing data"""
        components = [
            {
                "type": "chart",
                "config": {
                    "chart_type": "line",
                    "x": "x",
                    "y": "y"
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Missing Data Dashboard"
        )
        
        # Should succeed but show error in component
        assert result["status"] == "success"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_metric_missing_value(self):
        """Test metric component with missing value"""
        components = [
            {
                "type": "metric",
                "config": {
                    "label": "Test Metric"
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Missing Value Dashboard"
        )
        
        # Should succeed but show error in component
        assert result["status"] == "success"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_text_missing_content(self):
        """Test text component with missing content"""
        components = [
            {
                "type": "text",
                "config": {
                    "title": "Test Text"
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Missing Content Dashboard"
        )
        
        # Should succeed but show error in component
        assert result["status"] == "success"
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_multiple_chart_types(self):
        """Test dashboard with multiple different chart types"""
        df = pd.DataFrame({
            'category': ['A', 'B', 'C'],
            'value1': [10, 20, 15],
            'value2': [5, 15, 10]
        })
        
        components = [
            {
                "type": "chart",
                "data": df,
                "config": {
                    "chart_type": "bar",
                    "x": "category",
                    "y": "value1",
                    "title": "Bar Chart"
                }
            },
            {
                "type": "chart",
                "data": df,
                "config": {
                    "chart_type": "pie",
                    "x": "category",
                    "y": "value1",
                    "title": "Pie Chart"
                }
            },
            {
                "type": "chart",
                "data": df,
                "config": {
                    "chart_type": "scatter",
                    "x": "value1",
                    "y": "value2",
                    "title": "Scatter Plot"
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Multi-Chart Dashboard"
        )
        
        assert result["status"] == "success"
        assert result["component_count"] == 3
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_formatted_metrics(self):
        """Test metric components with different format strings"""
        components = [
            {
                "type": "metric",
                "config": {
                    "value": 1234567.89,
                    "label": "Currency",
                    "format": "${:,.2f}"
                }
            },
            {
                "type": "metric",
                "config": {
                    "value": 0.7543,
                    "label": "Percentage",
                    "format": "{:.1%}"
                }
            },
            {
                "type": "metric",
                "config": {
                    "value": 42,
                    "label": "Integer",
                    "format": "{:,d}"
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Formatted Metrics Dashboard"
        )
        
        assert result["status"] == "success"
        assert result["component_count"] == 3
        assert os.path.exists(result["file_path"])
        
        # Cleanup
        os.unlink(result["file_path"])
    
    def test_build_dashboard_table_with_numeric_formatting(self):
        """Test table component formats numeric values correctly"""
        df = pd.DataFrame({
            'name': ['Product A', 'Product B'],
            'price': [1234.56, 789.01],
            'quantity': [100, 250]
        })
        
        components = [
            {
                "type": "table",
                "data": df,
                "config": {
                    "title": "Product Table"
                }
            }
        ]
        
        result = build_dashboard(
            components=components,
            title="Formatted Table Dashboard"
        )
        
        assert result["status"] == "success"
        assert os.path.exists(result["file_path"])
        
        # Verify numeric formatting in HTML
        with open(result["file_path"], 'r') as f:
            html_content = f.read()
            assert "1,234.56" in html_content  # Float formatting
            assert "100" in html_content  # Integer formatting
        
        # Cleanup
        os.unlink(result["file_path"])
