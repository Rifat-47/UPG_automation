"""copy access point management from one program to another program"""

import requests
import json
from datetime import datetime
import sys

# Start measuring execution time
starting_time = datetime.now()

print('Welcome to UPG programme configuration!')
print('***** All Environment *****:')
environment = {
    '1': ['Stage', 'https://upgapstg.brac.net'],
    '2': ['Training', 'https://trainingupg.brac.net'],
    '3': ['Production', 'https://upgbd.brac.net']
}

for env in environment:
    print(env, environment[env][0])

# print('$$$ Select Environment:')
selected_environment = str(input('$$$ Select Environment: '))
base_url = ''
credential = {"email": "admin@brac.net", "password": "123456"}
for env in environment:
    if environment[selected_environment][0] == environment[env][0]:
        base_url = environment[env][1]
        if environment[env][0].upper() == 'PRODUCTION':
            credential = {"email": "admin@brac.net", "password": "12345@#"}
        break

# Login to the system
login_json = requests.post(f'{base_url}/upg-auth/api/v1/account/login',
                          data = credential)

# Check if login was successful
if login_json.status_code == 200:
    print('Success! Logged in successfully!!')

    # deserialize login response: JSON formatted string into a Python object
    login_data = json.loads(login_json.content)
    access_token = login_data['result']['access_token']

    print('----------------------------------------------------------------------------')
    # Get all module names
    module_names_json = requests.get(f"{base_url}/upg-auth/api/v1/acl/menu",
                                headers={'Authorization': f"Bearer {access_token}"})
    modules_data = json.loads(module_names_json.content)
    modules_info = modules_data['resultset']
    all_modules = []  # total 10 module from m1 to m10
    for i in modules_info:
        if not i['id'].startswith('w'):
            all_modules.append(i)
    print('all modules length: ', len(all_modules))

    print('----------------------------------------------------------------------------')
    # Get all roles
    roles_json = requests.get(f"{base_url}/upg-auth/api/v1/roles",
                              headers={'Authorization': f"Bearer {access_token}"})
    roles_data = json.loads(roles_json.content)
    roles_info = roles_data['resultset']
    all_roles = []
    for role in roles_info:
        if role['is_active']:
            all_roles.append(role)
            # print(role['role_name'])
    print('active roles: ', len(all_roles))

    # child_program_name = selected_child_program_info['Program_name']
    # child_program_id = selected_child_program_info['Program_id']
    # child_cohort_name = selected_child_cohort_info['cohort_name']
    # child_cohort_id = selected_child_cohort_info['cohort_id']
    #
    # parent_program_name = selected_parent_program_info['Program_name']
    # parent_program_id = selected_parent_program_info['Program_id']
    # parent_cohort_name = selected_parent_cohort_info['cohort_name']
    # parent_cohort_id = selected_parent_cohort_info['cohort_id']

    """***main code starts here***"""
    # Get all programs
    program_data = requests.get(f'{base_url}/upg-participant-selection/api/v1/program',
                                headers={'Authorization': f"Bearer {access_token}"})
    program_info = json.loads(program_data.content)
    all_program_set = program_info['resultset']
    all_program = []
    for programme in all_program_set:
        if programme['is_active']:
            all_program.append(programme)

    program_dictionary = []
    for index, program in enumerate(all_program):
        program_dictionary.append({
            'Serial': index + 1,
            'Program_name': program['program_name'],
            'Program_id': program['id']
        })

    print('All Programs: ')
    for program in program_dictionary:
        print(program['Serial'], ': ', program['Program_name'])

    # Input parent and child program numbers
    parent_program = int(input('Enter Parent Program No (Interger Value): '))
    print('great!')
    child_program = int(input('Enter Child Program No (Integer Value): '))

    # Check if input program numbers are valid
    if not (program_dictionary[0]['Serial'] <= parent_program <= program_dictionary[-1]['Serial'] and
            program_dictionary[0]['Serial'] <= child_program <= program_dictionary[-1]['Serial']):
        print("Invalid parent_program_id or child_program_id entered. Run the program again!")
        sys.exit(1)
    else:
        # Get program IDs and names based on input program numbers
        parent_program_id, parent_program_name = 0, ''
        child_program_id, child_program_name = 0, ''

        for program in program_dictionary:
            if program['Serial'] == parent_program:
                parent_program_id, parent_program_name = program['Program_id'], program['Program_name']
            if program['Serial'] == child_program:
                child_program_id, child_program_name = program['Program_id'], program['Program_name']

    print(f'$$$$$***** Starting Now *****$$$$$')
    print("##############################################################################################")
    # Access point management for each role
    role_count = 0
    finished_roles = []
    for role in all_roles:
        role_id = role['id']
        print(f'Role Name = "{role['role_name']}", Role Id = {role_id}')

        # Get access control info for child program
        child_access_control_data = requests.get(f"{base_url}/upg-auth/api/v1/roles/{role_id}/acl/program/{child_program_id}",
                                                 headers={'Authorization': f"Bearer {access_token}"})
        child_access_control_info = json.loads(child_access_control_data.content)
        child_all_info = child_access_control_info['resultset']
        print(f"======= {child_program_name} info for '{role['role_name']}': {len(child_all_info)} =======")

        # Get access control info for parent program
        parent_access_control_data = requests.get(f"{base_url}/upg-auth/api/v1/roles/{role_id}/acl/program/{parent_program_id}",
                                                  headers={'Authorization': f"Bearer {access_token}"})

        # deserialize a JSON formatted string into a Python object
        parent_access_control_info = json.loads(parent_access_control_data.content)
        parent_all_info = parent_access_control_info['resultset']
        print(f"======= {parent_program_name} info for '{role['role_name']}': {len(parent_all_info)} =======")

        # If no access control info for parent program, skip
        if len(parent_all_info) == 0:
            finished_roles.append(role['role_name'])
            role_count += 1
            print(f'***** work finished for {role['role_name']}: as found no data *****')
            print('##############################################################################################')
            continue

        # Process access control info
        count = 0
        for parent_info in parent_all_info:
            data_for_edit = {
                "role_id": role_id,
                "role_name": parent_info["role_name"],
                "program_id": child_program_id,
                "menu_id": parent_info["menu_id"],
                "menu_name": parent_info["menu_name"],
                "menu_order": parent_info["menu_order"],
                "submenu_id": parent_info["submenu_id"],
                "submenu_name": parent_info["submenu_name"],
                "submenu_order": parent_info["submenu_order"],
                "actions": parent_info["actions"],
                "is_active": parent_info["is_active"]
            }
            child_request_body_for_edit = json.dumps(data_for_edit)

            data_for_add = {
                "list" : [
                    {
                        "role_id": role_id,
                        "role_name": parent_info["role_name"],
                        "program_id": child_program_id,
                        "menu_id": parent_info["menu_id"],
                        "menu_name": parent_info["menu_name"],
                        "menu_order": parent_info["menu_order"],
                        "submenu_id": parent_info["submenu_id"],
                        "submenu_name": parent_info["submenu_name"],
                        "submenu_order": parent_info["submenu_order"],
                        "actions": parent_info["actions"],
                        "is_active": parent_info["is_active"]
                    }
                ]
            }
            child_request_body_for_add = json.dumps(data_for_add)

            child_info_id_tobe_updated = ''
            child_info_id_found = False

            for child_info in child_all_info:
                if child_info['menu_id'] == parent_info["menu_id"] and child_info['submenu_id'] == parent_info["submenu_id"]:
                    child_info_id_tobe_updated = child_info['id']
                    child_info_id_found = True
                    break

            if child_info_id_found:
                # print('data updating')
                update_request = requests.put(f'{base_url}/upg-auth/api/v1/roles/{role_id}/acl/{child_info_id_tobe_updated}',
                                              data= child_request_body_for_edit,
                                              headers= {'Authorization': f"Bearer {access_token}", 'Content-Type': 'application/json'})
            else:
                update_request = requests.post(f'{base_url}/upg-auth/api/v1/roles/{role_id}/acl',
                                               data= child_request_body_for_add,
                                               headers={'Authorization': f"Bearer {access_token}", 'Content-Type': 'application/json'})
            update_request_info = json.loads(update_request.content)
            # print(update_request_info)
            if update_request_info['status'] == "ok":
                count += 1
            else:
                print(f"Error: {parent_info}")

        print(f'***** Data updated for "{role['role_name']}": {count} of {len(parent_all_info)} updated *****')
        finished_roles.append(role['role_name'])
        print('##############################################################################################')
        role_count += 1
    print('Access point completed for: ', finished_roles)
    print(f'Updated {role_count} out of {len(all_roles)} roles.')
else:
    print('Error: Login failed, please check your email & password')

# End measuring execution time
ending_Time = datetime.now()
total_time = ending_Time - starting_time

# Extract minutes and seconds from the time difference
minutes = total_time.seconds // 60
seconds = total_time.seconds % 60

time_difference_str = f"{minutes}min {seconds}s"
print("Total Time taken:", time_difference_str)