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
SHEET_NAME="PC"

# Extract filename without extension for output
BASENAME=$(basename "$INPUT_FILE" .xlsx)
OUTPUT_FILE="$OUTPUT_FOLDER/wa_bonds_data.csv"

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
    data_df = pd.read_excel('$INPUT_FILE', sheet_name='$SHEET_NAME', skiprows=15, usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16, 17, 18, 19, 20, 23, 24])

    # Hardcode headers for now
    headers = [ 
        'postcode',
        'flats_units_1br_count',
        'flats_units_1br_median',
        'flats_units_2br_count',
        'flats_units_2br_median',
        'flats_units_3br_count',
        'flats_units_3br_median',
        'flats_units_4+br_count',
        'flats_units_4+br_median',
        'houses_1br_count',
        'houses_1br_median',
        'houses_2br_count',
        'houses_2br_median',
        'houses_3br_count',
        'houses_3br_median',
        'houses_4+br_count',
        'houses_4+br_median',
        'other_unknown_count',
        'other_unknown_median'
    ]

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