"""SELECT * from group_visit_schedule WHERE cohort_id=e64173ea-09d7-4ddc-af63-3158e14ae3b2 and branch_id=5f7b8261-5620-4ba7-9134-0448aa2f3809;"""
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
    query_list.append(f"Delete from group_visit_schedule where cohort_id={data[0]} and collection_point_id={data[1]} and id={data[2]};")

for query in query_list:
    print(query)

print(len(query_list))