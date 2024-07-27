"""need to work more on this, not complete yet"""

import openpyxl
import uuid

# Load the workbook
workbook = openpyxl.load_workbook('../Book1.xlsx')

# Get all sheet names
sheet_names = workbook.sheetnames

all_data = []
query_list = []

for sheet_name in sheet_names:
    # Select the sheet by name
    sheet = workbook[sheet_name]
    # print(sheet)
    # print(sheet.min_row, sheet.max_row)
    # print(sheet.min_column, sheet.max_column)

    for row in sheet.iter_rows(min_row=sheet.min_row, max_row=sheet.max_row, min_col=sheet.min_column, max_col=sheet.max_column):
        # query = f'DELETE from collection_point WHERE id={} AND vo_id={} and participant_id={};'
        # for cell in row:
        #     print(cell.value)
        row_data = [cell.value for cell in row]
        all_data.append(row_data)
    break

print(all_data)
uuid_values = []

for data in all_data:
    uuid_value = uuid.uuid1()
    while uuid_value in uuid_values:
        uuid_value = uuid.uuid1()

    uuid_values.append(uuid_value)

    if data[1] == 'c6b60ecf-472d-4ecf-9c8e-6ca4c919d518':
        category_id = '1f413b9d-a770-441a-a569-89e69b22e350'
    elif data[1] == 'c9546f8b-6bcb-4c98-93c9-a049ca1f2f13':
        category_id = '77afab68-bddf-44ff-bbc0-2c843a2637fb'
    elif data[1] == '3b76400d-0fa2-4113-909a-9af8da9cfc74':
        category_id = 'f2c67443-c3ea-46c2-8fcf-00a9d8ca25ab'
    else:
        category_id = ''

    query_list.append(f'Insert into enterprise ("id","category_id","client_created_at","client_updated_at","cohort_id","created_at","created_by","description","enterprise_code","is_active","main_asset_id","main_asset_quantity","name","supporting_asset_id","supporting_asset_quantity","updated_at","updated_by") VALUES '
    f"('{uuid_value}', {category_id}, '{data[2]}', '{data[3]}', 6a1325d4-07cc-4985-b7cc-c945c4f536fe, toTimestamp(now()), {data[6]}, {data[7]}, '{data[8]}', {str(data[9]).lower()}, {data[10]}, {data[11]}, '{data[12]}', {data[13]}, {data[14]}, toTimestamp(now()), {data[16]});")

for query in query_list:
    print(query)

print(len(query_list))