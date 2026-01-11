#!/bin/bash

# Excel to CSV Converter Script for macOS
# Usage: ./excel_to_csv.sh <input_directory> [output_directory]
# Modified to process all Excel files in a directory and extract cells A3:E from the first sheet

# Check if an input directory was provided
if [ $# -lt 1 ]; then
    echo "Error: Please provide an input directory containing Excel files"
    echo "Usage: $0 <input_directory> [output_directory]"
    exit 1
fi

# Get the input directory and check if it exists
INPUT_DIR="$1"
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Directory '$INPUT_DIR' not found"
    exit 1
fi

# Set output directory (use current directory if not specified)
OUTPUT_DIR="."
if [ $# -ge 2 ]; then
    OUTPUT_DIR="$2"
fi

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Count the number of Excel files
EXCEL_FILES=("$INPUT_DIR"/*.xlsx "$INPUT_DIR"/*.xls)
EXCEL_COUNT=0
for file in "${EXCEL_FILES[@]}"; do
    if [ -f "$file" ]; then
        EXCEL_COUNT=$((EXCEL_COUNT + 1))
    fi
done

if [ $EXCEL_COUNT -eq 0 ]; then
    echo "Error: No Excel files found in '$INPUT_DIR'"
    exit 1
fi

echo "Found $EXCEL_COUNT Excel files to process"

# Run Python script to convert Excel files to CSV
python3 -c "
import sys
import pandas as pd
import os
import glob

try:
    # Get directories
    input_dir = '$INPUT_DIR'
    output_dir = '$OUTPUT_DIR'
    
    # Find all Excel files in the input directory
    excel_files = glob.glob(os.path.join(input_dir, '*.xlsx'))
    excel_files.extend(glob.glob(os.path.join(input_dir, '*.xls')))
    
    if not excel_files:
        print('No Excel files found')
        sys.exit(1)
    
    files_processed = 0
    
    # Process each Excel file
    for excel_file in excel_files:
        try:
            # Get the base filename without extension
            basename = os.path.splitext(os.path.basename(excel_file))[0]
            
            # Read only the first sheet with specific range (A3:E to the bottom)
            xl = pd.ExcelFile(excel_file)
            first_sheet = xl.sheet_names[0]
            
            # Read the sheet, skipping the first 2 rows
            df = pd.read_excel(excel_file, sheet_name=first_sheet, skiprows=2)
            
            # Select only columns A-E (first 5 columns)
            if len(df.columns) >= 5:
                df = df.iloc[:, 0:5]
            else:
                print(f'Warning: Sheet in {basename} has fewer than 5 columns, using all available columns')
            
            # Create output filename
            output_file = os.path.join(output_dir, basename + '.csv')
            
            # Save as CSV
            df.to_csv(output_file, index=False)
            print(f'Created: {output_file}')
            files_processed += 1
            
        except Exception as e:
            print(f'Error processing {excel_file}: {str(e)}')
            continue
    
    print(f'Conversion completed! Successfully processed {files_processed} file(s)')
except Exception as e:
    print(f'Error: {str(e)}')
    sys.exit(1)
"

# Check if the conversion was successful
if [ $? -ne 0 ]; then
    echo "Conversion failed"
    exit 1
fi

echo "All Excel files processed successfully"
exit 0