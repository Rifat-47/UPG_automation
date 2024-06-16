"""add input category from one program to another program"""
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

    """stars here"""
    """fetching all inputs data"""
    all_inputs_json = requests.get(
        f"https://upgapstg.brac.net/upg-participant-selection/api/v1/input/get-all",
        headers={'Authorization': f"Bearer {access_token}"})

    all_inputs_data = json.loads(all_inputs_json.content)
    all_inputs_info = all_inputs_data['resultset']

    print('All inputs length', len(all_inputs_info))

    current_child_inputs = []
    parent_inputs = []
    child_program_name = selected_child_program_info['Program_name']
    child_program_id = selected_child_program_info['Program_id']
    child_program_cohort = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']
    parent_program_name = selected_parent_program_info['Program_name']

    # print(selected_parent_program_info)
    parent_program_cohort = selected_parent_cohort_info['cohort_name']
    for inputx in all_inputs_info:
        if inputx["program_name"] == child_program_name and inputx['cohort_name'] == child_program_cohort:
            current_child_inputs.append(inputx)
        if inputx["program_name"] == parent_program_name and inputx['cohort_name'] == parent_program_cohort:
            parent_inputs.append(inputx)

    print('Parent inputs: ', len(parent_inputs))
    print('Current child inputs: ', len(current_child_inputs))

    """delete child's existing inputs"""
    child_deleted_input = 0
    for inputy in current_child_inputs:
        cohort_id = selected_child_cohort_info['cohort_id']
        input_id = inputy['id']
        delete_input_request_json = requests.delete(f"https://upgapstg.brac.net/upg-participant-selection/api/v1/input/{input_id}",
                                                    headers={'Authorization': f"Bearer {access_token}"})
        delete_input_request = json.loads(delete_input_request_json.content)
        # print(delete_material_request)
        if delete_input_request['result']['is_success']:
            child_deleted_input += 1

    if len(current_child_inputs) == child_deleted_input:
        print(f"All existing inputs deleted. Total {child_deleted_input} deleted.")
    else:
        print(
            f'{child_deleted_input} out of {len(current_child_inputs)} inputs has been deleted.')

    # sys.exit(3)

    """adding input setap data"""
    print('Updating input setup, please wait...')
    child_input_updated = 0
    for inputx in parent_inputs:
        data = [
            {
                "type": inputx['type'],
                "code": inputx['code'],
                "cohort_id": child_cohort_id,
                "description": inputx['description']
            }
        ]
        """adding material in child program"""
        child_input_update_request = requests.post('https://upgapstg.brac.net/upg-participant-selection/api/v1/input',
                                                   json=data, headers={'Authorization': f"Bearer {access_token}"})

        if child_input_update_request.status_code == 200:
            child_input_updated += 1
        else:
            print(data)

    if len(parent_inputs) == child_input_updated:
        print(f'Everything updated! {child_input_updated} out of {len(parent_inputs)}')
    else:
        print(f'{child_input_updated} data updated out of {len(parent_inputs)}')

else:
    print('Login failed. Try with correct credentials')