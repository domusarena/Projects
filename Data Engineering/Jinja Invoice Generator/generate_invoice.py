### 1.Imports ###

from docxtpl import DocxTemplate
import jinja2
import pandas as pd

from io import BytesIO

### 2.Declare variables ###

# Declare variables which would be taken from widgets in Azure Databricks Notebooks
current_timestamp = "20230125T000000"
month_variant = "202301"

# Get latest version of template stored in business container
template_name = "jinja_template_1.0.docx"

# Get latest version of csvs generated in business container
csvs = [f"jinja_csv_1_{current_timestamp}.csv", f"jinja_csv_2_{current_timestamp}.csv"]

# Save directories for csvs, template and invoice folders
root_directory = "Brownbags/Jinja/Python/" # Change this as required

directory_csvs = root_directory + "csv/" + month_variant + "/"
directory_template = root_directory + "template/"
directory_invoice = root_directory + "invoice/" + month_variant + "/"

### 3.Custom Jinja2 filters ###

# Checks for null value and rounds to 2 d.p.
def round_null_check(value):
    try:
        value = float(value)
        if value == 0:
          value = abs(value)
        return "{:,.2f}".format(value)
    except:
        return "0.00"

# Checks for null value and rounds to 0 d.p.
def round0_null_check(value):
    try:
        value = float(value)
        if value == 0:
          value = abs(value)
        return "{:,.0f}".format(value)
    except:
        return "0"

### 4.Set up Jinja environment ###

jinja_env = jinja2.Environment()
jinja_env.filters['round_null_check'] = round_null_check
jinja_env.filters['round0_null_check'] = round0_null_check

### 5.Helper Functions ###

# Reads data from CSVs into pandas df
def read_data(file_name):
    df = pd.read_csv(directory_csvs + file_name)

    for col in df.columns:
        df[col] = df[col].apply(str)
    
    return df

# Reads template word doc into bytes stream
def read_template(file_name):
    template_stream = open(directory_template + file_name, 'rb')
    template_stream.seek(0)
    return template_stream

# Creates JSON structure for data in CSV 1
def update_contexts_from_csv_1(invoice_contexts, df, month_variant):
    for i in range(df.shape[0]):
        row = df.loc[i]
        account_number = row['account_number']
        if row['month'] == month_variant:
            if account_number not in invoice_contexts:
                context = {}
                key = row['key']
                value = row['value']
                context[key] = value
                invoice_contexts[account_number] = context
            else:
                context = invoice_contexts[account_number]
                key = row['key']
                value = row['value']
                context[key] = value
                invoice_contexts[account_number] = context

# Adds to JSON structure data in CSV 2
def update_contexts_from_csv_2(invoice_contexts, df, month_variant):
    for i in range(df.shape[0]):
        row = df.loc[i]
        account_number = row['account_number']
        if row['month'] == month_variant:
            if account_number not in invoice_contexts:
                context = {}
                new_charge_rows = []
                new_charge = {}
                new_charge['charge_type'] = row['charge_type']
                new_charge['amount_payable_ex_gst'] = row['amount_payable_ex_gst']
                new_charge['amount_payable_gst'] = row['amount_payable_gst']
                new_charge['amount_payable_inc_gst'] = row['amount_payable_inc_gst']
                new_charge_rows.append(new_charge)
                context['new_charge_rows'] = new_charge_rows
                invoice_contexts[account_number] = context
            else:
                context = invoice_contexts[account_number]
                if 'new_charge_rows' not in context:
                    new_charge_rows = []
                    new_charge = {}
                    new_charge['charge_type'] = row['charge_type']
                    new_charge['amount_payable_ex_gst'] = row['amount_payable_ex_gst']
                    new_charge['amount_payable_gst'] = row['amount_payable_gst']
                    new_charge['amount_payable_inc_gst'] = row['amount_payable_inc_gst']
                    new_charge_rows.append(new_charge)
                    context['new_charge_rows'] = new_charge_rows
                    invoice_contexts[account_number] = context
                else:
                    new_charge_rows = context['new_charge_rows']
                    new_charge = {}
                    new_charge['charge_type'] = row['charge_type']
                    new_charge['amount_payable_ex_gst'] = row['amount_payable_ex_gst']
                    new_charge['amount_payable_gst'] = row['amount_payable_gst']
                    new_charge['amount_payable_inc_gst'] = row['amount_payable_inc_gst']
                    new_charge_rows.append(new_charge)
                    context['new_charge_rows'] = new_charge_rows
                    invoice_contexts[account_number] = context

# Creates invoice contexts JSON structure from CSV data
def contexts_from_df(invoice_contexts, csv_name, month_variant):
    df = read_data(csv_name)
    if csv_name == f"jinja_csv_1_{current_timestamp}.csv":
        update_contexts_from_csv_1(invoice_contexts, df, month_variant)
    if csv_name == f"jinja_csv_2_{current_timestamp}.csv":
        update_contexts_from_csv_2(invoice_contexts, df, month_variant)

# Combines template stream and invoice contexts to create invoices
def generate_invoices(invoice_contexts, month_variant, jinja_env, template):
    for account_number in invoice_contexts:
      
        # Get that customer's context
        context = invoice_contexts[account_number]
        
        # Render template with given customer context
        doc = DocxTemplate(template)
        doc.render(context, jinja_env)
        invoice_name = f"{account_number} - Invoice - {month_variant} - {current_timestamp}.docx"
        doc.save(directory_invoice + "/" + invoice_name)
         
### 6.Main ###

# Create empty master dict to store each invoice context with customer as key, context as value
template = read_template(template_name)

invoice_contexts = {}
for csv_name in csvs:
  print(csv_name)
  # Update invoice_contexts dict
  contexts_from_df(invoice_contexts, csv_name, month_variant)
  
print("Success creating contexts from csv files")
print(invoice_contexts)

# Print context for each customer
for account_number in invoice_contexts:
    print(account_number)
    print(invoice_contexts[account_number])

generate_invoices(invoice_contexts, month_variant, jinja_env, template) 

print(f"Success generating invoices for month {month_variant}")   