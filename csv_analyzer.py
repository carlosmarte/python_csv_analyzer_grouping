import pandas as pd
import os
from typing import Dict, List, Union, Optional, Set
from pathlib import Path

class CSVAnalyzerGrouping:
    """
    A class to load, analyze, and group CSV files based on column presence
    and perform grouped operations on the data.
    """

    def __init__(self, directory: Optional[str] = None):
        """Initialize the CSVAnalyzerGrouping with empty data storage."""
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.all_columns: Set[str] = set()

        if directory:
            self.load_from_directory(directory)

    def load_from_directory(self, path: str) -> None:
        """
        Load all CSV files from the specified directory into Pandas DataFrames.

        Args:
            path (str): Directory path containing CSV files.

        Raises:
            FileNotFoundError: If the directory doesn't exist.
        """
        directory = Path(path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        csv_files = list(directory.glob("*.csv"))
        self.load_from_files([str(f) for f in csv_files])

    def use_dataframes(self, dataframes: Dict[str, pd.DataFrame]) -> None:
        """
        Use existing pandas DataFrames instead of loading from files.

        Args:
            dataframes (Dict[str, pd.DataFrame]): Dictionary mapping names to DataFrames.
        """
        self.dataframes.clear()
        self.all_columns.clear()
        
        for name, df in dataframes.items():
            try:
                if not isinstance(df, pd.DataFrame):
                    raise ValueError(f"Value for {name} is not a pandas DataFrame")
                self.dataframes[name] = df
                self.all_columns.update(df.columns)
                print(f"Successfully loaded DataFrame: {name}")
            except Exception as e:
                print(f"Error loading DataFrame {name}: {str(e)}")

    def load_from_files(self, files: List[str]) -> None:
        """
        Load specified CSV files into Pandas DataFrames.

        Args:
            files (List[str]): List of file paths to CSV files.
        """
        self.dataframes.clear()
        self.all_columns.clear()
        
        for file_path in files:
            try:
                df = pd.read_csv(file_path)
                self.dataframes[file_path] = df
                self.all_columns.update(df.columns)
                print(f"Successfully loaded: {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")

    def _create_agg_functions(self, df: pd.DataFrame, column_name: str) -> Dict[str, str]:
        """
        Create aggregation functions for each column, using 'first' to maintain original values.

        Args:
            df (pd.DataFrame): DataFrame to analyze
            column_name (str): Name of the grouping column to exclude

        Returns:
            Dict[str, str]: Dictionary of column names and their aggregation functions
        """
        agg_funcs = {}
        for col in df.columns:
            if col != column_name and not df[col].isna().all():  # Only include non-NaN columns
                agg_funcs[col] = 'first'
        return agg_funcs

    def grouped_data_by_column(self, column_name: str) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Group data by specified column for files that contain it.
        Only includes non-NaN columns from the original CSV being grouped.

        Args:
            column_name (str): Column name to group by.

        Returns:
            Dict containing:
                'matched': Dict[str, pd.DataFrame] - Grouped data from files with the column
                'unmatched': Dict[str, pd.DataFrame] - Data from files without the column
        """
        matched_dfs = {}
        unmatched_dfs = {}

        # Split into matched and unmatched
        for file_path, df in self.dataframes.items():
            if column_name in df.columns and not df[column_name].isna().all():
                # Remove columns that are all NaN
                non_nan_cols = [col for col in df.columns if not df[col].isna().all()]
                matched_dfs[file_path] = df[non_nan_cols]
            else:
                unmatched_dfs[file_path] = df

        # Group matched data
        grouped_matched_dfs = {}
        for file_path, df in matched_dfs.items():
            try:
                # Create appropriate aggregation functions
                agg_funcs = self._create_agg_functions(df, column_name)
                
                # Perform grouping with simple aggregation to maintain original column names
                grouped_df = df.groupby(column_name).agg(agg_funcs)
                
                # Remove the multi-level column index to keep original column names
                if isinstance(grouped_df.columns, pd.MultiIndex):
                    grouped_df.columns = grouped_df.columns.get_level_values(0)
                
                grouped_matched_dfs[file_path] = grouped_df
                print(f"Successfully grouped data from: {file_path}")
            except Exception as e:
                print(f"Error grouping data from {file_path}: {str(e)}")
                unmatched_dfs[file_path] = df  # Move to unmatched if grouping fails

        return {
            "matched": grouped_matched_dfs,
            "unmatched": unmatched_dfs
        }

    def export_matched_data(self, output_dir: str, dataset: Dict[str, Dict[str, pd.DataFrame]], 
                          output_prefix: str = "grouped") -> None:
        """
        Export matched (grouped) data to a single combined CSV file.
        Only includes non-NaN columns from the original CSV files being grouped.

        Args:
            output_dir (str): Directory to save the exported file.
            dataset (Dict): Dataset containing matched and unmatched data.
            output_prefix (str): Prefix for output filename.
        """
        matched_data = dataset.get("matched", {})
        if not matched_data:
            print("No matched data to export")
            return

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Initialize an empty list to store all DataFrames
            all_dfs = []

            # Process each grouped DataFrame
            for file_path, df in matched_data.items():
                # Remove columns that are all NaN
                non_nan_cols = [col for col in df.columns if not df[col].isna().all()]
                df_cleaned = df[non_nan_cols]

                if isinstance(df_cleaned.index, pd.MultiIndex) or df_cleaned.index.name is not None:
                    df_cleaned = df_cleaned.reset_index()
                
                # Add source file information
                df_cleaned['source_file'] = os.path.basename(file_path)
                all_dfs.append(df_cleaned)

            # Combine all DataFrames
            combined_df = pd.concat(all_dfs, axis=0, ignore_index=True)
            
            # Reorder columns to ensure source_file is last
            cols = [col for col in combined_df.columns if col != 'source_file'] + ['source_file']
            combined_df = combined_df[cols]

            # Export combined DataFrame
            output_path = os.path.join(output_dir, f"{output_prefix}_combined.csv")
            combined_df.to_csv(output_path, index=False)
            print(f"Successfully exported combined data to: {output_path}")

        except Exception as e:
            print(f"Error exporting combined data: {str(e)}")

    def export_unmatched_data(self, output_dir: str, dataset: Dict[str, Dict[str, pd.DataFrame]], 
                            output_prefix: str = "grouped") -> None:
        """
        Export unmatched data to CSV files.

        Args:
            output_dir (str): Directory to save the exported files.
            dataset (Dict): Dataset containing matched and unmatched data.
            output_prefix (str): Prefix for output filenames.
        """
        self._export_data(output_dir, dataset.get("unmatched", {}), output_prefix)

    def _export_data(self, output_dir: str, data: Dict[str, pd.DataFrame], 
                    output_prefix: str) -> None:
        """
        Helper method to export DataFrames to CSV files.

        Args:
            output_dir (str): Directory to save the exported files.
            data (Dict[str, pd.DataFrame]): Dictionary of DataFrames to export.
            output_prefix (str): Prefix for output filenames.
        """
        os.makedirs(output_dir, exist_ok=True)

        for file_path, df in data.items():
            try:
                # Extract original filename without extension
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(output_dir, f"{output_prefix}_{base_name}.csv")

                # Reset index if it's a grouped DataFrame
                if isinstance(df.index, pd.MultiIndex) or df.index.name is not None:
                    df = df.reset_index()

                df.to_csv(output_path, index=False)
                print(f"Successfully exported: {output_path}")
            except Exception as e:
                print(f"Error exporting {file_path}: {str(e)}")

    def list_all_matched_columns(self) -> Dict[str, List[str]]:
        """
        List all columns present in each CSV file that contains matches.
        
        Returns:
            Dict[str, List[str]]: Dictionary with filenames as keys and their columns as values.
        """
        return {os.path.basename(file_path): list(df.columns) 
                for file_path, df in self.dataframes.items()}

    def list_all_unmatched_columns(self) -> Dict[str, List[str]]:
        """
        List columns that are not present in all CSV files.
        
        Returns:
            Dict[str, List[str]]: Dictionary with filenames as keys and their unique columns as values.
        """
        # Get all columns from all files
        all_columns = set()
        for df in self.dataframes.values():
            all_columns.update(df.columns)
        
        # Find unmatched columns for each file
        unmatched_columns = {}
        for file_path, df in self.dataframes.items():
            missing_cols = all_columns - set(df.columns)
            if missing_cols:
                unmatched_columns[os.path.basename(file_path)] = list(missing_cols)
        
        return unmatched_columns

    def list_all_filenames(self) -> List[str]:
        """
        List all loaded CSV filenames.
        
        Returns:
            List[str]: List of loaded CSV filenames.
        """
        return [os.path.basename(file_path) for file_path in self.dataframes.keys()]

    def get_column_data(self, column_name: str) -> Dict[str, pd.Series]:
        """
        Get all non-NaN data from a specific column across all CSVs that contain it.
        
        Args:
            column_name (str): Name of the column to retrieve.
            
        Returns:
            Dict[str, pd.Series]: Dictionary with filenames as keys and column data as values.
        """
        column_data = {}
        for file_path, df in self.dataframes.items():
            if column_name in df.columns and not df[column_name].isna().all():
                # Only include non-NaN values
                non_nan_data = df[column_name].dropna()
                if not non_nan_data.empty:
                    column_data[os.path.basename(file_path)] = non_nan_data
        return column_data

    def search_column_value(self, value: Union[str, int, float] = None, **kwargs) -> pd.DataFrame:
        """
        Search for rows containing a specific value across all non-NaN columns or matching specific column values.
        
        Args:
            value: Value to search for across all columns (optional)
            **kwargs: Column-value pairs to search for (e.g., name='John')
            
        Returns:
            pd.DataFrame: DataFrame containing all matching rows with source_file column.
            
        Example:
            # Search for value across all columns
            df = analyzer.search_column_value("John")
            
            # Search for specific column value
            df = analyzer.search_column_value(name="John")
            
            # Search with multiple conditions
            df = analyzer.search_column_value(name="John", age=30)
        """
        matching_dfs = []

        for file_path, df in self.dataframes.items():
            # Remove columns that are all NaN
            non_nan_cols = [col for col in df.columns if not df[col].isna().all()]
            df_cleaned = df[non_nan_cols].copy()
            df_cleaned['source_file'] = os.path.basename(file_path)
            
            if value is not None:
                # Search for value across all non-NaN columns
                mask = df_cleaned.astype(str).apply(lambda x: x.str.contains(str(value), 
                                                                        case=False, 
                                                                        na=False)).any(axis=1)
                matching_dfs.append(df_cleaned[mask])
            elif kwargs:
                # Search for specific column-value pairs in non-NaN columns
                mask = pd.Series(True, index=df_cleaned.index)
                for col, val in kwargs.items():
                    if col in df_cleaned.columns:
                        mask &= df_cleaned[col].astype(str).str.contains(str(val), 
                                                                    case=False, 
                                                                    na=False)
                matching_dfs.append(df_cleaned[mask])

        if not matching_dfs:
            return pd.DataFrame()

        # Combine all matching rows and ensure source_file is the last column
        result = pd.concat(matching_dfs, axis=0, ignore_index=True)
        cols = [col for col in result.columns if col != 'source_file'] + ['source_file']
        return result[cols]