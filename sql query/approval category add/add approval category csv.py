from datetime import datetime
from tabulate import tabulate
import csv

# Load the CSV file
csv_filename = '../CSV1.csv'

all_data = []
query_list = []

# Read the CSV file
with open(csv_filename, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)  # Read the header row
    print(type(csv_reader))
    for row in csv_reader:
        all_data.append(row)

cohort_id = input('Enter cohort id: ')

for data in all_data:
    query_list.append(
        f'INSERT INTO approval_category ('
        f'"cohort_id","category_key","id","attribute","category_key_notification","category_name","created_at",'
        f'"created_by","is_active","is_adhoc_approval","updated_at","updated_by") VALUES ('
        f"'{cohort_id}', "
        f"'{data[1]}', uuid(), null, '{data[4]}', '{data[5]}', '{data[6]}', '{data[7]}', true, true, '{data[10]}', null);"
    )

for query in query_list:
    print(query)

print(len(query_list))