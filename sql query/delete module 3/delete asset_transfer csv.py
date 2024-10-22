"""SELECT * from asset_transfer WHERE cohort_id= '63384b69-414e-431f-9e4c-1adfe07801fd' ALLOW FILTERING;"""
"""export csv file and run the script"""

import csv

# Load the CSV file
csv_filename = '../CSV1.csv'

all_data = []
query_list = []

# Read the CSV file
with open(csv_filename, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)  # Read the header row
    # print(type(csv_reader))
    for row in csv_reader:
        all_data.append(row)


for data in all_data:
    query_list.append(f"Delete from asset_transfer where batch_id='{data[0]}';")

for query in query_list:
    print(query)

print(len(query_list))