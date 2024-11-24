import pandas as pd
import sys
import glob
from pathlib import Path
import logging
import os
from datetime import datetime

"""
csv_consolidator/
├── data/
│   ├── unprocessed/  (put your CSV files here)
│   └── processed/    (consolidated files go here)
├── csv_consolidator.py
├── requirements.txt
└── README.md
"""

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Define default directories
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / 'data'
UNPROCESSED_DIR = DATA_DIR / 'unprocessed'
PROCESSED_DIR = DATA_DIR / 'processed'

def get_csv_date(df):
    """
    Try to get the earliest date from a dataframe by checking common date column names
    and parsing the first row's date.
    """
    date_columns = ['date', 'timestamp', 'created_at', 'datetime', 'time', 'Timestamp']
    for col in df.columns:
        col_lower = col.lower()
        if any(date_name in col_lower for date_name in date_columns):
            try:
                dates = pd.to_datetime(df[col])
                if not dates.empty:
                    return dates.min()
            except:
                continue
    return None

def read_csv_with_metadata(file_path):
    """
    Read a CSV file that might have metadata headers before the actual CSV data.
    """
    try:
        # First, read all lines to find where the actual CSV data starts
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Find the line that contains the actual CSV headers
        header_index = -1
        for i, line in enumerate(lines):
            if 'ID,Timestamp,Transaction Type' in line:
                header_index = i
                break
        
        if header_index == -1:
            raise ValueError("Could not find CSV headers")
        
        # Read the CSV starting from the header line
        df = pd.read_csv(file_path, skiprows=header_index)
        return df
    
    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        raise

def get_all_headers(csv_files):
    """Get all unique headers from the CSV files."""
    all_headers = set()
    headers_by_file = {}
    
    for file in csv_files:
        try:
            df = read_csv_with_metadata(file)
            headers = set(df.columns)
            headers_by_file[file] = headers
            all_headers.update(headers)
        except Exception as e:
            logger.error(f"Error reading headers from {file}: {str(e)}")
            raise
    
    return all_headers, headers_by_file

def generate_date_range_filename(dfs):
    """
    Generate a filename based on the earliest and latest dates found in the dataframes.
    Format: consolidated_MM-DD-YYYY_thru_MM-DD-YYYY.csv
    """
    all_dates = []
    
    # Try to find dates in each dataframe
    for df in dfs:
        df_date = get_csv_date(df)
        if df_date is not None:
            all_dates.append(df_date)
    
    if all_dates:
        earliest = min(all_dates)
        latest = max(all_dates)
        return f'consolidated_{earliest.strftime("%m-%d-%Y")}_thru_{latest.strftime("%m-%d-%Y")}.csv'
    else:
        # Fallback to current timestamp if no dates found
        timestamp = datetime.now().strftime('%m-%d-%Y')
        return f'consolidated_{timestamp}.csv'

def consolidate_csvs(output_filename=None):
    """
    Consolidate multiple CSV files from the unprocessed directory into one file in the processed directory.
    
    Args:
        output_filename: Optional name for the output file. If not provided, a date range based name will be used.
    """
    # Ensure directories exist
    UNPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get list of CSV files
    csv_files = list(UNPROCESSED_DIR.glob('*.csv'))
    if not csv_files:
        logger.error(f"No CSV files found in {UNPROCESSED_DIR}")
        return

    logger.info(f"Found {len(csv_files)} CSV files to process")
    
    try:
        # Get all unique headers
        all_headers, headers_by_file = get_all_headers(csv_files)
        
        # Check for header mismatches
        base_headers = headers_by_file[csv_files[0]]
        new_headers = all_headers - base_headers
        
        if new_headers:
            logger.warning("\nFound different headers across files:")
            for file, headers in headers_by_file.items():
                diff = headers - base_headers
                if diff:
                    logger.warning(f"{file.name}: Additional headers: {diff}")
            
            response = input("\nWould you like to include these new columns? [y/N]: ").lower()
            if response != 'y':
                logger.info("Proceeding with only common headers")
                all_headers = base_headers
        
        # Read and concatenate all CSV files
        dfs = []
        for file in csv_files:
            try:
                df = read_csv_with_metadata(file)
                # Add missing columns with NaN values
                for col in all_headers:
                    if col not in df.columns:
                        df[col] = pd.NA
                dfs.append(df)
                logger.info(f"Successfully read: {file.name}")
            except Exception as e:
                logger.error(f"Error reading {file}: {str(e)}")
                continue
        
        if not dfs:
            logger.error("No valid CSV files could be read")
            return
        
        # Concatenate all dataframes
        final_df = pd.concat(dfs, ignore_index=True)
        
        # Ensure all columns from all_headers are present and in the same order
        final_df = final_df.reindex(columns=list(all_headers))
        
        # Generate output filename if not provided
        if output_filename is None:
            output_filename = generate_date_range_filename(dfs)
        elif not output_filename.endswith('.csv'):
            output_filename += '.csv'
        
        # Create full output path
        output_path = PROCESSED_DIR / output_filename
        
        # Save consolidated CSV
        final_df.to_csv(output_path, index=False)
        logger.info(f"\nSuccessfully consolidated {len(dfs)} CSV files into: {output_path}")
        logger.info(f"Total rows: {len(final_df)}")
        logger.info(f"Total columns: {len(final_df.columns)}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python csv_consolidator.py [output_filename]")
        print("Example: python csv_consolidator.py combined_output.csv")
        sys.exit(1)
    
    output_filename = sys.argv[1] if len(sys.argv) == 2 else None
    consolidate_csvs(output_filename)
