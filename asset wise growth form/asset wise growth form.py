"""
get parent/child = https://upgapstg.brac.net/upg-participant-selection/api/v1/asset-wise-growth-form/cohort/6a1325d4-07cc-4985-b7cc-c945c4f536fe


add = https://upgapstg.brac.net/upg-participant-selection/api/v1/asset-wise-growth-form/create
data = {
    "cohort_id": "6a1325d4-07cc-4985-b7cc-c945c4f536fe",
    "asset_id": "86d00b1c-8bc3-44bc-947b-eaae5fb1ea3a",
    "form_id": "21048cb0-cfc4-11ee-a56e-6dc077383323",
    "form_name": "Agriculture_DIUPG_2023"
}

delete = https://upgapstg.brac.net/upg-participant-selection/api/v1/asset-wise-growth-form/delete?cohort_id=6a1325d4-07cc-4985-b7cc-c945c4f536fe&asset_id=77ffafd8-24fa-4007-9d1c-785bd684f0df&id=e34e2dc2-fcc3-4640-b0ed-e5662aa771e9
"""

"""add asset wise growth form one program to another program"""
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
    child_program_name = selected_child_program_info['Program_name']
    child_program_id = selected_child_program_info['Program_id']
    child_program_cohort = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']
    parent_program_name = selected_parent_program_info['Program_name']
    parent_cohort_id = selected_parent_cohort_info['cohort_id']
    # print(selected_parent_program_info)

    """fetch childs existing data"""
    child_current_asset_wise_growth_form_json = requests.get(
        f"https://upgapstg.brac.net/upg-participant-selection/api/v1/asset-wise-growth-form/cohort/{child_cohort_id}",
        headers={'Authorization': f"Bearer {access_token}"})

    child_current_asset_wise_growth_form_info = json.loads(child_current_asset_wise_growth_form_json.content)

    """delete child's existing inputs"""
    if 'resultset' in child_current_asset_wise_growth_form_info:
        child_current_asset_wise_growth_form = child_current_asset_wise_growth_form_info['resultset']
        child_current_asset_wise_growth_form_length = len(child_current_asset_wise_growth_form)
        print("No of designation hierarchy(child): ", child_current_asset_wise_growth_form_length)

        current_deleted_data = 0
        for child_current_data in child_current_asset_wise_growth_form:
            asset_id = child_current_data["asset_id"]
            id = child_current_data["id"]
            delete_current_asset_wise_growth_form_json = requests.delete(
                f'https://upgapstg.brac.net/upg-participant-selection/api/v1/asset-wise-growth-form/delete?cohort_id={child_cohort_id}&asset_id={asset_id}&id={id}',
                headers={'Authorization': f"Bearer {access_token}"})
            delete_current_hierarchy_request = json.loads(delete_current_asset_wise_growth_form_json.content)
            if delete_current_hierarchy_request['status'] == "ok":
                current_deleted_data += 1

        if child_current_asset_wise_growth_form_length == current_deleted_data:
            print(f"All existing asset wise growth form deleted. Total {current_deleted_data} deleted.")
        else:
            print(
                f'{current_deleted_data} out of {child_current_asset_wise_growth_form_length} asset wise growth form has been deleted.')
    else:
        print('Sorry,' + ' ' + child_current_asset_wise_growth_form_info['message'])

    """adding asset wise growth form data"""
    print('Updating asset wise growth form setup, please wait...')

    # fetching parent data
    parent_asset_wise_growth_form_json = requests.get(
        f"https://upgapstg.brac.net/upg-participant-selection/api/v1/asset-wise-growth-form/cohort/{parent_cohort_id}",
        headers={'Authorization': f"Bearer {access_token}"})

    parent_asset_wise_growth_form_info = json.loads(parent_asset_wise_growth_form_json.content)
    parent_asset_wise_growth_form_info_length = len(parent_asset_wise_growth_form_info['resultset'])
    print(f"Parent asset wise growth form length: ", parent_asset_wise_growth_form_info_length)

    child_data_updated = 0
    for parent_data in parent_asset_wise_growth_form_info['resultset']:
        data = {
            "cohort_id": child_cohort_id,
            "asset_id": parent_data['asset_id'],
            "form_id": parent_data["form_id"],
            "form_name": parent_data["form_name"]
        }

        """adding asset wise growth form in child program"""
        child_asset_wise_growth_form_update_request = requests.post(
            "https://upgapstg.brac.net/upg-participant-selection/api/v1/asset-wise-growth-form/create",
            json=data, headers={'Authorization': f"Bearer {access_token}"})

        if child_asset_wise_growth_form_update_request.status_code == 200:
            child_data_updated += 1
        else:
            print(data)

    if parent_asset_wise_growth_form_info_length == child_data_updated:
        print(f'Everything updated! {child_data_updated} out of {parent_asset_wise_growth_form_info_length}')
    else:
        print(f'{child_data_updated} data updated out of {parent_asset_wise_growth_form_info_length}')

else:
    print('Login failed. Try with correct credentials')