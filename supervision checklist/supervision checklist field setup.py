"""Complete"""
"""add supervision checklist setup from one program to another program"""
"""Remember, Parent refers to source program and child refers to target program"""
"""at first, action plan type setup is the pre-requirement for this task"""
"""Just select the program and cohort of source program and target program, you are good to go"""

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

    child_program_name = selected_child_program_info['Program_name']
    child_program_id = selected_child_program_info['Program_id']
    child_cohort_name = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']

    parent_program_name = selected_parent_program_info['Program_name']
    parent_program_id = selected_parent_program_info['Program_id']
    parent_cohort_name = selected_parent_cohort_info['cohort_name']
    parent_cohort_id = selected_parent_cohort_info['cohort_id']

    """main code stars here"""
    """fetch & delete existing child data"""
    child_supervision_checklist_json = requests.get(f'https://upgapstg.brac.net/upg-enrollment/api/v1/checklist/get-by-cohort/{child_cohort_id}',
                                                    headers={'Authorization': f"Bearer {access_token}"})
    child_supervision_checklist_data = json.loads(child_supervision_checklist_json.content)

    if 'resultset' in child_supervision_checklist_data:
        child_supervision_checklist_info = child_supervision_checklist_data['resultset']
        child_supervision_checklist_length = len(child_supervision_checklist_info)
        print('Total existing child checklist length: ', child_supervision_checklist_length)

        if child_supervision_checklist_length > 0:
            current_deleted_checklist = 0
            for child_checklist in child_supervision_checklist_info:
                action_plan_type_id = child_checklist["action_plan_type_id"]
                checklist_id = child_checklist['id']
                delete_current_checklist_request = requests.delete(f'https://upgapstg.brac.net/upg-enrollment/api/v1/checklist/delete/{checklist_id}/cohort-id/{child_cohort_id}/action-plan-type-id/{action_plan_type_id}',
                                                                   headers={'Authorization': f"Bearer {access_token}"})
                delete_current_checklist_data = json.loads(delete_current_checklist_request.content)
                if delete_current_checklist_data['status'] == 'ok':
                    current_deleted_checklist += 1

            if current_deleted_checklist == child_supervision_checklist_length:
                print(f'All existing checklist deleted. {current_deleted_checklist} out of {child_supervision_checklist_length} deleted.')
            else:
                print(f'{current_deleted_checklist} out of {child_supervision_checklist_length} supervision checklist is deleted')

    """fetch parent action plan type"""
    parent_action_plan_type_map = {}
    parent_action_plan_type_json = requests.get(f'https://upgapstg.brac.net/upg-enrollment/api/v1/action-plan/type/by-cohort/{parent_cohort_id}',
                                                headers={'Authorization': f"Bearer {access_token}"})
    parent_action_plan_type_data = json.loads(parent_action_plan_type_json.content)
    parent_action_plan_type_info = parent_action_plan_type_data["resultset"]
    for p_action_plan in parent_action_plan_type_info:
        parent_action_plan_type_map[p_action_plan["action_plan_name"]] = p_action_plan['id']

    """fetch child action plan type"""
    child_action_plan_type_map = {}
    child_action_plan_type_json = requests.get(f'https://upgapstg.brac.net/upg-enrollment/api/v1/action-plan/type/by-cohort/{child_cohort_id}',
                                               headers={'Authorization': f"Bearer {access_token}"})
    child_action_plan_type_data = json.loads(child_action_plan_type_json.content)
    child_action_plan_type_info = child_action_plan_type_data['resultset']
    for c_action_plan in child_action_plan_type_info:
        child_action_plan_type_map[c_action_plan['action_plan_name']] = c_action_plan['id']

    final_action_type_map = {parent_action_plan_type_map[key]: child_action_plan_type_map[key] for key in parent_action_plan_type_map}

    print(f'Parent action plan type length: ', len(parent_action_plan_type_map))
    print(f'Child action plan type length: ', len(child_action_plan_type_map))
    print(f'Finally mapped action plan length: ', len(final_action_type_map))

    """fetch parent supervision checklist"""
    parent_supervision_checklist_json = requests.get(
        f'https://upgapstg.brac.net/upg-enrollment/api/v1/checklist/get-by-cohort/{parent_cohort_id}',
        headers={'Authorization': f"Bearer {access_token}"})
    parent_supervision_checklist_data = json.loads(parent_supervision_checklist_json.content)

    parent_supervision_checklist_length = 0
    child_supervision_checklist_updated = 0
    if 'resultset' in parent_supervision_checklist_data:
        parent_supervision_checklist_info = parent_supervision_checklist_data['resultset']
        parent_supervision_checklist_length = len(parent_supervision_checklist_info)
        print('Total existing Parent checklist length: ', parent_supervision_checklist_length)

        if parent_supervision_checklist_length > 0:
            print('Updating supervision checklist field setup, please wait...')
            for parent_checklist in parent_supervision_checklist_info:
                data = {
                    "list": [
                        {
                            "cohort_id": child_cohort_id,
                            "form_id": parent_checklist["form_id"],
                            "action_plan_type_id": final_action_type_map[parent_checklist["action_plan_type_id"]],
                            "action_plan_type_name": parent_checklist["action_plan_type_name"],
                            "role_id": parent_checklist["role_id"],
                            "role_name": parent_checklist["role_name"],
                            "checklist": parent_checklist["checklist"]
                        }
                    ]
                }

                """adding supervision checklist in child program"""
                child_supervision_checklist_update_request = requests.post(f'https://upgapstg.brac.net/upg-enrollment/api/v1/checklist/submit',
                                json=data, headers={'Authorization': f"Bearer {access_token}"})
                if child_supervision_checklist_update_request.status_code == 200:
                    child_supervision_checklist_updated += 1
                else:
                    print(data)

    if parent_supervision_checklist_length == child_supervision_checklist_updated:
        print(f'Everything updated! {child_supervision_checklist_updated} out of {parent_supervision_checklist_length}')
    else:
        print(f'{child_supervision_checklist_updated} data updated out of {parent_supervision_checklist_length}')

else:
    print('Login failed. Try with correct credentials')

# -- DIUPG df90c5c9-7fb3-4633-99db-259b2ce82990
# -- LoadTest 6a1325d4-07cc-4985-b7cc-c945c4f536fe