"""add asset & input mapping from one program to another program"""
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
    print(selected_child_cohort_info)

    # print(parent)
    # print(child)
    if parent == child:
        print("Program & cohort of parent and child is similar, can't advance further.")
        sys.exit(5)

    """stars here"""
    """fetching all inputs data"""
    all_reason_setup_json = requests.get(
        f"https://upgapstg.brac.net/upg-participant-selection/api/v1/reason/reasons/all",
        headers={'Authorization': f"Bearer {access_token}"})

    all_reason_setup_data = json.loads(all_reason_setup_json.content)
    all_reason_setup_info = all_reason_setup_data['resultset']

    print('All reason setup length', len(all_reason_setup_info))

    current_child_reason_setup = []
    parent_reason_setup = []
    child_program_name = selected_child_program_info['Program_name']
    child_program_id = selected_child_program_info['Program_id']
    child_program_cohort = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']
    parent_program_name = selected_parent_program_info['Program_name']

    # print(selected_parent_program_info)
    parent_program_cohort = selected_parent_cohort_info['cohort_name']
    for inputx in all_reason_setup_info:
        if inputx["program_name"] == child_program_name and inputx['cohort_name'] == child_program_cohort:
            current_child_reason_setup.append(inputx)
        if inputx["program_name"] == parent_program_name and inputx['cohort_name'] == parent_program_cohort:
            parent_reason_setup.append(inputx)

    print('Parent reason setup: ', len(parent_reason_setup))
    print('Current child reason setup: ', len(current_child_reason_setup))

    # sys.exit(5)

    """deactivating the cohort"""
    # getting all cohorts of child program
    child_program_cohorts_request_json = requests.get(
        f"https://upgapstg.brac.net/upg-participant-selection/api/v1/cohort/{child_program_id}",
        headers={'Authorization': f"Bearer {access_token}"})
    child_program_cohorts_request_info = json.loads(child_program_cohorts_request_json.content)
    child_program_cohorts_data = child_program_cohorts_request_info['resultset']
    data_for_activate_deactivate_cohort = {}
    for child_cohort in child_program_cohorts_data:
        if child_cohort['id'] == child_cohort_id:
            del child_cohort['id']
            data_for_activate_deactivate_cohort = child_cohort
            break

    # getting child cohort info
    data_for_activate_deactivate_cohort['slNo'] = 1
    data_for_activate_deactivate_cohort['is_active'] = False
    deactivate_cohort_request_json = requests.patch(f"https://upgapstg.brac.net/upg-participant-selection/api/v1/cohort/update/{child_cohort_id}",
                                                    json= data_for_activate_deactivate_cohort,
                                                    headers={'Authorization': f"Bearer {access_token}"})
    deactivate_cohort_request = json.loads(deactivate_cohort_request_json.content)
    if not deactivate_cohort_request['result']['is_success']:
        print('Cohort is not deactivated, try again!')
        sys.exit(3)
    else:
        print('Cohort is deactivated...')

    """delete child's existing reason setup"""
    child_deleted_reason_setup = 0
    for child_reason in current_child_reason_setup:
        reason_setup_id = child_reason['id']
        delete_reason_setup_request_json = requests.delete(f"https://upgapstg.brac.net/upg-participant-selection/api/v1/reason/delete/{child_cohort_id}/{reason_setup_id}",
                                                           headers={'Authorization': f"Bearer {access_token}"})
        delete_reason_setup_request = json.loads(delete_reason_setup_request_json.content)
        # print(delete_reason_setup_request)
        if delete_reason_setup_request['result']['is_success']:
            child_deleted_reason_setup += 1

    if len(current_child_reason_setup) == child_deleted_reason_setup:
        print(f"All existing reason setup deleted. Total {child_deleted_reason_setup} deleted.")
    else:
        print(
            f'{child_deleted_reason_setup} out of {len(current_child_reason_setup)} reason setup has been deleted.')

    """activating the cohort again"""
    data_for_activate_deactivate_cohort['is_active'] = True
    activate_cohort_request_json = requests.patch(
        f"https://upgapstg.brac.net/upg-participant-selection/api/v1/cohort/update/{child_cohort_id}",
        json=data_for_activate_deactivate_cohort,
        headers={'Authorization': f"Bearer {access_token}"})
    activate_cohort_request = json.loads(activate_cohort_request_json.content)
    if not activate_cohort_request['result']['is_success']:
        print('Cohort is not activated, try again!')
        sys.exit(4)
    else:
        print('Cohort is activated...')

    """fetching all reason type"""
    all_reason_type_json = requests.get(f'https://upgapstg.brac.net/upg-participant-selection/api/v1/reason/reason-type/all',
                                        headers={'Authorization': f"Bearer {access_token}"})
    all_reason_type_info = json.loads(all_reason_type_json.content)
    all_reason_type_data = all_reason_type_info['resultset']
    print(f'Fetched {len(all_reason_type_data)} reason type data.')

    """adding reason setup data"""
    print('Updating reason setup, please wait...')
    child_reason_setup_updated = 0
    for parent_reason in parent_reason_setup:
        reason_type_id = ''
        for reason_type in all_reason_type_data:
            if parent_reason["type"] == reason_type["reason_type"]:
                reason_type_id = reason_type['id']
                break
        if reason_type_id == '':
            print(f'Error: Type Id not found for "{parent_reason["type"]}"')
            break

        data = {
            "name": parent_reason['name'],
            "cohort_id": child_cohort_id,
            "program_id": child_program_id,
            "type_id": reason_type_id,
            "cohort_name": child_program_cohort,
            "program_name": child_program_name,
            "type": parent_reason["type"]
        }
        """adding input map in child program"""
        child_reason_setup_update_request = requests.post('https://upgapstg.brac.net/upg-participant-selection/api/v1/reason/create',
                                                          json=data, headers={'Authorization': f"Bearer {access_token}"})
        if child_reason_setup_update_request.status_code == 201:
            child_reason_setup_updated += 1
        else:
            print(data)

    if len(parent_reason_setup) == child_reason_setup_updated:
        print(f'Everything updated! {child_reason_setup_updated} out of {len(parent_reason_setup)}')
    else:
        print(f'{child_reason_setup_updated} data updated out of {len(parent_reason_setup)}')

