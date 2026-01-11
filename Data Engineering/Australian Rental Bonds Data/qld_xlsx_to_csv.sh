#!/bin/bash

# Excel to CSV Converter Script
# Converts the '2 pc-new-bonds' sheet from an Excel file to CSV

# Check if correct number of parameters provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <input_excel_file> <output_folder>"
    echo "Example: $0 /path/to/rtabondstatistics.xlsx /path/to/output"
    exit 1
fi

# Get parameters
INPUT_FILE="$1"
OUTPUT_FOLDER="$2"
SHEET_NAME="2 pc-new-bonds"

# Extract filename without extension for output
BASENAME=$(basename "$INPUT_FILE" .xlsx)
OUTPUT_FILE="$OUTPUT_FOLDER/2_pc-new-bonds.csv"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found!"
    exit 1
fi

# Check if output folder exists, create if it doesn't
if [ ! -d "$OUTPUT_FOLDER" ]; then
    echo "Creating output folder: $OUTPUT_FOLDER"
    mkdir -p "$OUTPUT_FOLDER"
    if [ $? -ne 0 ]; then
        echo "Error: Could not create output folder '$OUTPUT_FOLDER'"
        exit 1
    fi
fi

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "Converting '$INPUT_FILE' using Python pandas..."
    python3 -c "
import pandas as pd
import sys
import os

try:
    # 
    data_df = pd.read_excel('$INPUT_FILE', sheet_name='$SHEET_NAME', skiprows=8)
    data_df = data_df.iloc[:, 2:]  # Slice from column index 2 to end

    #
    header_df = pd.read_excel('$INPUT_FILE', sheet_name='$SHEET_NAME', header=None, skiprows=5, nrows=2)
    header_df = header_df.iloc[:, 4:]  # Slice from column index 2 to end
    quarter_row = header_df.iloc[0].str.split('.').str[0]
    year_row = header_df.iloc[1]
    date_headers = quarter_row.astype(str) + ' ' + year_row.astype(str)
    headers = ['Postcode', 'Dwelling'] + date_headers.to_list()
    
    # Save as CSV
    data_df.to_csv('$OUTPUT_FILE', header=headers, index=False)
    print('Successfully converted sheet \"$SHEET_NAME\" to $OUTPUT_FILE')
    print(f'Converted data shape: {data_df.shape[0]} rows × {data_df.shape[1]} columns')
    
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"

else
    echo "Error: Python not found!"
    echo "Please install Python and required packages:"
    echo "  pip install pandas openpyxl"
    echo ""
    echo "Installation commands:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-pandas python3-openpyxl"
    echo "  macOS: brew install python && pip3 install pandas openpyxl"
    exit 1
fi

# Check if output file was created
if [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "Conversion completed successfully!"
    echo "Output file: $OUTPUT_FILE"
    echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
    echo ""
    echo "First few lines of the CSV:"
    head -5 "$OUTPUT_FILE"
else
    echo "Warning: Output file '$OUTPUT_FILE' was not created."
    echo "Please check the error messages above."
fi