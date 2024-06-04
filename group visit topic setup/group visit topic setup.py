"""adding group visit setup"""

"""material setup is required before adding group visit setup"""

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
    """fetching all group visit data"""
    all_group_visit_topic_json = requests.get(
        f'https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material/all',
        headers={'Authorization': f"Bearer {access_token}"})

    all_group_visit_topic_data = json.loads(all_group_visit_topic_json.content)
    all_group_visit_topic_info = all_group_visit_topic_data['resultset']

    print('All material length', len(all_group_visit_topic_info))

    current_child_group_visit_topics = []
    parent_group_visit_topics = []
    child_program_name = selected_child_program_info['Program_name']
    # child_program_id = selected_child_program_info['Program_id']
    child_program_cohort = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']
    parent_program_name = selected_parent_program_info['Program_name']

    # print(selected_parent_program_info)
    parent_program_cohort = selected_parent_cohort_info['cohort_name']
    for group_visit in all_group_visit_topic_info:
        if group_visit["program_name"] == child_program_name and group_visit['cohort_name'] == child_program_cohort:
            current_child_group_visit_topics.append(group_visit)
        if group_visit["program_name"] == parent_program_name and group_visit['cohort_name'] == parent_program_cohort:
            parent_group_visit_topics.append(group_visit)

    print('Parent group visit topics: ', len(parent_group_visit_topics))
    print('Current child group visit topics: ', len(current_child_group_visit_topics))

    """delete child's existing materials"""
    child_deleted_group_visit = 0
    for group_visit in current_child_group_visit_topics:
        cohort_id = selected_child_cohort_info['cohort_id']
        material_id = group_visit['id']
        visit_number = group_visit["visit_number"]
        visit_id = group_visit['id']
        delete_material_request_json = requests.delete(
            f"https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material?cohort_id={cohort_id}&visit_number={visit_number}&id={visit_id}",
            headers={'Authorization': f"Bearer {access_token}"})
        delete_material_request = json.loads(delete_material_request_json.content)
        # print(delete_material_request)
        if delete_material_request['result']['is_success']:
            child_deleted_group_visit += 1

    if len(current_child_group_visit_topics) == child_deleted_group_visit:
        print(f"All existing designation hierarchy deleted. Total {child_deleted_group_visit} deleted.")
    else:
        print(
            f'{child_deleted_group_visit} out of {len(current_child_group_visit_topics)} materials has been deleted.')

    # sys.exit(3)

    """adding material setap data"""
    print('Updating group visit topic setup, please wait...')

    child_group_visit_topic_updated = 0
    for group_visit in parent_group_visit_topics:
        data = {
            "list": [
                {
                    "cohort_id": child_cohort_id,
                    "visit_number": group_visit["visit_number"],
                    "materials_id": group_visit["materials_id"],
                    "topic": group_visit["topic"],
                    "attribute": group_visit["attribute"]
                }
            ]
        }

        """adding group visit topic in child program"""
        child_group_visit_topic_update_request = requests.post(
            'https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material',
            json=data, headers={'Authorization': f"Bearer {access_token}"})

        if child_group_visit_topic_update_request.status_code == 200:
            child_group_visit_topic_updated += 1
        else:
            print('Group visit topic update failed: ', data)

    if len(parent_group_visit_topics) == child_group_visit_topic_updated:
        print(f'Everything updated! {child_group_visit_topic_updated} out of {len(parent_group_visit_topics)}')
    else:
        print(f'{child_group_visit_topic_updated} group visit topic data updated out of {len(parent_group_visit_topics)}')

else:
    print('Login failed. Try with correct credentials')



payload_data = {
    "list":[
        {
            "cohort_id":"6a1325d4-07cc-4985-b7cc-c945c4f536fe",
            "visit_number":1,
            "materials_id":"7049613d-0b4b-4baf-aec6-f49b7f3a1f9b",
            "topic":"পরিবার পরিকল্পনা (Family planning)",
            "attribute":"পরিবার পরিকল্পনা (Family planning)"
        }
    ]
}

all = 'https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material/all'

add = 'https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material'

delete = f'https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material?cohort_id={cohort_id}&visit_number={visit_number}&id={visit_id}'
