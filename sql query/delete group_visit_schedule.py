import pandas as pd
import openpyxl

# Read the Excel file
excel_file = 'Book1.xlsx'  # Replace with your file name
sheet_name = 'Sheet1'  # Replace with your sheet name if necessary

# Load the sheet into a DataFrame
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Extract columns A, B, and C into separate lists
column_a_values = df.iloc[:, 0].tolist()
column_b_values = df.iloc[:, 1].tolist()
column_c_values = df.iloc[:, 2].tolist()

# Generate SQL commands
sql_commands = []
# for a, b in zip(column_a_values, column_b_values):
for a, b, c in zip(column_a_values, column_b_values, column_c_values):
    sql_commands.append(f"DELETE from group_visit_schedule WHERE cohort_id={a} AND collection_point_id={b} and id={c};")

# Print SQL commands
for query in sql_commands:
    print(query)

# Print the number of SQL commands
print(len(sql_commands))

# group_visit_schedule
# "cohort_id" = df90c5c9-7fb3-4633-99db-259b2ce82990
# "collection_point_id" = 023ae117-254f-47a1-a7ba-641030d15f54
# "id" = 03765161-0607-43f2-9f13-949d80af41c9);
