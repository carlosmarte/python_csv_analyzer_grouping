import pandas as pd
import os
from excel_analyzer import ExcelAnalyzerGrouping

# First, let's create some sample Excel files for demonstration
def create_sample_excel_files(output_dir: str):
    """Create sample Excel files for testing"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Sales data across different regions
    sales_data = {
        'North': pd.DataFrame({
            'Product': ['A', 'B', 'C', 'A', 'B'],
            'Sales': [100, 150, 200, 120, 160],
            'Date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02', '2024-01-03'],
            'Region': ['North'] * 5
        }),
        'South': pd.DataFrame({
            'Product': ['A', 'B', 'C', 'B', 'C'],
            'Sales': [90, 140, 180, 130, 170],
            'Date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02', '2024-01-03'],
            'Region': ['South'] * 5
        })
    }
    
    # Customer data across different departments
    customer_data = {
        'Active': pd.DataFrame({
            'CustomerID': [1, 2, 3, 4, 5],
            'Name': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown', 'Charlie Davis'],
            'Status': ['Active'] * 5,
            'LastPurchase': ['2024-01-01', '2024-01-02', '2024-01-01', '2024-01-03', '2024-01-02']
        }),
        'Inactive': pd.DataFrame({
            'CustomerID': [6, 7, 8],
            'Name': ['Eve Johnson', 'Frank Miller', 'Grace Lee'],
            'Status': ['Inactive'] * 3,
            'LastPurchase': ['2023-11-01', '2023-10-15', '2023-12-01']
        })
    }
    
    # Save sales data
    with pd.ExcelWriter(os.path.join(output_dir, 'sales_data.xlsx')) as writer:
        sales_data['North'].to_excel(writer, sheet_name='North', index=False)
        sales_data['South'].to_excel(writer, sheet_name='South', index=False)
    
    # Save customer data
    with pd.ExcelWriter(os.path.join(output_dir, 'customer_data.xlsx')) as writer:
        customer_data['Active'].to_excel(writer, sheet_name='Active', index=False)
        customer_data['Inactive'].to_excel(writer, sheet_name='Inactive', index=False)

def main():
    # Create sample data
    temp_dir = ".tmp"
    create_sample_excel_files(temp_dir)
    
    # Initialize the analyzer with the directory
    analyzer = ExcelAnalyzerGrouping(temp_dir)
    
    # 1. List all loaded Excel files and their sheets
    print("\n1. Loaded Excel files and sheets:")
    files_and_sheets = analyzer.list_excel_files()
    for file, sheets in files_and_sheets.items():
        print(f"File: {file}")
        print(f"Sheets: {sheets}")
    
    # 2. View data from a specific sheet
    print("\n2. Data from North sheet of sales_data.xlsx:")
    north_data = analyzer.get_sheet_data("sales_data.xlsx", "North")
    print(north_data)
    
    # 3. Group data by Product across all sheets
    print("\n3. Grouping data by Product:")
    grouped_data = analyzer.grouped_data_by_column("Product")
    
    print("\nMatched files (containing Product column):")
    for file, df in grouped_data['matched'].items():
        print(f"\nFile: {file}")
        print(df)
    
    print("\nUnmatched files (without Product column):")
    for file in grouped_data['unmatched'].keys():
        print(file)
    
    # 4. Search for a specific customer
    print("\n4. Searching for 'John':")
    search_results = analyzer.search_column_value("John")
    print(search_results)
    
    # 5. Get all sales data
    print("\n5. Getting all Sales column data:")
    sales_data = analyzer.get_column_data("Sales")
    for file, data in sales_data.items():
        print(f"\nFile: {file}")
        print(data)
    
    # 6. List all columns across files
    print("\n6. All matched columns:")
    matched_columns = analyzer.list_all_matched_columns()
    for file, columns in matched_columns.items():
        print(f"\nFile: {file}")
        print(f"Columns: {columns}")
    
    # 7. Export grouped data
    print("\n7. Exporting grouped data:")
    output_dir = ".tmp/output"
    analyzer.export_matched_data(output_dir, grouped_data, "product_grouped")
    print(f"Exported grouped data to {output_dir}")

if __name__ == "__main__":
    main()