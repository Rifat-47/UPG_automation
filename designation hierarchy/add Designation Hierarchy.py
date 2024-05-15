"""add designation hierarchy from one program to another program"""
"""parent and child programs are hard-coded here, need to change info while working with other program & cohorts"""

import requests
import json
import sys

# getting access token by login
login_json = requests.post('https://upgapstg.brac.net/upg-auth/api/v1/account/login',
                          data ={"email": "admin@brac.net","password": "123456"})

if login_json.status_code == 200:
    print('logged in successfully')
    # deserialize a JSON formatted string into a Python object
    login_data = json.loads(login_json.content)

    access_token = login_data['result']['access_token']

    # Get all programs
    program_data = requests.get('https://upgapstg.brac.net/upg-participant-selection/api/v1/program',
                                headers={'Authorization': f"Bearer {access_token}"})
    program_info = json.loads(program_data.content)
    all_program = program_info['resultset']
    program_dictionary = []
    for index, program in enumerate(all_program):
        # print(program['is_active'])
        if program['is_active']:
            program_dictionary.append({
                'Serial': index + 1,
                'Program_name': program['program_name'],
                'Program_id': program['id'],
                'Cohorts' : []
            })

    for program in program_dictionary:
        # program_id = '5a4772b9-83d2-4fcb-950f-7bd0006ce78c'
        program_id = program['Program_id']
        cohorts_of_program_json = requests.get(f'https://upgapstg.brac.net/upg-participant-selection/api/v1/cohort/{program_id}',
                                               headers={'Authorization': f"Bearer {access_token}"})
        cohorts_of_program_info = json.loads(cohorts_of_program_json.content)
        # print(cohorts_of_program_info)
        cohorts_values = cohorts_of_program_info['resultset']
        cohort_datas = []
        for index, cohort in enumerate(cohorts_values):
            if cohort['is_active']:
                cohort_data = {
                    'cohort_serial' : index + 1,
                    'cohort_name' : cohort['cohort'],
                    'cohort_id' : cohort['id']
                }
                cohort_datas.append(cohort_data)
        program['Cohorts'] = cohort_datas
    # print(program_dictionary[-1])

    print('All Programs: ')
    for program in program_dictionary:
        print(program['Serial'], ' ', program['Program_name'])

    selected_program = int(input('Select Parent Program: '))
    selected_program_name = ''
    selected_cohort = None
    print(program_dictionary)

    # showing all cohorts & get selected cohort
    for program in program_dictionary:
        if 'Serial' in program and program['Serial'] == selected_program:
            selected_program_name = program['Program_name']
            print(f"Select Cohort of {selected_program_name}: ")
            all_cohorts_of_a_program = program['Cohorts']
            for cohort in all_cohorts_of_a_program:
                print(cohort['cohort_serial'], ' ', cohort['cohort_name'])
            selected_cohort = int(input(f'Enter cohort of {selected_program_name}: '))
            break

    selected_cohort_parent_program = None
    selected_cohort_id_parent_program = None
    for program in program_dictionary:
        if 'Program_name' in program and program['Program_name'] == selected_program_name:
            for cohort in program['Cohorts']:
                if cohort['cohort_serial'] == selected_cohort:
                    selected_cohort_parent_program = cohort['cohort_name']
                    selected_cohort_id_parent_program = cohort['cohort_id']
                    break

    print(selected_program_name, selected_cohort_parent_program)

    sys.exit(1)

    """delete child's existing designation hierarchy"""
    child_cohort_id = '0e2035c4-3c96-4e63-965e-85b4e13b9da5'
    child_program_id = "69114ee1-4c0a-4e28-929d-a2c92b115a6e"
    child_current_designation_hierarchy_json = requests.get(f'https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy/{child_cohort_id}',
                                                            headers={'Authorization': f"Bearer {access_token}"})
    child_current_designation_hierarchy_info = json.loads(child_current_designation_hierarchy_json.content)
    child_current_designation_hierarchy = child_current_designation_hierarchy_info['resultset']
    child_current_designation_hierarchy_length = len(child_current_designation_hierarchy)
    print("No of designation hierarchy(child): ", child_current_designation_hierarchy_length)

    current_deleted_hierarchy = 0
    for designation_hierarchy in child_current_designation_hierarchy:
        hierarchy_id = designation_hierarchy['id']
        delete_current_hierarchy_request_json = requests.delete(f'https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy/{hierarchy_id}',
                                                           headers={'Authorization': f"Bearer {access_token}"})
        delete_current_hierarchy_request = json.loads(delete_current_hierarchy_request_json.content)
        if delete_current_hierarchy_request['status'] == "ok":
            current_deleted_hierarchy += 1

    if child_current_designation_hierarchy_length == current_deleted_hierarchy:
        print("All existing designation hierarchy deleted.")
    else:
        print(f'{current_deleted_hierarchy} out of {child_current_designation_hierarchy_length} designation hierarchy deleted.')
    # sys.exit(1)

    """ diupg-2023 = cohort id: df90c5c9-7fb3-4633-99db-259b2ce82990 """
    """fetching data from existing cohort to update our expected cohort"""
    parent_cohort_id = 'df90c5c9-7fb3-4633-99db-259b2ce82990'
    parent_designation_hierarchy_json = requests.get(f"https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy/{parent_cohort_id}",
                                                     headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    parent_hierarchy_info = json.loads(parent_designation_hierarchy_json.content)

    # hierarchy_info_length & success compare & check if all data loaded successfully
    parent_hierarchy_info_length = len(parent_hierarchy_info['resultset'])
    designation_hierarchy_updated = 0

    """need to update cohort_id & program_id"""
    for single_hierarchy in parent_hierarchy_info['resultset']:
        data = [{
            'cohort_id': child_cohort_id,
            'is_active': single_hierarchy['is_active'],
            'level': single_hierarchy['level'],
            'parent_role_id': single_hierarchy['parent_role_id'],
            'program_id': child_program_id,
            'role_id': single_hierarchy['role_id'],
            'role_name': single_hierarchy['role_name'],
            'parent_role_name': single_hierarchy['parent_role_name']
        }]

        # serialize Python objects into a JSON formatted string
        json_request_body = json.dumps(data)

        """adding designation hierarchy in child program"""
        child_designation_hierarchy_update_request = requests.post("https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy",
                                                                   json= data, headers={'Authorization': f"Bearer {access_token}"})

        if child_designation_hierarchy_update_request.status_code == 200:
            designation_hierarchy_updated += 1
        else:
            print(data)

    if parent_hierarchy_info_length == designation_hierarchy_updated:
        print(f'everything updated! {designation_hierarchy_updated} out of {parent_hierarchy_info_length}')
    else:
        print(f'{designation_hierarchy_updated} data updated out of {parent_hierarchy_info_length}')

else:
    print("Login failed. Please check your credentials.")
