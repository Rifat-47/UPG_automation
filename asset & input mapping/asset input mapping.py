"""add asset & input mapping from one program to another program"""
"""input category & input setup is the pre-requirement for this task, need same data for both prog"""
"""Just select the program and cohort of source program and target program, you are good to go"""
"""Remember, Parent refers to source program and child refers to target program"""
"""mandatory: input category must be same for child & parent program, it's better to have same inputs too"""

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

    """stars here"""
    """fetching all inputs data"""
    all_asset_input_mapping_json = requests.get(
        f"{base_url}/upg-participant-selection/api/v1/input/asset-input-mapping/all",
        headers={'Authorization': f"Bearer {access_token}"})

    all_asset_input_mapping_data = json.loads(all_asset_input_mapping_json.content)
    all_asset_input_mapping_info = all_asset_input_mapping_data['resultset']

    print('All asset & input mapping length: ', len(all_asset_input_mapping_info))

    current_child_asset_input_maps = []
    parent_asset_input_maps = []

    for single_asset_input_map in all_asset_input_mapping_info:
        if single_asset_input_map["cohort_id"] == child_cohort_id:
            current_child_asset_input_maps.append(single_asset_input_map)
        if single_asset_input_map["cohort_id"] == parent_cohort_id:
            parent_asset_input_maps.append(single_asset_input_map)

    print('Parent asset & input mapping length: ', len(parent_asset_input_maps))
    print('Current asset & input mapping length: ', len(current_child_asset_input_maps))

    """delete child's existing asset input mapping"""
    child_deleted_asset_input_map = 0
    for c_asset_input_map in current_child_asset_input_maps:
        asset_id = c_asset_input_map["asset_id"]
        map_id = c_asset_input_map['id']
        delete_input_request_json = requests.delete(
            f"{base_url}/upg-participant-selection/api/v1/input/asset-input-mapping/by-asset-id/{asset_id}/by-id/{map_id}",
            headers={'Authorization': f"Bearer {access_token}"})
        delete_input_request = json.loads(delete_input_request_json.content)
        if delete_input_request['result']['is_success']:
            child_deleted_asset_input_map += 1

    if len(current_child_asset_input_maps) == child_deleted_asset_input_map:
        print(f"All existing inputs deleted. Total {child_deleted_asset_input_map} deleted.")
    else:
        print(
            f'{child_deleted_asset_input_map} out of {len(current_child_asset_input_maps)} asset & input mapping has been deleted.')

    # sys.exit(3)

    """input category map for parent & child"""
    all_input_category_json = requests.get(
        f"{base_url}/upg-participant-selection/api/v1/input/get-all",
        headers={'Authorization': f"Bearer {access_token}"})

    all_input_category_data = json.loads(all_input_category_json.content)
    all_input_category_info = all_input_category_data['resultset']

    print('All input category length: ', len(all_input_category_info))

    current_child_input_category = {}
    parent_input_category = {}

    # print(selected_parent_program_info)
    parent_program_cohort = selected_parent_cohort_info['cohort_name']
    for inputx in all_input_category_info:
        if inputx["program_name"] == child_program_name and inputx['cohort_name'] == child_cohort_name:
            current_child_input_category[inputx["type"]] = inputx["id"]
        if inputx["program_name"] == parent_program_name and inputx['cohort_name'] == parent_program_cohort:
            parent_input_category[inputx["type"]] = inputx["id"]

    final_input_category_map = {parent_input_category[key]: current_child_input_category[key] for key in
                                parent_input_category}

    print('Parent input category: ', len(parent_input_category))
    print('Current child input category: ', len(current_child_input_category))
    print(f'Final input categry mapped: ', len(final_input_category_map))
    print('=============================')
    print(f'Final input categry mapped: ', final_input_category_map)
    print('=============================')
    """inputs map for parent & child"""
    all_inputs_json = requests.get(
        f"{base_url}/upg-participant-selection/api/v1/input/setup/all",
        headers={'Authorization': f"Bearer {access_token}"})

    all_inputs_data = json.loads(all_inputs_json.content)
    all_inputs_info = all_inputs_data['resultset']

    print('All inputs length', len(all_inputs_info))

    current_child_inputs_map = {}
    parent_inputs_map = {}

    current_child_inputs = []
    parent_inputs = []
    for inputx in all_inputs_info:
        if inputx["cohort_id"] == child_cohort_id:
            current_child_inputs.append(inputx)
            current_child_inputs_map[inputx["name"]] = inputx['id']
        if inputx["cohort_id"] == parent_cohort_id:
            parent_inputs.append(inputx)
            parent_inputs_map[inputx["name"]] = inputx['id']

    final_inputs_map = {parent_inputs_map[key]: current_child_inputs_map[key] for key in parent_inputs_map}
    
    print('Parent inputs: ', len(parent_inputs_map))
    print('Current child inputs: ', len(current_child_inputs_map))
    print(f'Final inputs mapped: ', len(final_inputs_map))

    # print(final_inputs_map)
    """adding asset & input mapping data"""
    print('Updating asset & input mapping setup, please wait...')
    child_asset_input_map_updated = 0
    for inputz in parent_asset_input_maps:
        # print(inputz)
        target_value = inputz.get("category_wise_input_name")
        # print('target value: ', target_value)

        for inputa in current_child_inputs:
            category_wise_input_id = ''
            if inputa["name"] == target_value and inputa["input_category_id"] == final_input_category_map[inputz["input_category_id"]]:
                category_wise_input_id = inputa["id"]

                data = {
                    "list": [{
                        "program_id": child_program_id,
                        "asset_id": inputz['asset_id'],
                        "cohort_id": child_cohort_id,
                        "input_category_id": final_input_category_map[inputz["input_category_id"]],
                        "category_wise_input_id": category_wise_input_id
                    }]
                }
                # sys.exit(10)

                """adding input map in child program"""
                child_asset_input_update_request = requests.post(
                    f'{base_url}/upg-participant-selection/api/v1/input/asset-input-mapping',
                    json=data, headers={'Authorization': f"Bearer {access_token}"})

                if child_asset_input_update_request.status_code == 200:
                    child_asset_input_map_updated += 1
                else:
                    print(data)
        # break

    if len(parent_asset_input_maps) == child_asset_input_map_updated:
        print(f'Everything updated! {child_asset_input_map_updated} out of {len(parent_asset_input_maps)}')
    else:
        print(f'{child_asset_input_map_updated} data updated out of {len(parent_asset_input_maps)}')

else:
    print('Login failed. Try with correct credentials')