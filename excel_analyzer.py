import pandas as pd
import os
from typing import Dict, Optional, List
from pathlib import Path
from csv_analyzer import CSVAnalyzerGrouping

class ExcelAnalyzerGrouping:
    """
    A class to load Excel files and analyze them using CSVAnalyzerGrouping functionality.
    Supports .xlsx files with multiple sheets.
    """

    def __init__(self, directory: Optional[str] = None):
        """
        Initialize the ExcelAnalyzerGrouping.
        
        Args:
            directory (Optional[str]): Directory path containing Excel files.
        """
        self.analyzer = CSVAnalyzerGrouping()
        self.excel_files: Dict[str, Dict[str, pd.DataFrame]] = {}  # {filename: {sheet_name: df}}
        
        if directory:
            self.load_from_directory(directory)

    def load_from_directory(self, path: str) -> None:
        """
        Load all Excel files from the specified directory.

        Args:
            path (str): Directory path containing Excel files.

        Raises:
            FileNotFoundError: If the directory doesn't exist.
        """
        directory = Path(path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        excel_files = list(directory.glob("*.xlsx"))
        self.load_from_files([str(f) for f in excel_files])

    def load_from_files(self, files: List[str]) -> None:
        """
        Load specified Excel files.

        Args:
            files (List[str]): List of file paths to Excel files.
        """
        self.excel_files.clear()
        dataframes_dict = {}

        for file_path in files:
            try:
                # Read all sheets from the Excel file
                xlsx = pd.ExcelFile(file_path)
                sheets_dict = {}
                
                for sheet_name in xlsx.sheet_names:
                    df = pd.read_excel(xlsx, sheet_name=sheet_name)
                    sheets_dict[sheet_name] = df
                    
                    # Create a unique identifier for each sheet
                    base_name = os.path.basename(file_path)
                    df_name = f"{base_name}|{sheet_name}"
                    dataframes_dict[df_name] = df
                
                self.excel_files[file_path] = sheets_dict
                print(f"Successfully loaded Excel file: {file_path}")
                
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")

        # Pass all dataframes to the CSV analyzer
        self.analyzer.use_dataframes(dataframes_dict)

    def list_excel_files(self) -> Dict[str, List[str]]:
        """
        List all loaded Excel files and their sheets.

        Returns:
            Dict[str, List[str]]: Dictionary with Excel filenames as keys and list of sheet names as values.
        """
        return {
            os.path.basename(file_path): list(sheets.keys())
            for file_path, sheets in self.excel_files.items()
        }

    def get_sheet_data(self, file_name: str, sheet_name: str) -> Optional[pd.DataFrame]:
        """
        Get data from a specific sheet in a specific Excel file.

        Args:
            file_name (str): Name of the Excel file
            sheet_name (str): Name of the sheet

        Returns:
            Optional[pd.DataFrame]: DataFrame containing the sheet data, or None if not found
        """
        for file_path, sheets in self.excel_files.items():
            if os.path.basename(file_path) == file_name and sheet_name in sheets:
                return sheets[sheet_name]
        return None

    # Delegate analysis methods to CSVAnalyzerGrouping
    def grouped_data_by_column(self, column_name: str):
        """Delegate to CSVAnalyzerGrouping"""
        return self.analyzer.grouped_data_by_column(column_name)

    def export_matched_data(self, output_dir: str, dataset: Dict, output_prefix: str = "grouped"):
        """Delegate to CSVAnalyzerGrouping"""
        return self.analyzer.export_matched_data(output_dir, dataset, output_prefix)

    def export_unmatched_data(self, output_dir: str, dataset: Dict, output_prefix: str = "grouped"):
        """Delegate to CSVAnalyzerGrouping"""
        return self.analyzer.export_unmatched_data(output_dir, dataset, output_prefix)

    def list_all_matched_columns(self):
        """Delegate to CSVAnalyzerGrouping"""
        return self.analyzer.list_all_matched_columns()

    def list_all_unmatched_columns(self):
        """Delegate to CSVAnalyzerGrouping"""
        return self.analyzer.list_all_unmatched_columns()

    def get_column_data(self, column_name: str):
        """Delegate to CSVAnalyzerGrouping"""
        return self.analyzer.get_column_data(column_name)

    def search_column_value(self, value=None, **kwargs):
        """Delegate to CSVAnalyzerGrouping"""
        return self.analyzer.search_column_value(value, **kwargs)