
import pandas as pd
from csv_analyzer import CSVAnalyzerGrouping


# self.analyzer = CSVAnalyzerGrouping(directory="__tests__/testdata")
# output_dir = ".tmp"
# # Group data by a specific column
# result = self.analyzer.grouped_data_by_column("category")
# self.analyzer.export_matched_data(output_dir, result, "grouped_by_category")
# self.analyzer.export_unmatched_data(output_dir, result)

# Initialize the analyzer
analyzer = CSVAnalyzerGrouping()

# Group data by a specific column
result = analyzer.load_from_directory("__tests__/testdata")

# # List all columns in each file
# columns = analyzer.list_all_matched_columns()
# print(columns)

# # Find missing columns
# unmatched = analyzer.list_all_unmatched_columns()
# print(unmatched)

# # Get all loaded filenames
# files = analyzer.list_all_filenames()
# print(files)


# # Get data from a specific column
# category_data = analyzer.get_column_data("category")
# print(category_data)

# # Search for a value across all columns
results = analyzer.search_column_value("track01-name-3")
print(results)

# Search for specific column values
results = analyzer.search_column_value(description="track01-d-4", name="track01-name-3")
# print(results)