else:
    print('Login failed. Try with correct credentials')


"""
# delete = https://upgapstg.brac.net/upg-participant-selection/api/v1/reason/delete/{child_cohort_id}/{reason_setup_id}

create = https://upgapstg.brac.net/upg-participant-selection/api/v1/reason/create
data = {
        "name":"Due to family constraints",
        "cohort_id":"6a1325d4-07cc-4985-b7cc-c945c4f536fe",
        "program_id":"adf3afb1-9e95-4a46-b4b9-67d4eb6b11af",
        "type_id":"d4c3cf0a-130c-4af0-b296-e7141981bcd4",
        "cohort_name":"2023",
        "program_name":"Load Test",
        "type":"self_exclusion"
       }
status = 201
"""

"""
cohort deactive = 
https://upgapstg.brac.net/upg-participant-selection/api/v1/cohort/update/6a1325d4-07cc-4985-b7cc-c945c4f536fe
patch
data = {
    "client_created_at":"1693897720",
    "client_updated_at":"1717094339",
    "cohort":"2023",
    "created_at":"2023-09-05T07:08:40.618Z",
    "created_by":"cac6aebd-d346-4112-ab7c-b2701f66d90e",
    "description":null,
    "end":"2024-12-30T18:00:00.000Z",
    "is_active":false,
    "months":null,
    "program_id":"adf3afb1-9e95-4a46-b4b9-67d4eb6b11af",
    "start":"2022-12-31T18:00:00.000Z",
    "updated_at":"2023-09-05T07:08:40.618Z",
    "updated_by":"cac6aebd-d346-4112-ab7c-b2701f66d90e",
    "slNo":1}
    
    
    
data before update = {
            "id": "6a1325d4-07cc-4985-b7cc-c945c4f536fe",
            "client_created_at": "1693897720",
            "client_updated_at": "1717094339",
            "cohort": "2023",
            "created_at": "2023-09-05T07:08:40.618Z",
            "created_by": "cac6aebd-d346-4112-ab7c-b2701f66d90e",
            "description": null,
            "end": "2024-12-30T18:00:00.000Z",
            "is_active": true,
            "months": null,
            "program_id": "adf3afb1-9e95-4a46-b4b9-67d4eb6b11af",
            "start": "2022-12-31T18:00:00.000Z",
            "updated_at": "2023-09-05T07:08:40.618Z",
            "updated_by": "cac6aebd-d346-4112-ab7c-b2701f66d90e"
        }
"""