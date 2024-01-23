import pandas as pd
from pandas.api.types import is_numeric_dtype
from datetime import datetime

def main():

    #Specify the path of the test data
    data_path = "test_data/test_data_nullcheck_fail.xlsx"

    # Define the name of the excel sheet to read data from
    sheet_name = 'data'

    # Read test Excel data into a DataFrame
    df = pd.read_excel(data_path, sheet_name=sheet_name, engine='openpyxl')
    print(df)

    # Input not null column list
    not_null_cols = [
        'project_id', 
        'project_name'
    ]

    # Input dollar columns list
    dollar_cols = [
        'project_cost'
    ]

    # Input date columns list
    date_cols = [
        'project_date'
    ]

    # Input validation check failure dictionary 
    data_validation_message_dict = {
        "Null Check" : "There are null values in one or more non-null columns.",
        "Duplicate ID Check" : "There are duplicate project_id's.",
        "Dollar Value Check" : "There are non-numerical values in one or more currency columns.",
        "Date Value Check" : "There are non-date values in one or more date."
    }

    passed, results = data_validation_checks(df, not_null_cols, dollar_cols, date_cols, data_validation_message_dict)

    # Turn validation results summary into array 
    error_report_list = []
    error_report_list.append("\n")
    for result in results:
        error_report_list.append(result + " : " + results[result]['Result'])
    
    error_report_list.append("\n")
    error_report_list.append("All Validations Passed?: " + str(passed))
    error_report_list.append("\n")

    for result in results:
        if 'Message' in results[result]:
            error_report_list.append(results[result]['Message'])
        if 'Failures' in results[result]:
            error_report_list.append("Failed columns: " + ' '.join(results[result]['Failures']))
        if 'Message' in results[result] or 'Failures' in results[result]:
            error_report_list.append("\n")

    for line in error_report_list:
        print(line)


## Returns: a boolean variable which is true if there are no null values and false otherwise,
# based on a input list of columns which cannot be null
def null_check(df, not_null_cols):
    passed = True
    failed_cols = []
    for col in not_null_cols:
        if df[col].isnull().values.any():
            passed = False
            failed_cols.append(col)
    return passed, failed_cols

# Returns: a boolean variable which is true if there is at least one duplicate id and false otherwise
def duplicate_id_check(df):
    duplicates = df['project_id'].duplicated()
    return not any(duplicates)

# Returns: a boolean value which is true if the row count of the before df (master list extraction before
# data update) is less than or equal to the updated df and false otherwise 

# Assumption: we have the row count of the before df - this needs to be saved in memory from a process before 
def missing_rows_check(df, row_count_before):
    row_count = len(df.index)
    if row_count >= row_count_before:
        return True 
    else:
        return False

# Returns: a boolean value which is true if all dollar column based on an input list are all numeric 
# and false otherwise
def dollar_value_check(df, dollar_cols):
    passed = True
    failed_cols = []
    for col in dollar_cols:
        if is_numeric_dtype(df[col]) == False:
            passed =  False
            failed_cols.append(col)
    return passed, failed_cols

# Returns: a boolean variable which is true if the value is null, of a datetime data type and a 
# date within the years of 2010 and 2035, and false otherwise.
def is_valid_date(date_value):

    # Check if the value is null
    if pd.isna(date_value):
        return True  # Null is considered valid
    
    # Check that the value is a datetime data type
    if not isinstance(date_value, datetime):
        return False
    
    # Check whether the 
    if date_value >= datetime.strptime("01/01/1900", '%d/%m/%Y') and date_value <= datetime.strptime("31/12/2035", '%d/%m/%Y'):
        return True
    else:
        return False
    
# Returns: a boolean value which is true if all the date columns based on an input list satify the
# requiremnents of the auxiliary function is_valid_date()
def date_value_check(df, date_cols):
    passed = True
    failed_cols = []
    for col in date_cols:
        if all(df[col].apply(is_valid_date)) == False:
            passed = False
            failed_cols.append(col)
    return passed, failed_cols

# Returns: validation check summary data 
def data_validation_checks(df, not_null_cols, dollar_cols, date_cols, data_validation_message_dict):

    validation_results = {}
    passed = True
    
    # For each test, create a new dictionary 
    validation_results['Null Check'] = {}
    null_check_result, null_check_failures = null_check(df, not_null_cols = not_null_cols)
    if null_check_result:
        # If the check passed, record it's result as "Passed"
        validation_results['Null Check']['Result'] = "Passed"
    else:
        # If the check failed, record it's result as "Failed"
        validation_results['Null Check']['Result'] = "Failed"
        # If the check fails, record it's failure message in the results from the message dictionary
        validation_results['Null Check']['Message'] = data_validation_message_dict['Null Check']
        
        validation_results['Null Check']['Failures'] = null_check_failures
        passed = False

    validation_results['Duplicate ID Check'] = {}
    if duplicate_id_check(df):
        validation_results['Duplicate ID Check']['Result'] = "Passed"
    else:
        validation_results['Duplicate ID Check']['Result'] = "Failed"
        validation_results['Duplicate ID Check']['Message'] = data_validation_message_dict['Duplicate ID Check']
        passed = False

    validation_results['Dollar Value Check'] = {}
    dollar_value_check_result, dollar_value_check_failures = dollar_value_check(df, dollar_cols = dollar_cols)
    if dollar_value_check_result:
        validation_results['Dollar Value Check']['Result'] = "Passed"
    else:
        validation_results['Dollar Value Check']['Result'] = "Failed"
        validation_results['Dollar Value Check']['Message'] = data_validation_message_dict['Dollar Value Check']
        validation_results['Dollar Value Check']['Failures'] = dollar_value_check_failures
        passed = False

    validation_results['Date Value Check'] = {}
    date_value_check_result, date_value_check_failures = date_value_check(df, date_cols = date_cols)
    if date_value_check_result:
        validation_results['Date Value Check']['Result'] = "Passed"
    else:
        validation_results['Date Value Check']['Result'] = "Failed"
        validation_results['Date Value Check']['Message'] = data_validation_message_dict['Date Value Check']
        validation_results['Date Value Check']['Failures'] = date_value_check_failures
        passed = False
 
    return passed, validation_results

if __name__ == '__main__':
    main()