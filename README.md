# CSV Analyzer with Grouping

A Python utility for loading, analyzing, and grouping CSV files based on common columns. This tool is particularly useful when you need to process multiple CSV files and group their data based on a specific column while maintaining the original column structure.

## Features

- Load CSV files from a directory or specific file paths
- Group data by any common column across CSV files
- Preserve original column names without modification
- Track source files in the output
- Handle both matched and unmatched files separately
- Export results to organized CSV files

## Requirements

- Python 3.6+
- pandas
- pathlib

## Installation

1. Clone this repository or copy the `csv_analyzer.py` file to your project
2. Install required dependencies:

```bash
pip install pandas
```

## Usage

### Basic Usage

```python
from csv_analyzer import CSVAnalyzerGrouping

# Initialize the analyzer
analyzer = CSVAnalyzerGrouping()

# Load CSV files from a directory
analyzer.load_from_directory("path/to/your/csvs")

# Or load specific CSV files
analyzer.load_from_files(["file1.csv", "file2.csv"])

# Group data by a specific column
result = analyzer.grouped_data_by_column("category")

# Export the results
output_dir = ".tmp"
analyzer.export_matched_data(output_dir, result, "grouped_by_category")
analyzer.export_unmatched_data(output_dir, result)
```

### Output Structure

The tool will create:

- A combined CSV file containing all grouped data with original columns plus a source_file column
- The source_file column will always be the last column in the output
- Original column names are preserved without any aggregation suffixes

### Example Output Format

For input CSV files containing columns: `name,category,link,tag,label,id,x_path`

The output will maintain the same structure with source_file added as the last column:

```
name,category,link,tag,label,id,x_path,source_file
```

## Methods

### `load_from_directory(path: str)`

Loads all CSV files from the specified directory.

### `load_from_files(files: List[str])`

Loads specific CSV files from the provided file paths.

### `grouped_data_by_column(column_name: str)`

Groups data by the specified column for files that contain it.

### `export_matched_data(output_dir: str, dataset: Dict, output_prefix: str)`

Exports matched (grouped) data to a single combined CSV file.

### `export_unmatched_data(output_dir: str, dataset: Dict, output_prefix: str)`

Exports unmatched data to separate CSV files.

## Error Handling

The tool includes comprehensive error handling for:

- Invalid directory paths
- File reading errors
- Grouping operation failures
- Export errors

Each operation provides clear feedback through console messages.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
