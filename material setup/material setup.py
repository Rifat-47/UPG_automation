"""add material setup from one program to another program"""
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
    """fetching all materials data"""
    all_materials_json = requests.get(
        f"https://upgapstg.brac.net/upg-enrollment/api/v1/materials/all",
        headers={'Authorization': f"Bearer {access_token}"})

    all_materials_data = json.loads(all_materials_json.content)
    all_materials_info = all_materials_data['resultset']

    print('All material length', len(all_materials_info))

    current_child_materials = []
    parent_materials = []
    child_program_name = selected_child_program_info['Program_name']
    child_program_id = selected_child_program_info['Program_id']
    child_program_cohort = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']
    parent_program_name = selected_parent_program_info['Program_name']

    # print(selected_parent_program_info)
    parent_program_cohort = selected_parent_cohort_info['cohort_name']
    for material in all_materials_info:
        if material["program_name"] == child_program_name and material['cohort_name'] == child_program_cohort:
            current_child_materials.append(material)
        if material["program_name"] == parent_program_name and material['cohort_name'] == parent_program_cohort:
            parent_materials.append(material)

    print('Parent materials', len(parent_materials))
    print('Current child materials', len(current_child_materials))

    """delete child's existing materials"""
    child_deleted_material = 0
    for material in current_child_materials:
        cohort_id = selected_child_cohort_info['cohort_id']
        material_id = material['id']
        delete_material_request_json = requests.delete(f"https://upgapstg.brac.net/upg-enrollment/api/v1/materials/delete/{cohort_id}/{material_id}",
                                               headers={'Authorization': f"Bearer {access_token}"})
        delete_material_request = json.loads(delete_material_request_json.content)
        # print(delete_material_request)
        if delete_material_request['result']['is_success']:
            child_deleted_material += 1

    if len(current_child_materials) == child_deleted_material:
        print(f"All existing designation hierarchy deleted. Total {child_deleted_material} deleted.")
    else:
        print(
            f'{child_deleted_material} out of {len(current_child_materials)} materials has been deleted.')

    # sys.exit(3)

    """adding material setap data"""
    print('Updating material setup, please wait...')
    child_material_updated = 0
    for material in parent_materials:
        data = {
            "name": material["name"],
            "cohort_id": child_cohort_id,
            "program_id": child_program_id,
            "cohort_name": material["cohort_name"],
            "program_name": child_program_name,
            "description": material["description"],
            "file": material["file"]
        }

        """adding material in child program"""
        child_material_update_request = requests.post('https://upgapstg.brac.net/upg-enrollment/api/v1/materials/create',
                                                      json=data, headers={'Authorization': f"Bearer {access_token}"})

        if child_material_update_request.status_code == 200:
            child_material_updated += 1
        else:
            print(data)

    if len(parent_materials) == child_material_updated:
        print(f'Everything updated! {child_material_updated} out of {len(parent_materials)}')
    else:
        print(f'{child_material_updated} data updated out of {len(parent_materials)}')

else:
    print('Login failed. Try with correct credentials')