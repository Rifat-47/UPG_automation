"""mandatory: material setup is the pre-requirement before adding group visit setup and should be same for good result"""
"""Just select the program and cohort of source program and target program, you are good to go"""
"""Remember, Parent refers to source program and child refers to target program"""

import requests
import json
import sys

print('Welcome to UPG programme configuration!')
print('***** All Programs *****:')
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

    """stars here"""
    """fetching all group visit topics data"""
    all_group_visit_topic_json = requests.get(
        f'{base_url}/upg-enrollment/api/v1/group-visit/material/all',
        headers={'Authorization': f"Bearer {access_token}"})

    all_group_visit_topic_data = json.loads(all_group_visit_topic_json.content)
    all_group_visit_topic_info = all_group_visit_topic_data['resultset']

    print('All group visit topics length: ', len(all_group_visit_topic_info))

    current_child_group_visit_topics = []
    parent_group_visit_topics = []

    child_program_name = selected_child_program_info['Program_name']
    child_program_id = selected_child_program_info['Program_id']
    child_cohort_name = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']

    parent_program_name = selected_parent_program_info['Program_name']
    parent_program_id = selected_parent_program_info['Program_id']
    parent_cohort_name = selected_parent_cohort_info['cohort_name']
    parent_cohort_id = selected_parent_cohort_info['cohort_id']
    
    for group_visit_topic in all_group_visit_topic_info:
        if group_visit_topic["cohort_id"] == child_cohort_id:
            current_child_group_visit_topics.append(group_visit_topic)
        if group_visit_topic["cohort_id"] == parent_cohort_id:
            parent_group_visit_topics.append(group_visit_topic)

    print('Parent group visit topics length: ', len(parent_group_visit_topics))
    print('Current child group visit topics length: ', len(current_child_group_visit_topics))

    """fetching all materials"""
    parent_materials_dic = {}
    child_materials_dic = {}
    all_materials_json = requests.get(f'{base_url}/upg-enrollment/api/v1/materials/all',
                                      headers={'Authorization': f"Bearer {access_token}"})
    all_materials_data = json.loads(all_materials_json.content)
    all_materials_info = all_materials_data['resultset']
    for material in all_materials_info:
        if material["cohort_id"] == parent_cohort_id:
            parent_materials_dic[material["id"]] = material["file"]
        if material["cohort_id"] == child_cohort_id:
            child_materials_dic[material["id"]] = material["file"]

    print("Parent material dic length: ", len(parent_materials_dic))
    print("Child material dic length: ", len(child_materials_dic))
    if len(parent_materials_dic) != len(child_materials_dic):
        print(f"Warning: Parent & child materials are not same.")

    result_materials_map = {}
    result_material_map_error = []
    child_materials_dic_copy = child_materials_dic.copy()
    for key_a, value_a in parent_materials_dic.items():
        for key_b, value_b in list(child_materials_dic_copy.items()):
            if value_a == value_b:
                result_materials_map[key_a] = key_b
                del child_materials_dic_copy[key_b]  # Delete the matched entry from 'b_copy' to prevent ambiguity
                break
        else:
            result_material_map_error.append(key_a)

    if len(result_material_map_error) > 0:
        print("Error: Material map error id's: ")
        for error in result_material_map_error:
            print(f"Error: No match is found for '{key_a}'")
        print("Parent & child materials aren't fully mapped. Check parent & child materials."
              "Even, if wanna to proceed, comment out the next line 'sys.exit(1)' & run again.")
        sys.exit(1)

    # print(result_materials_map)

    """delete child's existing group visit topics"""
    child_deleted_group_visit = 0
    for group_visit in current_child_group_visit_topics:
        cohort_id = selected_child_cohort_info['cohort_id']
        material_id = group_visit['id']
        visit_number = group_visit["visit_number"]
        visit_id = group_visit['id']
        delete_material_request_json = requests.delete(
            f"{base_url}/upg-enrollment/api/v1/group-visit/material?cohort_id={cohort_id}&visit_number={visit_number}&id={visit_id}",
            headers={'Authorization': f"Bearer {access_token}"})
        delete_material_request = json.loads(delete_material_request_json.content)
        # print(delete_material_request)
        if delete_material_request['result']['is_success']:
            child_deleted_group_visit += 1
        else:
            print(f"Error: Can't delete group visit topic, cohort={child_cohort_id}, visit no={visit_number}, id={visit_id}")

    if len(current_child_group_visit_topics) == child_deleted_group_visit:
        print(f"All existing topics setup deleted. Total {child_deleted_group_visit} deleted.")
    else:
        print(
            f'{child_deleted_group_visit} out of {len(current_child_group_visit_topics)} topic setup has been deleted.')

    # sys.exit(3)

    """adding material setup data"""
    print('Updating group visit topic setup, please wait...')

    child_group_visit_topic_updated = 0
    for group_visit in parent_group_visit_topics:
        if group_visit["materials_id"] is not None and group_visit["materials_id"] in result_materials_map:
            data = {
                "list": [
                    {
                        "cohort_id": child_cohort_id,
                        "visit_number": group_visit["visit_number"],
                        "materials_id": result_materials_map[group_visit["materials_id"]],
                        "topic": group_visit["topic"],
                        "attribute": group_visit["attribute"]
                    }
                ]
            }

            """adding group visit topic in child program"""
            child_group_visit_topic_update_request = requests.post(
                f'{base_url}/upg-enrollment/api/v1/group-visit/material',
                json=data, headers={'Authorization': f"Bearer {access_token}"})

            if child_group_visit_topic_update_request.status_code == 200:
                child_group_visit_topic_updated += 1
            else:
                print('Group visit topic update failed: ', data)
        else:
            print(f"Error: Material id is missing for visit number {group_visit["visit_number"]}")

    if len(parent_group_visit_topics) == child_group_visit_topic_updated:
        print(f'Everything updated! {child_group_visit_topic_updated} out of {len(parent_group_visit_topics)}')
    else:
        print(f'{child_group_visit_topic_updated} group visit topic data updated out of {len(parent_group_visit_topics)}')

else:
    print('Error: Login failed. Try with correct credentials')



# payload_data = {
#     "list":[
#         {
#             "cohort_id":"6a1325d4-07cc-4985-b7cc-c945c4f536fe",
#             "visit_number":1,
#             "materials_id":"7049613d-0b4b-4baf-aec6-f49b7f3a1f9b",
#             "topic":"পরিবার পরিকল্পনা (Family planning)",
#             "attribute":"পরিবার পরিকল্পনা (Family planning)"
#         }
#     ]
# }

# all = 'https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material/all'
#
# add = 'https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material'
#
# delete = f'https://upgapstg.brac.net/upg-enrollment/api/v1/group-visit/material?cohort_id={cohort_id}&visit_number={visit_number}&id={visit_id}'
