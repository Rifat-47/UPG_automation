"""followup questionnaire setup from one program to another program"""
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

    """delete child's existing followup questionnaire"""
    child_cohort_id = selected_child_cohort_info['cohort_id']
    child_program_id = selected_child_program_info['Program_id']

    child_current_followup_questionnaire_json = requests.get(
        f'https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material-question/get-all-by-cohort/{child_cohort_id}',
        headers={'Authorization': f"Bearer {access_token}"})
    child_current_followup_questionnaire_info = json.loads(child_current_followup_questionnaire_json.content)

    if 'resultset' in child_current_followup_questionnaire_info:
        child_current_followup_questionnaire = child_current_followup_questionnaire_info['resultset']
        child_current_followup_questionnaire_length = len(child_current_followup_questionnaire)
        print("No of followup questionnaire (child): ", child_current_followup_questionnaire_length)

        current_deleted_questionnaire = 0
        for followup_questionnaire in child_current_followup_questionnaire:
            materials_id = followup_questionnaire['materials_id']
            followup_questionnaire_id = followup_questionnaire['id']
            delete_current_questionnaire_request_json = requests.delete(
                f'https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material-question/delete?cohort_id={child_cohort_id}&materials_id={materials_id}&id={followup_questionnaire_id}',
                headers={'Authorization': f"Bearer {access_token}"})
            delete_current_questionnaire_request = json.loads(delete_current_questionnaire_request_json.content)
            if delete_current_questionnaire_request['status'] == "ok":
                current_deleted_questionnaire += 1

        if child_current_followup_questionnaire_length == current_deleted_questionnaire:
            print(f"All existing followup questionnaire deleted. Total {current_deleted_questionnaire} deleted.")
        else:
            print(
                f'{current_deleted_questionnaire} out of {child_current_followup_questionnaire_length} followup questionnaire has been deleted.')
    else:
        print('Sorry,' + ' ' + child_current_followup_questionnaire_info['message'])

    """fetching data from existing cohort to update our expected cohort"""
    parent_cohort_id = selected_parent_cohort_info['cohort_id']

    parent_followup_questionnaire_json = requests.get(
        f"https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material-question/get-all-by-cohort//{parent_cohort_id}",
        headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    parent_followup_questionnaire_info = json.loads(parent_followup_questionnaire_json.content)
    # print(parent_hierarchy_info)

    # compare & check if all data loaded successfully
    parent_followup_questionnaire_info_length = len(parent_followup_questionnaire_info['resultset'])
    followup_questionnaire_updated = 0

    """need to update cohort_id & program_id"""
    print('Updating info, please wait...')
    for questionnaire in parent_followup_questionnaire_info['resultset']:
        data = {
            "list" : [
                {
                    'cohort_id': child_cohort_id,
                    'question': questionnaire['question'],
                    'materials_id': questionnaire['materials_id'],
                    'materials_topic': questionnaire['materials_topic'],
                }
            ]
        }

        """adding followup questionnaire in child program"""
        child_followup_questionnaire_update_request = requests.post(
            "https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material-question/add-material-questions",
            json=data, headers={'Authorization': f"Bearer {access_token}"})

        if child_followup_questionnaire_update_request.status_code == 200:
            followup_questionnaire_updated += 1
        else:
            print(data)

    if parent_followup_questionnaire_info_length == followup_questionnaire_updated:
        print(f'Everything updated! {followup_questionnaire_updated} out of {parent_followup_questionnaire_info_length}')
    else:
        print(f'{followup_questionnaire_updated} data updated out of {parent_followup_questionnaire_info_length}')

else:
    print('Login failed. Try with correct credentials')