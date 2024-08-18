"""SELECT * from input_category WHERE cohort_id=child_cohort_id ALLOW FILTERING; """
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
    for row in csv_reader:
        all_data.append(row)


for data in all_data:
    query_list.append(f"Delete from input_category where id={data[0]};")

for query in query_list:
    print(query)

print(len(query_list))