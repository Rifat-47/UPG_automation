from datetime import datetime
from tabulate import tabulate
import csv

# Load the CSV file
csv_filename = '../CSV1.csv'

all_data = []

# Read the CSV file
with open(csv_filename, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)  # Read the header row
    for row in csv_reader:
        all_data.append(row)

# Convert 'Created At' column to datetime objects and sort data
created_at_index = headers.index('created_at')

# Convert 'Created At' values to datetime
for row in all_data:
    if row[created_at_index]:  # Ensure there's a value
        try:
            datetime_obj = datetime.strptime(row[created_at_index], '%Y-%m-%d %H:%M:%S.%f%z')
            row[created_at_index] = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass  # Handle invalid date formats if necessary

# Sort all_data based on 'Created At' in descending order
all_data.sort(key=lambda x: datetime.strptime(x[created_at_index], '%Y-%m-%d %H:%M:%S') if isinstance(x[created_at_index], str) else datetime.min, reverse=True)

print(tabulate(all_data, headers=headers, tablefmt="grid"))
