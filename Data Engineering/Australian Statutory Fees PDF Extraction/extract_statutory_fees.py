import os
import glob
import pdfplumber
import pandas as pd
import argparse
import csv

def list_files_os(directory_path):
    """
    Lists all files in a given directory using the os module.
    """
    files = []
    for entry in os.listdir(directory_path):
        full_path = os.path.join(directory_path, entry)
        if os.path.isfile(full_path):
            files.append(entry)
    return files


def extract_tables_from_pdf(pdf_path, pages:dict):
    """
    Extract all tables from a PDF using pdfplumber (no cleaning).
    """
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            if page_num in pages[os.path.basename(pdf_path)]:
                for table_idx, table in enumerate(page.extract_tables() or []):
                    if not table:
                        continue
                    df = pd.DataFrame(table)
                    df.insert(0, "source_pdf", os.path.basename(pdf_path))
                    df.insert(1, "page", page_num)
                    df.insert(2, "table_index", table_idx)
                    tables.append(df)
    return tables


def clean_tables(df):
    """
    Load and clean a CSV file containing statutory fees data.
    
    Args:
        df (pd.DataFrame): DataFrame containing extracted table data
        
    Returns:
        pd.DataFrame: Cleaned DataFrame with proper headers and filtered rows
    """
    
    # Step 1: Remove all null columns beyond the first 3 columns
    cols_to_check = df.columns[3:]  # All columns after source_pdf, page, table_index
    non_null_cols = []
    
    for col in cols_to_check:
        if not df[col].isna().all():  # Keep column if it has at least one non-null value
            non_null_cols.append(col)
    
    # Keep first 3 columns + non-null columns
    df_cleaned = df[list(df.columns[:3]) + non_null_cols].copy()
    
    if df_cleaned.empty or len(df_cleaned.columns) < 4:
        return pd.DataFrame()
    
    # Step 2: Analyze header patterns to understand column structure
    header_indicators = {}
    potential_fee_cols = []
    potential_gst_cols = []
    potential_unit_cols = []
    
    # Look at first few rows to identify column types
    for col_idx in range(3, len(df_cleaned.columns)):
        col_values = []
        for row_idx in range(min(5, len(df_cleaned))):
            val = str(df_cleaned.iloc[row_idx, col_idx]).strip() if pd.notna(df_cleaned.iloc[row_idx, col_idx]) else ''
            if val:
                col_values.append(val.lower())
        
        # Check for year/fee indicators
        if any('24' in val or '2024' in val for val in col_values):
            header_indicators[col_idx] = 'fee_24_25'
        elif any('25' in val or '2025' in val for val in col_values):
            header_indicators[col_idx] = 'fee_25_26'
        elif any('gst' in val for val in col_values):
            header_indicators[col_idx] = 'gst'
        elif any('unit' in val or 'per' in val for val in col_values):
            header_indicators[col_idx] = 'unit'
        
        # Look for dollar signs in data rows to identify fee columns
        dollar_count = sum(1 for row_idx in range(min(10, len(df_cleaned)))
                          if str(df_cleaned.iloc[row_idx, col_idx]).strip().startswith('$'))
        if dollar_count > 0:
            potential_fee_cols.append(col_idx)
        
        # Look for Y/N patterns to identify GST columns
        yn_count = sum(1 for row_idx in range(min(10, len(df_cleaned)))
                      if str(df_cleaned.iloc[row_idx, col_idx]).strip() in ['Y', 'N', 'Yes', 'No'])
        if yn_count > 0:
            potential_gst_cols.append(col_idx)
        
        # Look for unit patterns
        unit_count = sum(1 for row_idx in range(min(10, len(df_cleaned)))
                        if any(keyword in str(df_cleaned.iloc[row_idx, col_idx]).lower() 
                              for keyword in ['per', 'each', 'hour', 'day', 'inspection', 'application', 'lift', 'bin', 'service']))
        if unit_count > 0:
            potential_unit_cols.append(col_idx)
    
    # Step 3: Process rows using iterrows()
    cleaned_rows = []
    current_header = None
    
    for idx, row in df_cleaned.iterrows():
        # Get the raw data columns (after source_pdf, page, table_index)
        raw_data = row.iloc[3:].values if len(row) > 3 else []
        
        # Check if all values are empty/null
        all_empty = all(pd.isna(val) or str(val).strip() == '' for val in raw_data)
        if all_empty:
            continue
        
        # Extract fee name (usually first non-empty data column)
        fee_name = None
        for i in range(3, len(row)):
            val = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
            if val and not val.startswith('$') and val not in ['Y', 'N', 'Yes', 'No']:
                # Check if it looks like a fee name (not just numbers)
                if not val.replace('.', '').replace(',', '').replace('$', '').replace('%', '').isdigit():
                    fee_name = val
                    break
        
        if not fee_name:
            continue
            
        # Skip rows that appear to be table headers
        skip_indicators = ['name', 'fee', '(incl. gst)', 'year 24/25', 'year 25/26', 'gst', 'increase', 'pricing policy']
        if fee_name.lower() in skip_indicators or any(indicator in fee_name.lower() for indicator in skip_indicators):
            continue
        
        # Extract fee amounts based on identified patterns
        fee_24_25 = None
        fee_25_26 = None
        gst = None
        unit = None
        
        # Use header indicators if available
        for col_idx, col_type in header_indicators.items():
            if col_idx < len(row):
                val = row.iloc[col_idx] if pd.notna(row.iloc[col_idx]) else None
                if col_type == 'fee_24_25':
                    fee_24_25 = val
                elif col_type == 'fee_25_26':
                    fee_25_26 = val
                elif col_type == 'gst':
                    gst = val
                elif col_type == 'unit':
                    unit = val
        
        # If no header indicators, use pattern matching
        if not any([fee_24_25, fee_25_26]):
            # Look for dollar amounts in potential fee columns
            dollar_values = []
            for col_idx in potential_fee_cols:
                if col_idx < len(row):
                    val = str(row.iloc[col_idx]).strip() if pd.notna(row.iloc[col_idx]) else ''
                    if val.startswith('$'):
                        dollar_values.append((col_idx, val))
            
            # Assign first two dollar values as fees (24/25, 25/26)
            if len(dollar_values) >= 2:
                fee_24_25 = dollar_values[0][1]
                fee_25_26 = dollar_values[1][1]
            elif len(dollar_values) == 1:
                fee_25_26 = dollar_values[0][1]  # Assume single fee is for 25/26
        
        # Look for GST value if not found
        if gst is None and potential_gst_cols:
            for col_idx in potential_gst_cols:
                if col_idx < len(row):
                    val = str(row.iloc[col_idx]).strip() if pd.notna(row.iloc[col_idx]) else ''
                    if val in ['Y', 'N', 'Yes', 'No']:
                        gst = val
                        break
        
        # Look for unit value if not found
        if unit is None and potential_unit_cols:
            for col_idx in potential_unit_cols:
                if col_idx < len(row):
                    val = str(row.iloc[col_idx]).strip() if pd.notna(row.iloc[col_idx]) else ''
                    if any(keyword in val.lower() for keyword in ['per', 'each', 'hour', 'day', 'inspection', 'application', 'lift', 'bin', 'service']):
                        unit = val
                        break
        
        # Check if this is a section header (has name but no fee data)
        has_fee_data = (fee_24_25 is not None and str(fee_24_25).strip() != '') or \
                       (fee_25_26 is not None and str(fee_25_26).strip() != '')
        
        if fee_name and not has_fee_data:
            # This is a section header row
            current_header = fee_name
            continue
        
        # Only keep rows that have both a fee name and some fee data
        if fee_name and has_fee_data:
            new_row_dict = {
                'source_pdf': row.iloc[0],
                'page': row.iloc[1],
                'table_index': row.iloc[2],
                'fee_name': fee_name,
                'fee_24_25': fee_24_25,
                'fee_25_26': fee_25_26,
                'gst_25_26': gst,
                'unit_25_26': unit
            }
            cleaned_rows.append(new_row_dict)
    
    # Create new DataFrame from cleaned rows
    if not cleaned_rows:
        return pd.DataFrame()
        
    df_result = pd.DataFrame(cleaned_rows)
    
    # Ensure we have the required columns in the right order
    required_columns = ['source_pdf', 'page', 'table_index', 'fee_name', 'fee_24_25', 'fee_25_26', 'gst_25_26', 'unit_25_26']
    
    # Add any missing columns
    for col in required_columns:
        if col not in df_result.columns:
            df_result[col] = None
    
    # Select only the required columns in the specified order
    df_final = df_result[required_columns]
    
    return df_final


