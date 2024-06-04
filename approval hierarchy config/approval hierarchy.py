"""approval hierarchy setup from one program to another program"""
"""Just select the program and cohort of source program and target program, you are good to go"""
"""Remember, Parent refers to source program and child refers to target program"""


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

    # Fetch program and cohort data in a single API call
    program_data = requests.get('https://upgapstg.brac.net/upg-participant-selection/api/v1/program',
                                headers={'Authorization': f"Bearer {access_token}"})
    program_info = json.loads(program_data.content)
    all_program = program_info['resultset']

    # Initialize program dictionary
    program_dictionary = []

    # Iterate over programs
    for index, program in enumerate(all_program):
        if program['is_active']:
            # Initialize cohorts list for each program
            cohorts_data = []
            # Fetch cohorts data for the current program
            cohorts_of_program_json = requests.get(
                f'https://upgapstg.brac.net/upg-participant-selection/api/v1/cohort/{program["id"]}',
                headers={'Authorization': f"Bearer {access_token}"})
            cohorts_of_program_info = json.loads(cohorts_of_program_json.content)
            cohorts_values = cohorts_of_program_info['resultset']
            # Iterate over cohorts of the program
            cohort_serial = 0
            for cohort_index, cohort in enumerate(cohorts_values):
                if cohort['is_active']:
                    cohort_serial += 1
                    cohorts_data.append({
                        'cohort_serial': cohort_serial,
                        'cohort_name': cohort['cohort'],
                        'cohort_id': cohort['id']
                    })

            # Add program info with cohorts to program_dictionary
            program_dictionary.append({
                'Serial': index + 1,
                'Program_name': program['program_name'],
                'Program_id': program['id'],
                'Cohorts': cohorts_data
            })

    # Print all programs
    print('***** All Programs *****:')
    for program in program_dictionary:
        print(program['Serial'], program['Program_name'])

    # Select parent program and cohort
    selected_parent_program = int(input('$$$$$ Select Parent Program: '))
    selected_parent_program_info = program_dictionary[selected_parent_program - 1]  # Adjusting index
    # print(selected_parent_program_info)
    print(f"Select Cohort of {selected_parent_program_info['Program_name']}: ")

    for cohort in selected_parent_program_info['Cohorts']:
        print(cohort['cohort_serial'], cohort['cohort_name'])
    selected_parent_cohort = int(input('*** Enter Parent cohort: '))

    # Get selected parent cohort info
    selected_parent_cohort_info = selected_parent_program_info['Cohorts'][
        selected_parent_cohort - 1]  # Adjusting index
    parent = selected_parent_program_info['Program_name'] + ' ' + selected_parent_cohort_info['cohort_name']


    ##### Select child program and cohort
    print("*****Now, select Child program and cohort*****")
    print('All Programs:')
    for program in program_dictionary:
        print(program['Serial'], program['Program_name'])

    selected_child_program = int(input('$$$$$ Select Child Program: '))
    selected_child_program_info = program_dictionary[selected_child_program - 1]  # Adjusting index
    print(f"Select Cohort of {selected_child_program_info['Program_name']}: ")
    for cohort in selected_child_program_info['Cohorts']:
        print(cohort['cohort_serial'], cohort['cohort_name'])

    selected_child_cohort = int(input('Enter child cohort: '))
    # Get selected child cohort info
    selected_child_cohort_info = selected_child_program_info['Cohorts'][selected_child_cohort - 1]  # Adjusting index
    child = selected_child_program_info['Program_name'] + " " + selected_child_cohort_info['cohort_name']

    # print(parent)
    # print(child)
    if parent == child:
        print("Program & cohort of parent and child is similar, can't advance further.")
        sys.exit(5)

    """delete child's existing approval hierarchy data"""
    child_cohort_id = selected_child_cohort_info['cohort_id']
    child_program_id = selected_child_program_info['Program_id']

    child_current_data_json = requests.get(
        f'https://upgapstg.brac.net/upg-enrollment/api/v1/approval/approval-hierarchy/all-by-cohort/{child_cohort_id}',
        headers={'Authorization': f"Bearer {access_token}"})
    child_current_data_info = json.loads(child_current_data_json.content)

    if 'resultset' in child_current_data_info:
        child_current_data = child_current_data_info['resultset']
        child_current_data_length = len(child_current_data)
        print("No of designation hierarchy(child): ", child_current_data_length)

        current_deleted_data = 0
        for data in child_current_data:
            data_id = data['id']
            delete_current_data_json = requests.delete(
                f'https://upgapstg.brac.net/upg-auth/api/v1/supervision/roles/hierarchy/{data_id}',
                headers={'Authorization': f"Bearer {access_token}"})
            delete_current_data_request = json.loads(delete_current_data_json.content)
            if delete_current_data_request['status'] == "ok":
                current_deleted_data += 1

        if child_current_data_length == current_deleted_data:
            print(f"All existing data deleted. Total {current_deleted_data} deleted.")
        else:
            print(
                f'{current_deleted_data} out of {child_current_data_length} data has been deleted.')
    else:
        print('Sorry,' + ' ' + child_current_data_info['message'])

    """fetching data from existing cohort to update our expected cohort"""
    parent_cohort_id = selected_parent_cohort_info['cohort_id']

    parent_data_json = requests.get(
        f"https://upgapstg.brac.net/upg-enrollment/api/v1/approval/approval-hierarchy/all-by-cohort/{parent_cohort_id}",
        headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    parent_data_info = json.loads(parent_data_json.content)

    # hierarchy_info_length & success compare & check if all data loaded successfully
    parent_data_info_length = len(parent_data_info['resultset'])
    data_updated = 0

    """need to update cohort_id & program_id"""
    print('Updating info, please wait...')
    for data_info in parent_data_info['resultset']:
        data = [{
            'list': {
                'cohort_id': child_cohort_id,
                'category_id': data_info['category_id'],
                'category_name': data_info['category_name'],
                'is_chain_approval': data_info['is_chain_approval'],
                'from_role': data_info['from_role'],
                'to_roles': data_info['to_role']
            }
        }]

        """adding designation hierarchy in child program"""
        child_supervision_hierarchy_update_request = requests.post(
            "https://upgapstg.brac.net/upg-auth/api/v1/supervision/roles/hierarchy",
            json=data, headers={'Authorization': f"Bearer {access_token}"})

        if child_supervision_hierarchy_update_request.status_code == 200:
            data_updated += 1
        else:
            print(data)

    if parent_data_info_length == data_updated:
        print(f'Everything updated! {data_updated} out of {parent_data_info_length}')
    else:
        print(f'{data_updated} data updated out of {parent_data_info_length}')

else:
    print('Login failed. Try with correct credentials')

