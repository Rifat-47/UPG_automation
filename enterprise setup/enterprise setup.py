"""Completed"""
"""add enterprise setup from one program to another program"""
"""Remember, Parent refers to source program and child refers to target program"""
"""mandatory, delete all enterprise option for child program, query is written in the sql query folder"""
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

    """main code stars here"""
    """fetching all materials data"""
    all_enterprise_json = requests.get(
        f"https://upgapstg.brac.net/upg-participant-selection/api/v1/enterprise/enterprise-wise-asset/all-enterprises",
        headers={'Authorization': f"Bearer {access_token}"})

    all_enterprise_data = json.loads(all_enterprise_json.content)
    all_enterprise_info = all_enterprise_data['resultset']

    print('All enterprise option length', len(all_enterprise_info))

    parent_enterprise = []
    child_program_name = selected_child_program_info['Program_name']
    child_program_id = selected_child_program_info['Program_id']
    child_cohort_name = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']

    parent_program_name = selected_parent_program_info['Program_name']
    parent_program_id = selected_parent_program_info['Program_id']
    parent_cohort_name = selected_parent_cohort_info['cohort_name']
    parent_cohort_id = selected_parent_cohort_info['cohort_id']

    for enterprise in all_enterprise_info:
        if enterprise["program_name"] == parent_program_name and enterprise['cohort_name'] == parent_cohort_name:
            parent_enterprise.append(enterprise)

    print('Total Parent enterprise: ', len(parent_enterprise))

    """get enterprise category for both parent & child program by cohort_id"""
    all_enterprise_category_json = requests.get(
        f"https://upgapstg.brac.net/upg-participant-selection/api/v1/enterprise-category/all",
        headers={'Authorization': f"Bearer {access_token}"})

    all_enterprise_category_data = json.loads(all_enterprise_category_json.content)
    all_enterprise_category_info = all_enterprise_category_data['resultset']

    parent_category_map = {}
    child_category_map = {}
    for enterprise_category in all_enterprise_category_info:
        if enterprise_category['cohort_id'] == child_cohort_id:
            # child_enterprise_category.append({enterprise_category['name']: enterprise_category['id']})
            child_category_map[enterprise_category['name']] = enterprise_category['id']
        if enterprise_category['cohort_id'] == parent_cohort_id:
            # parent_enterprise_category.append({enterprise_category['id']: enterprise_category['name']})
            parent_category_map[enterprise_category['id']] = enterprise_category['name']

    """adding material setap data"""
    print('Updating material setup, please wait...')
    child_enterprise_updated = 0

    for enterprise in parent_enterprise:
        category_id = enterprise['category_id']
        category_name = parent_category_map.get(category_id, '')
        child_category_id = child_category_map.get(category_name, '')

        assets = []
        all_assets = enterprise["assets"]
        for asset in all_assets:
            assets.append({
                "asset_name": asset["name"],
                "quantity": asset["quantity"],
                "asset_id": asset["asset_id"],
                "is_main_asset": asset["is_main_asset"]
            })

        data = {
            "name": enterprise['name'],
            "enterprise_code": enterprise["enterprise_code"],
            "cohort_id": child_cohort_id,
            "main_asset_quantity": enterprise["main_asset_quantity"],
            "supporting_asset_quantity": enterprise["supporting_asset_quantity"],
            "category_id": child_category_id,
            "main_asset_id": enterprise["main_asset_id"],
            "supporting_asset_id": enterprise["supporting_asset_id"],
            "assets": assets
        }

        # print(enterprise)
        # print(data)

        """adding enterprise in child program"""
        child_enterprise_update_request = requests.post('https://upgapstg.brac.net/upg-participant-selection/api/v1/enterprise/enterprise-wise-asset/create-enterprise-asset',
                                                      json=data, headers={'Authorization': f"Bearer {access_token}"})

        if child_enterprise_update_request.status_code == 201:
            child_enterprise_updated += 1
        else:
            print(data)

    if len(parent_enterprise) == child_enterprise_updated:
        print(f'Everything updated! {child_enterprise_updated} out of {len(parent_enterprise)}')
    else:
        print(f'{child_enterprise_updated} data updated out of {len(parent_enterprise)}')

else:
    print('Login failed. Try with correct credentials')