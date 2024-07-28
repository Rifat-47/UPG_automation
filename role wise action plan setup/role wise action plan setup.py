"""Completed"""
"""add role wise action plan setup from one program to another program"""
"""action plan type setup is required for child program"""
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

    """delete child's existing role wise action plan setup"""
    child_cohort_id = selected_child_cohort_info['cohort_id']
    child_program_id = selected_child_program_info['Program_id']

    child_role_wise_action_plan_json = requests.get(
        f'https://upgapstg.brac.net/upg-enrollment/api/v1/action-plan/role-wise-type/all-by-cohort/{child_cohort_id}',
        headers={'Authorization': f"Bearer {access_token}"})
    child_current_role_wise_action_plan_info = json.loads(child_role_wise_action_plan_json.content)

    if 'resultset' in child_current_role_wise_action_plan_info:
        child_current_role_wise_action_plan = child_current_role_wise_action_plan_info['resultset']
        child_current_role_wise_action_plan_length = len(child_current_role_wise_action_plan)
        print("No of role wise action plan (child): ", child_current_role_wise_action_plan_length)

        current_deleted_role_wise_action_plan = 0
        for role_wise_action_plan in child_current_role_wise_action_plan:
            action_plan_id = role_wise_action_plan["action_plan_type_id"]
            role_id = role_wise_action_plan["role_id"]
            action_plan_type_id = role_wise_action_plan["action_plan_type_id"]
            delete_current_role_wise_action_plan_request_json = requests.delete(
                f'https://upgapstg.brac.net/upg-enrollment/api/v1/action-plan/role-wise-type/delete/cohort-id/{child_cohort_id}/role-id/{role_id}/action-plan-type-id/{action_plan_type_id}',
                headers={'Authorization': f"Bearer {access_token}"})
            delete_current_role_wise_action_plan_request = json.loads(delete_current_role_wise_action_plan_request_json.content)
            if delete_current_role_wise_action_plan_request['status'] == "ok":
                current_deleted_role_wise_action_plan += 1

        if child_current_role_wise_action_plan_length == current_deleted_role_wise_action_plan:
            print(f"All existing action plan type deleted. Total {current_deleted_role_wise_action_plan} deleted.")
        else:
            print(
                f'{current_deleted_role_wise_action_plan} out of {child_current_role_wise_action_plan_length} role wise action plan has been deleted.')
    else:
        print('Sorry,' + ' ' + child_current_role_wise_action_plan_info['message'])


    """fetching data from existing cohort to update our expected cohort"""
    parent_cohort_id = selected_parent_cohort_info['cohort_id']

    # print(f"https://upgapstg.brac.net/upg-auth/api/v1/supervision/roles/hierarchy/{parent_cohort_id}")
    parent_role_wise_action_plan_json = requests.get(
        f"https://upgapstg.brac.net/upg-enrollment/api/v1/action-plan/role-wise-type/all-by-cohort/{parent_cohort_id}",
        headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    parent_role_wise_action_plan_info = json.loads(parent_role_wise_action_plan_json.content)
    # print(parent_role_wise_action_plan_info)

    # hierarchy_info_length & success compare & check if all data loaded successfully
    parent_role_wise_action_plan_info_length = len(parent_role_wise_action_plan_info['resultset'])
    print("Total parent role wise action plan: ", parent_role_wise_action_plan_info_length)

    role_wise_action_plan_updated = 0

    """get action plan category id for both parent & child program by cohort_id"""
    parent_action_plan_type_map = {}
    child_action_plan_type_map = {}

    child_current_action_plan_type_json = requests.get(
        f'https://upgapstg.brac.net/upg-enrollment/api/v1/action-plan/type/by-cohort/{child_cohort_id}',
        headers={'Authorization': f"Bearer {access_token}"})
    child_current_action_plan_type_info = json.loads(child_current_action_plan_type_json.content)

    for action_plan_type in child_current_action_plan_type_info['resultset']:
        child_action_plan_type_map[action_plan_type["action_plan_name"]] = action_plan_type['id']

    parent_current_action_plan_type_json = requests.get(
        f'https://upgapstg.brac.net/upg-enrollment/api/v1/action-plan/type/by-cohort/{parent_cohort_id}',
        headers={'Authorization': f"Bearer {access_token}"})
    parent_current_action_plan_type_info = json.loads(parent_current_action_plan_type_json.content)

    for action_plan_type in parent_current_action_plan_type_info['resultset']:
        parent_action_plan_type_map[action_plan_type["id"]] = action_plan_type["action_plan_name"]


    """need to update cohort_id & program_id"""
    print('Updating info, please wait...')
    for single_role_wise_action_plan in parent_role_wise_action_plan_info['resultset']:
        action_plan_type_id = single_role_wise_action_plan["action_plan_type_id"]
        action_plan_type_name = parent_action_plan_type_map.get(action_plan_type_id, '')
        child_action_plan_id = child_action_plan_type_map.get(action_plan_type_name, '')

        data = {
            "role_wise_action_plan_types": [
                {
                    "action_plan_type_id": child_action_plan_id,
                    "action_plan_type_name": single_role_wise_action_plan["action_plan_type_name"],
                    "role_id": single_role_wise_action_plan["role_id"],
                    "role_name": single_role_wise_action_plan["role_name"],
                    "cohort_id": child_cohort_id
                }
            ]
        }
        # print(action_plan_type_id, action_plan_type_name, child_action_plan_id)
        # exit(1)

        """adding role wise action plan setup request in child program"""
        child_role_wise_action_plan_update_request = requests.post(
            "https://upgapstg.brac.net/upg-enrollment/api/v1/action-plan/role-wise-type/add",
            json=data, headers={'Authorization': f"Bearer {access_token}"})

        if child_role_wise_action_plan_update_request.status_code == 200:
            role_wise_action_plan_updated += 1
        else:
            print(data)

    if parent_role_wise_action_plan_info_length == role_wise_action_plan_updated:
        print(f'Everything updated! {role_wise_action_plan_updated} out of {parent_role_wise_action_plan_info_length}')
    else:
        print(f'{role_wise_action_plan_updated} data updated out of {parent_role_wise_action_plan_info_length}')

else:
    print('Login failed. Try with correct credentials')

