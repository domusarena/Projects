
# Data Quality Checks using Pandas

This is a python script I created in my role as data specialist at Data Addiction for my client New South Wales Reconstruction Authority in 2023. Before loading data into a pipeline, it checks whether or not the new data satifies a few requirements by administering a few tests using the Pandas library.

The tests include:
- Null check: some pre-specified columns muct not contain null values
- Duplicate id check: the id column must not contain duplicate values
- Date value check: some pre-specified columns must contain a value date data type
- Dollar value check: some pre-specified columns must contain a numerical data type 

This python script was used as part of a bigger application using Azure Functions. However, this broader part of the project is hard to capture my personal Github repo. In a nutshell, if the new data passed these validation checks, it would be moved into an Azure Datalake Storage folder which would trigger it's load into the rest of the pipeline. If it failed, an error report text file would be generated and emailed to a stakeholder using Microsoft Power Automate.