def squash_csv_rows(input_files, output_files):
    """
    Squash CSV rows by shifting all non-null values to the left,
    removing gaps from null/empty cells.
    """
    for input_file, output_file in zip(input_files, output_files):
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            
            squashed_rows = []
            for row in reader:
                # Filter out empty/null values and shift left
                squashed_row = [cell for cell in row if cell.strip()]
                squashed_rows.append(squashed_row)
            
            # Find the maximum row length after squashing
            max_length = max(len(row) for row in squashed_rows) if squashed_rows else 0
            
            # Pad rows to ensure consistent column count
            for row in squashed_rows:
                while len(row) < max_length:
                    row.append('')
        
        # Write the squashed data
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(squashed_rows)

def squash_dataframe_rows(df):
    """
    Squash DataFrame rows by shifting all non-null values to the left,
    removing gaps from null/empty cells.
    
    Args:
        df (pd.DataFrame): Input DataFrame to squash
        
    Returns:
        pd.DataFrame: DataFrame with squashed rows (all non-null values shifted left)
    """
    squashed_data = []
    
    for _, row in df.iterrows():
        # Convert row to list and filter out null/empty values
        row_values = row.tolist()
        squashed_row = [str(cell).strip() for cell in row_values if pd.notna(cell) and str(cell).strip()]
        squashed_data.append(squashed_row)
    
    if not squashed_data:
        return pd.DataFrame()
    
    # Find the maximum row length after squashing
    max_length = max(len(row) for row in squashed_data) if squashed_data else 0
    
    # Pad rows to ensure consistent column count
    for row in squashed_data:
        while len(row) < max_length:
            row.append('')
    
    # Create new DataFrame with squashed data
    # Generate column names based on max_length
    column_names = [f'col_{i}' for i in range(max_length)]
    squashed_df = pd.DataFrame(squashed_data, columns=column_names)
    
    return squashed_df
    
       
