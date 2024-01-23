
# Jinja Invoice Generator

This is a simplified version of a data engineering project that I helped build and maintain at my work as a data engineer.

The actual project was a data platform solution delivered using Microsoft Azure using Azure resources including Azure Databricks, Azure Data Lake Storage Gen 2, Azure Data Factory and more to ingest source data, apply transformations and create and send out invoice to our client's customers.

This small project focuses on the how we leveraged the Jinja library in python to use CSV data to generate the invoices.

Essentially the workflow takes in 2 inputs: a word document template and CSVs containing invoice-related data. The Jinja templating engine takes these two as inputs and compiles them together. It outputs the template with data filled into the jinja placeholders.

To run the this demo project, you can simply download the folder and run in on your local device, ensuring you have the same of python (I used  v3.8.10) downloaded and the libraries imported at the top of the python (or jupyter notebook) file.

You can run either the python file or jupyter notebook - both should produce the sample invoices. Note that these are python implementations using pandas, but our production implementation at work was leveraging libraries such as pySpark to deal with the high volumne of data processed.









