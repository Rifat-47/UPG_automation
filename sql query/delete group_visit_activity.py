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
column_d_values = df.iloc[:, 3].tolist()

# Generate SQL commands
sql_commands = []
# for a, b in zip(column_a_values, column_b_values):
for a, b, c, d in zip(column_a_values, column_b_values, column_c_values, column_d_values):
    sql_commands.append(f"DELETE from group_visit_activity WHERE cohort_id='{a}' AND branch_id='{b}' and group_visit_schedule_id='{c}' and id={d};")

# Print SQL commands
for query in sql_commands:
    print(query)

# Print the number of SQL commands
print(len(sql_commands))

# group_visit_activity -
# "cohort_id" = '63384b69-414e-431f-9e4c-1adfe07801fd'
# "branch_id" = '21399120-651c-4fb2-b2fb-c27fa99b4f88'
# "group_visit_schedule_id" = '1f0d5b4d-c833-414c-b5f1-1ad9f56a9c34'
# "id" = b6bb6378-a1b5-4253-9b0d-e540e2cccc31);