def main():

    # Define all state page dictionaries
    state_configs = {
        'NSW': {
            'pages_dict': {
                "Bayside NSW - Fees & Charges 2025-26.pdf": [26, 92, 92, 94],
                "Blacktown NSW - GSPS-202526-revised-12Aug2025.pdf": [59, 60, 61, 66, 112, 129, 130, 131],
                "Burwood NSW - Fees-and-Charges-2025-2026.pdf": [17, 63, 75],
                "Camden NSW - Adopted-2025-26-Fees-and-Charges-Schedule-FINAL-v2.pdf": [34, 35, 41, 42, 43],
                "Campbelltown NSW - fees-and-charges-2025-26.pdf": [6, 9, 10, 38, 74],
                "Canada Bay NSW - ECM_8627404_v2_Fees_And_Charges_2025-2026.pdf": [18, 25, 61, 78, 79, 80],
                "Canterbury Bankstown NSW - Fees_and_Charges_2025-26_pdf.pdf": [60, 61, 62, 63, 69],
                "Cumberland NSW - fees-charges-2025-2026.pdf": [20, 29, 30, 64, 78, 80, 81, 82],
                "Fairfield NSW - 2024-2025-pricing-policy-fees-and-charges-1-august-2024.pdf": [59, 60, 61, 62, 63, 89, 129],
                "Georges River NSW - Fees-and-Charges-Report-for-2025-2026.pdf": [30, 32, 33, 34, 62, 63],
                "Hawesbury NSW - HCC-Operational-Plan-2025-2026.pdf": [93, 113, 115, 117, 118, 119, 120],
                "Hornsby NSW - 2526-Fees-and-Charges-Adopted-Cover.pdf": [31, 48, 77, 78, 79, 80],
                "Hunters Hill NSW - feesandchargesfy2025.26.pdf": [48, 49, 50],
                "Inner West NSW - Fees and Charges 2025-26.pdf": [48, 49, 50, 69],
                "Ku-ring-gai NSW - adopted-2025-2026-public-fees-charges.pdf": [19, 31, 32, 33, 67],
                "Lane Cove NSW - TRIM_Draft Delivery Program   Operational Plan - April 2025 - V2_1888554.pdf": [196, 200, 206, 207],
                "Liverpool NSW - Revenue-Pricing-Policy,-Fees-and-Charges-FY-2025-2026.pdf": [73, 76, 77, 78, 101],
                "Mosman NSW - 250105.003.mosplan.feescharges.01_adpt_lr.pdf": [29, 33, 34, 45, 48],
                "North Sydney NSW - 3648e7fa36da85edad58e4a5227ad759Draft-Fees-and-Charges-Schedule-2025-26_1749605838.pdf": [69, 70, 100],
                "Northern Beaches NSW - Fees_Booklet_for_Council_ReportOPT.pdf": [42, 58, 59, 74, 75, 76],
                "Parramatta NSW - 2025-2026-fees-and-charges.pdf": [60, 77, 90, 91, 92, 174, 175, 176],
                "Penrith NSW - 2025-2026 Fees and Charges - Penrith City Council.pdf": [32, 33, 38, 67, 68, 69, 70, 71, 72],
                "Randwick NSW - General-Fees-and-Charges-2025-26.pdf": [34, 52, 53, 57, 63],
                "Ryde NSW - 2025-2026-fees-and-charges.pdf": [61, 62, 63, 64, 65, 66, 106],
                "Strathfield NSW - 2025-26-fees-and-charges_adopted_final-v3.pdf": [18, 49, 54, 55],
                "Sutherland NSW - 55faac5ab7b8ab0e980b50001cfaeba0_2. 2025 2026 Fees and Charges - Draft.pdf": [51, 69, 70, 71],
                "Sydney NSW - Statement of revenue policy - fees and charges - adopted 23 June 2025.pdf": [27, 42, 50, 72, 73, 74],
                "The Hills NSW - 3b03e2dbf7ae4b50fd3a30da7eb098df_Part 5 - Hills Shire Plan Draft Fees  Charges 2025-2026.pdf": [6, 42, 43, 44, 56, 65],
                "Waverly NSW - Pricing_Policy_Fees_and_Charges.pdf": [14, 15, 35, 62],
                "Willoughby NSW - ECM_7222796_v1_2025-2026-Adopted-Fees-And-Charges.pdf": [29, 30, 53, 54],
                "Wollondilly NSW - 12.-Fees_And_Charges_Report-2025_2026.pdf": [30, 44, 45, 46],
                "Woollahra NSW - 25-26-fees-and-charges.pdf": [47, 56, 57]
            },
            'input_folder': 'Documents/NSW',
            'csv_dir': 'Data/Individual/NSW',
            'combined_out': 'Data/Combined/nsw_data.csv'
        },
        'VIC': {
            'pages_dict': {
                "Banyule VIC - Budget-2025-2029.pdf": [124, 125, 126, 127, 128, 144, 159],
                "Bayside VIC - item_10.2_-_attachment_1_-_2025-26_draft_annual_budget_with_fees_and_charges.pdf": [89,96, 103, 106],
                "Brimbank VIC - Annual Action Plan and Budget 2025-2026.PDF": [64, 71, 72, 74, 77],
                "Darebin VIC - darebin-city-council-–-statutory-planning-fee-schedule-fy25-26.pdf":[],
                "Glen Eira VIC - user-fees-and-charges-2025-2026.pdf":[],
                "Hobsons Bay VIC - Annual-Budget-2025-26.pdf":[99, 107, 108, 109, 110],
                "Manningham - 2025-26 Budget - 30 June 2025 - Final.pdf":[85, 91, 92, 93],
                "Maribyrnong VIC - CC-Statutory-Permit-Application-Fee-Schedule-2025-26.pdf":[],
                "Maribyrnong VIC -City-Council-Building-Fees-Fee-Schedule-2025-26.pdf":[],
                "Melton VIC -Council-2025-2026-Fees-and-Charges_v1.doc.pdf":[],
                "Meri-bek VIC - fees-and-charges-2025-29.pdf":[30, 31, 38, 46],
                "Monash VIC - 2025-26-annual-budget.pdf":[117, 126, 127, 128, 129, 130, 131, 132],
                "Moonee Valley VIC - Adopted-Budget-2025-26-2.pdf":[116, 117, 118, 199, 120, 121],
                "Stonnington VIC - Appendix_B-Budget_2025-26_-Schedule_of_Fees_and_Charges_June_2025.pdf":[],
                "Whitehorse VIC - Planning Fees - 1 July 2025.pdf":[],
                "Wyndham VIC - Attachment B Fees & Charges 2025-26 Adopted Budgetv2_0.pdf":[1, 2, 4, 18, 28],
                "Yarra City VIC - yarra_city_council_annual_budget_2025-26.pdf":[84, 112],
                "Yarra Ranges VIC - Fees-and-Charges-2025-2026.pdf":[15, 24, 25, 26, 33, 34]
            },
            'input_folder': 'Documents/VIC',
            'csv_dir': 'Data/Individual/VIC',
            'combined_out': 'Data/Combined/vic_data.csv'
        },
        'QLD': {
            'pages_dict': {
                "Brisbane QLD - Schedule of Fees and Charges 2025-26.pdf.coredownload.pdf":[23, 24, 25, 37, 38, 39, 42, 43, 44, 45, 55],
                "Ipswich QLD - 2025-2026-fees-and-charges-report-v3-20250929.pdf":[41, 42, 43, 44, 71, 72, 73, 74, 75],
                "Logan City QLD - register-of-cost-recovery-fees-and-charges-2025-to-2026.pdf":[44, 49, 55, 56, 57, 58, 59, 60],
                "Moreton Bay QLD - adopted-fees-and-charges-schedule-2025-2026.pdf":[9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 135, 136, 160, 161, 162, 163, 164],
                "Redland QLD - register-of-fees.pdf":[3, 17, 27, 28, 29]
            },
            'input_folder': 'Documents/QLD',
            'csv_dir': 'Data/Individual/QLD',
            'combined_out': 'Data/Combined/qld_data.csv'
        },
        'WA': {
            'pages_dict': {
                "Bassendean WA - Fees-and-Charges-2025-26.pdf": [15, 16, 18, 21],
                "Bayswater WA - eab44378-ee97-4b57-80e6-cc6577f5e39b.pdf": [30],
                "Belmont WA - Fees and Charges 2025-26.pdf": [18, 19],
                "Cambridge WA - Fees-and-Charges-2025-2026-Amended.pdf": [25],
                "Claremont WA - toc_schedule-of-fees-and-charges.pdf": [8],
                "Cockburn WA - ECM_12373647_v2_Fees-and-Charges-2025-2026.pdf": [7, 28, 29, 30, 31, 32],
                "Cottlesloe WA - approved_2025-2026_fees_and_charges_schedule.pdf": [7, 8, 9],
                "Fremantle WA - Updated-Fees_And_Charges_Report-2025-26-V2.pdf": [81, 91, 92, 93, 94],
                "Mosman Park WA - Adopted-Fees-Charges-2025_26.pdf": [4, 8, 9],
                "Nedlands WA - 2025-26-Schedule-of-Fees-and-Charges.pdf": [10, 11, 13, 14],
                "Peppermint Grove WA - Fees-and-Charges-202526.pdf": [3],
                "Perth WA - Fees and Charges 2025-2026 Schedule Final.pdf": [12, 16, 17],
                "South Perth WA - 2025_2026_fees-and-charges.pdf": [26, 29, 31, 32, 63],
                "Stirling WA - 2025-26-Statutory-Budget_FINAL_inc-fees-and-charges_11082025.pdf": [38, 43, 45, 46, 47],
                "Subiaco WA - Fees-and-charges-2025-26_6.pdf": [1, 4],
                "Victoria Park WA - 14.4.4_Schedule_of_Fees_and_Charges_for_2025_26.pdf": [29, 30, 31, 32, 34, 35],
                "Vincent WA - Fees-and-Charges-2025-2026.pdf": [8, 9, 10, 13]
            },
            'input_folder': 'Documents/WA',
            'csv_dir': 'Data/Individual/WA',
            'combined_out': 'Data/Combined/wa_data.csv'
        },
        'SA': {
            'pages_dict': {
                "Adelaide Hills SA - AHC-Fees-and-Charges-2025-26-September.pdf": [2, 3, 9],
                "Adelaide SA - fees-charges.pdf": [4, 5, 8, 9, 11],
                "Barossa SA - Fees-Charges-Register-2025-2026-Council-adopted.pdf": [4, 7, 9],
                "Charles Sturt SA - Fees-and-Charges-Register-2025-26.pdf": [34, 61, 62, 63, 63, 65, 66],
                "Marion SA - Fees-and-Charges-Schedule-2025-26.pdf": [11, 22],
                "Murray Bridge SA - Draft-Fees-and-Charges-Schedule_1747200979.pdf": [2, 3],
                "Onkaparinga SA - Schedule-of-Fees-and-Charges.pdf": [36, 37, 38, 39, 40, 64, 87, 122, 123, 124]
            },
            'input_folder': 'Documents/SA',
            'csv_dir': 'Data/Individual/SA',
            'combined_out': 'Data/Combined/sa_data.csv'
        },
        'TAS': {
            'pages_dict': {
                "Clarence Valley TAS - 2025-26-Fees-Charges.pdf": [12, 13, 14, 18, 37, 45],
                "Glenorchy City TAS - Schedule-of-Fees-Charges-2025-26-PUBLIC.pdf": [3, 4, 5, 8, 9, 10],
                "Hobart TAS - city-of-hobart-fees-and-charges-2025-26-updated-16-july-2025.pdf": [27, 28, 29, 67, 68, 69, 70],
                "Kingsborough TAS - KC-Fees-Charges-2025-26.pdf": [6, 7, 8, 9, 11, 12, 13, 14]
            },
            'input_folder': 'Documents/TAS',
            'csv_dir': 'Data/Individual/TAS',
            'combined_out': 'Data/Combined/tas_data.csv'
        }
    }

    # Process each state
    for state_code, config in state_configs.items():
        print(f"\n{'='*60}")
        print(f"Processing {state_code} councils...")
        print(f"{'='*60}")
        
        input_folder = config['input_folder']
        csv_dir = config['csv_dir']
        combined_out = config['combined_out']
        pages_dict = config['pages_dict']

        # Check if input folder exists
        if not os.path.exists(input_folder):
            print(f"  ⚠️ Input folder {input_folder} not found. Skipping {state_code}.")
            continue

        # Get all pdf file names with full paths
        pdf_files = []
        try:
            for filename in os.listdir(input_folder):
                if filename.lower().endswith('.pdf'):
                    full_path = os.path.join(input_folder, filename)
                    pdf_files.append(full_path)
        except Exception as e:
            print(f"  ⚠️ Error reading {input_folder}: {e}")
            continue

        if not pdf_files:
            print(f"  ⚠️ No PDF files found in {input_folder}. Skipping {state_code}.")
            continue
            
        print(f"Found {len(pdf_files)} PDF files in {state_code}")

        os.makedirs(csv_dir or ".", exist_ok=True)
        os.makedirs(os.path.dirname(combined_out) or ".", exist_ok=True)
        
        cleaned_tables = []
        # Generate CSVs from pdfs for each council
        for pdf_path in pdf_files:
            pdf_name = os.path.basename(pdf_path)
            if pdf_name not in pages_dict:
                print(f"  ⚠️ {pdf_name} not configured in pages_dict. Skipping.")
                continue
                
            if not pages_dict[pdf_name]:  # Empty page list
                print(f"  ⚠️ {pdf_name} has empty page configuration. Skipping.")
                continue
                
            print(f"Extracting tables from {pdf_path}...")

            try:
                tables = extract_tables_from_pdf(pdf_path, pages=pages_dict)

                if not tables:
                    print("  ⚠️ No tables found.")
                    continue
                    
                pdf_cleaned_tables = []
                for table in tables:
                    try:
                        cleaned_df = clean_tables(table)
                        if not cleaned_df.empty:
                            pdf_cleaned_tables.append(cleaned_df)
                            cleaned_tables.append(cleaned_df)
                        print(f"  ✅ Cleaned table from {os.path.basename(pdf_path)}")
                    except Exception as e:
                        print(f"  ⚠️ Error cleaning table from {os.path.basename(pdf_path)}: {e}")
                        continue

                # Save the cleaned tables for this PDF
                if pdf_cleaned_tables:
                    pdf_out = os.path.join(
                        csv_dir or ".",
                        f"{os.path.splitext(os.path.basename(pdf_path))[0]}.csv",
                    )
                    combined_pdf_df = pd.concat(pdf_cleaned_tables, ignore_index=True)
                    combined_pdf_df.to_csv(pdf_out, index=False)
                    print(f"  ✅ Saved {pdf_out}")
            except Exception as e:
                print(f"  ⚠️ Error processing {pdf_name}: {e}")
                continue

        # Create combined CSV for this state
        combined = []
        if os.path.exists(csv_dir):
            print(f"Reading CSV files from {csv_dir}...")
            try:
                for filename in os.listdir(csv_dir):
                    if filename.lower().endswith('.csv'):
                        csv_path = os.path.join(csv_dir, filename)
                        print(f"Reading {csv_path}...")
                        try:
                            df = pd.read_csv(csv_path)
                            # Only include files that have the new schema (contain proper column names)
                            expected_columns = ['source_pdf', 'page', 'table_index', 'fee_name', 'fee_24_25', 'fee_25_26', 'gst_25_26', 'unit_25_26']
                            if all(col in df.columns for col in expected_columns):
                                combined.append(df)
                                print(f"  ✅ Added {filename} to combined dataset ({len(df)} rows)")
                            else:
                                print(f"  ⚠️ Skipped {filename} - does not have expected schema")
                        except Exception as e:
                            print(f"  ⚠️ Error reading {filename}: {e}")
                            continue
            except Exception as e:
                print(f"  ⚠️ Error reading CSV directory {csv_dir}: {e}")
        
        # Concatenate all dataframes into one combined state df
        if combined:
            combined_df = pd.concat(combined, ignore_index=True)
            print(f"Combined DataFrame shape: {combined_df.shape}")
            
            # For the new schema, we don't need to squash rows since they're already properly structured
            if not combined_df.empty and 'source_pdf' in combined_df.columns:
                print(f"Using proper schema - no squashing needed")
                
                # Drop all null columns
                combined_df.dropna(axis=1, how='all', inplace=True)

                # Save the combined DataFrame
                combined_df.to_csv(combined_out, index=False)
                print(f"  ✅ Saved combined data to {combined_out}")
            else:
                print(f"  ⚠️ No valid data found for {state_code}")
        else:
            print(f"No CSV files found or loaded successfully for {state_code}.")

    print(f"\n{'='*60}")
    print("All states processing completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
