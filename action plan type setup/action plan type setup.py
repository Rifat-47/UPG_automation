"""completed"""
"""add action plan type setup from one program to another program"""
"""Just select the program and cohort of source program and target program, you are good to go"""
"""Remember, Parent refers to source program and child refers to target program"""
"""mandatory: 1. delete all checklist from 'checklist' table using child cohort id.
    demo: DELETE from checklist WHERE cohort_id='child cohort id';
    
    2. delete all action plan type from from 'action_plan_type' table
    demo: DELETE from action_plan_type WHERE cohort_id=child_cohort_id;
"""

import requests
import json
import sys

print('Welcome to UPG programme configuration!')
print('***** All Environments *****:')
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

# getting access token by login
login_json = requests.post(f'{base_url}/upg-auth/api/v1/account/login',
                          data = credential)

if login_json.status_code == 200:
    print('Success! Logged in successfully!!')
    # deserialize a JSON formatted string into a Python object
    login_data = json.loads(login_json.content)

    access_token = login_data['result']['access_token']

    # Fetch program and cohort data in a single API call
    program_data = requests.get(f'{base_url}/upg-participant-selection/api/v1/program',
                                headers={'Authorization': f"Bearer {access_token}"})
    program_info = json.loads(program_data.content)
    all_program_set = program_info['resultset']
    all_program = []
    for programme in all_program_set:
        if programme['is_active']:
            all_program.append(programme)

    # Initialize program dictionary
    program_dictionary = []

    # Iterate over programs
    for index, program in enumerate(all_program):
        if program['is_active']:
            # Initialize cohorts list for each program
            cohorts_data = []
            # Fetch cohorts data for the current program
            cohorts_of_program_json = requests.get(
                f'{base_url}/upg-participant-selection/api/v1/cohort/{program["id"]}',
                headers={'Authorization': f"Bearer {access_token}"})
            cohorts_of_program_info = json.loads(cohorts_of_program_json.content)
            cohorts_values = cohorts_of_program_info['resultset']
            # Iterate over cohorts of the program
            cohort_serial = 0
            for single_cohort in cohorts_values:
                if single_cohort['is_active']:
                    cohort_serial += 1
                    cohorts_data.append({
                        'cohort_serial': cohort_serial,
                        'cohort_name': single_cohort['cohort'],
                        'cohort_id': single_cohort['id']
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

    if parent == child:
        print("Program & cohort of parent and child is similar, can't advance further.")
        sys.exit(5)

    child_program_name = selected_child_program_info['Program_name']
    child_program_id = selected_child_program_info['Program_id']
    child_cohort_name = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']

    parent_program_name = selected_parent_program_info['Program_name']
    parent_program_id = selected_parent_program_info['Program_id']
    parent_cohort_name = selected_parent_cohort_info['cohort_name']
    parent_cohort_id = selected_parent_cohort_info['cohort_id']

    """main code starts here"""
    """delete child's existing action plan type"""
    # we are using db to delete child data
    child_current_action_plan_type_json = requests.get(
        f'{base_url}/upg-enrollment/api/v1/action-plan/type/by-cohort/{child_cohort_id}',
        headers={'Authorization': f"Bearer {access_token}"})
    child_current_action_plan_type_info = json.loads(child_current_action_plan_type_json.content)

    if 'resultset' in child_current_action_plan_type_info:
        child_current_action_plan_type = child_current_action_plan_type_info['resultset']
        child_current_action_plan_type_length = len(child_current_action_plan_type)
        print("No of action plan type(child): ", child_current_action_plan_type_length)

        current_deleted_action_plan_type = 0
        for action_plan_type in child_current_action_plan_type:
            action_plan_type_id = action_plan_type['id']
            delete_current_hierarchy_request_json = requests.delete(
                f'{base_url}/upg-enrollment/api/v1/action-plan/type/delete/{action_plan_type_id}/cohortId/{child_cohort_id}',
                headers={'Authorization': f"Bearer {access_token}"})
            delete_current_action_plan_type_request = json.loads(delete_current_hierarchy_request_json.content)
            # print(f"check: {action_plan_type_id}")
            if 'status' in delete_current_action_plan_type_request:
                if delete_current_action_plan_type_request['status'] == "ok":
                    current_deleted_action_plan_type += 1
            else:
                print(f"Error: Can't delete: id= {action_plan_type_id}")

        if child_current_action_plan_type_length == current_deleted_action_plan_type:
            print(f"All existing action plan type deleted. Total {current_deleted_action_plan_type} deleted.")
        else:
            print(f'{current_deleted_action_plan_type} out of {child_current_action_plan_type_length} action plan type has been deleted.')
            print(f"Go to mandatory instruction above & follow that.")
            sys.exit(10)
    else:
        print('Sorry,' + ' ' + child_current_action_plan_type_info['message'])


    """fetching data from existing cohort to update our expected cohort"""
    parent_cohort_id = selected_parent_cohort_info['cohort_id']

    parent_action_plan_type_json = requests.get(
        f"{base_url}/upg-enrollment/api/v1/action-plan/type/by-cohort/{parent_cohort_id}",
        headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    parent_action_plan_type_info = json.loads(parent_action_plan_type_json.content)
    # print(parent_action_plan_type_info)

    # hierarchy_info_length & success compare & check if all data loaded successfully
    parent_action_plan_type_info_length = len(parent_action_plan_type_info['resultset'])
    print("Total action plan type (parent): ", parent_action_plan_type_info_length)
    action_plan_type_updated = 0

    """need to update cohort_id & program_id"""
    print('Updating info, please wait...')
    for single_action_plan_type in parent_action_plan_type_info['resultset']:
        data = {
            "action_plan_types": [
                {
                    "action_plan_name": single_action_plan_type["action_plan_name"],
                    "action_plan_type_tag": single_action_plan_type["action_plan_type_tag"],
                    "cohort_id": child_cohort_id
                }
            ]
        }

        """adding designation hierarchy in child program"""
        child_action_plan_type_update_request = requests.post(
            f"{base_url}/upg-enrollment/api/v1/action-plan/type/add",
            json=data, headers={'Authorization': f"Bearer {access_token}"})

        if child_action_plan_type_update_request.status_code == 200:
            action_plan_type_updated += 1
        else:
            print(f"Error: Cant update: {data}")

    if parent_action_plan_type_info_length == action_plan_type_updated:
        print(f'Everything updated! {action_plan_type_updated} out of {parent_action_plan_type_info_length}')
    else:
        print(f'{action_plan_type_updated} data updated out of {parent_action_plan_type_info_length}')

else:
    print('Error: Login failed. Try with correct credentials')

