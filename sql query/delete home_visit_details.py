# delete home_visit_details

import pandas as pd
import openpyxl
# Read the Excel file
excel_file = 'Book1.xlsx'  # Replace with your file name
sheet_name = 'Sheet1'  # Replace with your sheet name if necessary

# Load the sheet into a DataFrame
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Extract column A into a list
column_a_values = df.iloc[:, 0].tolist()
column_b_values = df.iloc[:, 1].tolist()

# Remove quotes from each item in the list
# column_a_values_cleaned = [str(item) for item in column_a_values]

sql_command = []
for a, b in zip(column_a_values, column_b_values):
    sql_command.append(f"DELETE from home_visit_details WHERE home_visit_id={a} and participant_id='{b}';")

# print(sql_command)

for query in sql_command:
    print(query)

print(len(sql_command))

# home_visit_details
# "home_visit_id" = e009f3a0-7655-44c8-b1cc-a8235eda00d4
# "participant_id" = '7c0669dc-09d9-4362-8e7a-8b277c6ccc16'