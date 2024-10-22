"""SELECT * from enterprise WHERE cohort_id=child_cohort_id ALLOW FILTERING; """
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
    # Delete from enterprise where id = '0d7f709d-571b-4243-8b17-bfbe4c0f8b92';
    query_list.append(f"Delete from group_wise_enterprise where id='{data[0]}';")

for query in query_list:
    print(query)

print(len(query_list))