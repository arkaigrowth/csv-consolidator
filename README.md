# CSV Consolidator

A Python utility to consolidate multiple CSV files into a single file while intelligently handling header mismatches and metadata. Designed to work with CSV files that may have metadata headers before the actual CSV data.

## Features

- Merges multiple CSV files into one
- Handles CSV files with metadata headers
- Detects and handles header mismatches
- Interactive prompt for handling new headers
- Intelligent date-based output filename generation
- Maintains separate directories for unprocessed and processed files
- Detailed logging of the consolidation process

## Directory Structure

```
csv_consolidator/
├── data/
│   ├── unprocessed/  (put your CSV files here)
│   └── processed/    (consolidated output goes here)
├── csv_consolidator.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone or download this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your CSV files in the `data/unprocessed` directory
2. Run the script:
```bash
python csv_consolidator.py [output_filename]
```

The script can be run in two ways:
- Without arguments: `python csv_consolidator.py`
  - Generates filename based on date range found in files
  - Format: `consolidated_MM-DD-YYYY_thru_MM-DD-YYYY.csv`
  - Example: `consolidated_04-09-2021_thru_03-02-2022.csv`
- With filename: `python csv_consolidator.py myoutput.csv`
  - Uses your specified filename

## CSV File Handling

### Metadata Headers
The script is designed to handle CSV files that have metadata headers before the actual CSV data. It will:
1. Skip metadata headers at the top of the file
2. Find the actual CSV headers (starting with "ID,Timestamp,Transaction Type")
3. Process the data from that point onward

### Header Mismatches
When different CSV files have different headers:
1. You'll be shown which files have different headers
2. You'll be prompted whether to include the new columns
3. If you choose 'no', only common headers will be included
4. If you choose 'yes', all unique headers will be included (with NaN for missing values)

## Date Detection

The script looks for dates in the following column names (case-insensitive):
- date
- timestamp
- created_at
- datetime
- time

These dates are used to generate the output filename when no filename is specified.

## Git Integration

The repository is configured to:
- Ignore all files in `data/unprocessed` and `data/processed`
- Keep the directory structure using `.gitkeep` files
- Ignore Python virtual environment and cache files
- Ignore system files like `.DS_Store`

## Error Handling

- Invalid CSV files are logged and skipped
- Detailed error messages for file reading issues
- Verification of input parameters
- Graceful handling of missing date information

## Output

The consolidated CSV file will:
- Include all specified headers
- Maintain data integrity
- Be placed in the `data/processed` directory
- Include a summary of:
  - Number of files processed
  - Total rows
  - Total columns
