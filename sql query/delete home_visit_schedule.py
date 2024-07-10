import pandas as pd
import openpyxl

# Read the Excel file
excel_file = 'Book1.xlsx'  # Replace with your file name
sheet_name = 'Sheet1'  # Replace with your sheet name if necessary

# Load the sheet into a DataFrame
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Extract columns A, B, and C into separate lists
column_a_values = df.iloc[:, 0].tolist()

# Generate SQL commands
sql_commands = []

for a in column_a_values:
    sql_commands.append(f"DELETE from home_visit_schedule WHERE id={a};")

# Print SQL commands
for query in sql_commands:
    print(query)

# Print the number of SQL commands
print(len(sql_commands))

# home_visit_schedule
# "id" = e009f3a0-7655-44c8-b1cc-a8235eda00d4);