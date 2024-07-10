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
    sql_commands.append(f"DELETE from collection_point WHERE id={a} AND vo_id={b} and"
                        f" participant_id={c};")

# Print SQL commands
for query in sql_commands:
    print(query)

# Print the number of SQL commands
print(len(sql_commands))


# collection_point
# "id" = db595f10-ba22-4c1b-85bf-c347aed4fcf7
# "vo_id" = adc014e7-e557-4e3a-a405-df35b68ed92e
# "participant_id" = 2544a542-f6f8-49b9-abe0-347e4b9d2cec);