"""add pre-requisite setup & mapping(do manually) from one program to another program"""
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

    child_program_name = selected_child_program_info['Program_name']
    child_program_id = selected_child_program_info['Program_id']
    child_cohort_name = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']

    parent_program_name = selected_parent_program_info['Program_name']
    parent_program_id = selected_parent_program_info['Program_id']
    parent_cohort_name = selected_parent_cohort_info['cohort_name']
    parent_cohort_id = selected_parent_cohort_info['cohort_id']

    """fetch all existing pre requisite"""
    all_pre_requisite_json = requests.get(
        f'https://upgapstg.brac.net/upg-participant-selection/api/v1/prerequisite/get-all-prerequisite-setup',
        headers={'Authorization': f"Bearer {access_token}"})
    all_pre_requisite_data = json.loads(all_pre_requisite_json.content)
    all_pre_requisite_info = all_pre_requisite_data['resultset']

    parent_pre_requisite = []
    child_pre_requisite = []

    for pre_requisite in all_pre_requisite_info:
        if pre_requisite['cohort_id'] == child_cohort_id:
            child_pre_requisite.append(pre_requisite)
        if pre_requisite['cohort_id'] == parent_cohort_id:
            parent_pre_requisite.append(pre_requisite)

    print('Parent pre requisite: ', len(parent_pre_requisite))
    print('Current child pre requisite: ', len(child_pre_requisite))
    
    """delete child's existing pre requisite"""
    child_deleted_pre_requisite = 0
    for c_pre_requisite in child_pre_requisite:
        pre_requisite_id = c_pre_requisite['id']
        delete_pre_requisite_request_json = requests.delete(
            f"https://upgapstg.brac.net/upg-participant-selection/api/v1/prerequisite/delete-prerequisite/{child_cohort_id}/{pre_requisite_id}",
            headers={'Authorization': f"Bearer {access_token}"})
        delete_pre_requisite_request = json.loads(delete_pre_requisite_request_json.content)
        if delete_pre_requisite_request['status'] == 'ok':
            child_deleted_pre_requisite += 1

    if len(child_pre_requisite) == child_deleted_pre_requisite:
        print(f"All existing pre requisite deleted. Total {child_deleted_pre_requisite} deleted.")
    else:
        print(
            f'{child_deleted_pre_requisite} out of {len(child_pre_requisite)} pre requisite has been deleted.')

    """adding pre requisite setap data"""
    print('Updating pre requisite setup, please wait...')

    child_pre_requisite_updated = 0
    for p_pre_requisite in parent_pre_requisite:
        data = {
            "title": p_pre_requisite["title"],
            "cohort_id": child_cohort_id,
            "program_id": child_program_id,
            "cohort_name": child_cohort_name,
            "program_name": child_program_name,
            "descriptions": p_pre_requisite["descriptions"]
        }

        """adding material in child program"""
        child_pre_requisite_update_request = requests.post('https://upgapstg.brac.net/upg-participant-selection/api/v1/prerequisite/prerequisite',
                                                   json=data, headers={'Authorization': f"Bearer {access_token}"})

        if child_pre_requisite_update_request.status_code == 200:
            child_pre_requisite_updated += 1
        else:
            print(data)

    if len(parent_pre_requisite) == child_pre_requisite_updated:
        print(f'Everything updated! {child_pre_requisite_updated} out of {len(parent_pre_requisite)}')
    else:
        print(f'{child_pre_requisite_updated} data updated out of {len(parent_pre_requisite)}')

else:
    print('Login failed. Try with correct credentials')



# parent = {'a': '101', 'b': '102', 'c': '103'}
# child = {'a': '201', 'b': '202', 'c': '203'}
#
# # Create the final dictionary
# final = {parent[key]: child[key] for key in parent}
#
# print(final)