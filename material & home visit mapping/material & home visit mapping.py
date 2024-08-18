"""add material & home visit mapping from one program to another program"""
"""Just select the program and cohort of source program and target program, you are good to go"""
"""Remember, Parent refers to source program and child refers to target program"""
"""NB: enterprise_category, enterprise, materials, home visit step id of parent & child program need to be same for proper material and 
home visit mapping"""

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
    """fetching all materials data"""
    all_material_home_visit_mapping_json = requests.get(
        f"{base_url}/upg-enrollment/api/v1/home-visit/step/material/all",
        headers={'Authorization': f"Bearer {access_token}"})

    all_material_home_visit_mapping_data = json.loads(all_material_home_visit_mapping_json.content)
    all_material_home_visit_mapping_info = all_material_home_visit_mapping_data['resultset']

    print('All material & home visit mapping length: ', len(all_material_home_visit_mapping_info))

    current_child_material_home_visit_mapping = []
    parent_material_home_visit_mapping = []

    for material in all_material_home_visit_mapping_info:
        if material["cohort_id"] == child_cohort_id:
            current_child_material_home_visit_mapping.append(material)
        if material["cohort_id"] == parent_cohort_id:
            parent_material_home_visit_mapping.append(material)

    print('Parent material & home visit mapping length: ', len(parent_material_home_visit_mapping))
    print('Current child material & home visit mapping length: ', len(current_child_material_home_visit_mapping))

    """delete child's existing data"""
    child_deleted_material_home_visit_mapping = 0
    print('Deleting existing data, please wait...')
    for child_material in current_child_material_home_visit_mapping:
        material_id = child_material['id']
        home_visit_step_id = child_material['home_visit_step_id']
        visit_number = child_material['visit_number']
        child_data_id = child_material['id']
        delete_material_home_visit_mapping_request_json = requests.delete(
            f"{base_url}/upg-enrollment/api/v1/home-visit/step/material?home_visit_step_id={home_visit_step_id}&visit_number={visit_number}&id={child_data_id}",
                headers={'Authorization': f"Bearer {access_token}"})
        delete_material_home_visit_mapping_request = json.loads(delete_material_home_visit_mapping_request_json.content)
        if delete_material_home_visit_mapping_request['result']['is_success']:
            child_deleted_material_home_visit_mapping += 1
        else:
            print(f"Error: Cant delete material, home visit step id: {home_visit_step_id}, visit no: {visit_number}, id: {child_data_id}")

    if len(current_child_material_home_visit_mapping) == child_deleted_material_home_visit_mapping:
        print(f"All existing material & home visit mapping deleted. Total {child_deleted_material_home_visit_mapping} deleted.")
    else:
        print(
            f'{child_deleted_material_home_visit_mapping} out of {len(current_child_material_home_visit_mapping)} material & home visit mapping has been deleted.')
    # sys.exit(3)

    """new code starts here"""
    # Function to get home visit steps for a cohort
    def get_home_visit_steps(cohort_id, access_token):
        response = requests.get(
            f"{base_url}/upg-enrollment/api/v1/home-visit/step/cohort/{cohort_id}",
            headers={'Authorization': f"Bearer {access_token}"}
        )
        # print(f'response code', response.status_code, response.text)
        if response.status_code == 200:
            return json.loads(response.content)['resultset']
        else:
            raise Exception(f"Failed to get home visit steps for cohort {cohort_id}: {response.text}")

    # Function to map parent steps to child steps
    def map_home_visit_steps(parent_steps, child_steps):
        step_mapping = {}
        for parent_step in parent_steps:
            for child_step in child_steps:
                if child_step['title'] == parent_step['title']:
                    step_mapping[parent_step['id']] = child_step['id']
                    break
        # print('Step map: ', step_mapping)
        print('------------------------')
        return step_mapping

    # Function to get enterprise categories for a cohort
    def get_enterprise_categories(cohort_id, access_token):
        response = requests.get(
            f"{base_url}/upg-participant-selection/api/v1/enterprise-category/all",
            headers={'Authorization': f"Bearer {access_token}"}
        )

        return_list= []
        if response.status_code == 200:
            response_data = json.loads(response.content)['resultset']
            for single_response in response_data:
                if single_response['cohort_id'] == cohort_id:
                    return_list.append(single_response)
            return return_list
        else:
            raise Exception(f"Failed to get home visit steps for cohort {cohort_id}: {response.text}")


    # Function to map parent enterprise categories to child enterprise categories
    def map_enterprise_categories(parent_enterprises, child_enterprises):
        enterprise_mapping = {}
        for parent_enterprise in parent_enterprises:
            for child_enterprise in child_enterprises:
                if child_enterprise["name"] == parent_enterprise["name"]:
                    enterprise_mapping[parent_enterprise['id']] = child_enterprise['id']
                    break
        # print("Enterprise mapping: ", enterprise_mapping)
        return enterprise_mapping


    # Function to get materials for a cohort
    def get_materials(cohort_id, access_token):
        response = requests.get(
            f"{base_url}/upg-enrollment/api/v1/materials/all",
            headers={'Authorization': f"Bearer {access_token}"}
        )

        material_list= []
        if response.status_code == 200:
            response_data = json.loads(response.content)['resultset']
            for single_response in response_data:
                if single_response['cohort_id'] == cohort_id:
                    material_list.append(single_response)
            return material_list
        else:
            raise Exception(f"Failed to get home visit steps for cohort {cohort_id}: {response.text}")

    # Function to map parent materials to child materials
    def map_materials(parent_materials, child_materials):
        material_mapping = {}
        for single_parent_material in parent_materials:
            for single_child_material in child_materials:
                if single_child_material["name"] == single_parent_material["name"]:
                    material_mapping[single_parent_material['id']] = single_child_material['id']
                    break
        return material_mapping

    try:
        parent_home_visit_step_data = get_home_visit_steps(parent_cohort_id, access_token)
        child_home_visit_step_data = get_home_visit_steps(child_cohort_id, access_token)

        parent_enterprise_categories = get_enterprise_categories(parent_cohort_id, access_token)
        child_enterprise_categories = get_enterprise_categories(child_cohort_id, access_token)

        parent_materials = get_materials(parent_cohort_id, access_token)
        child_materials = get_materials(child_cohort_id, access_token)
    except Exception as e:
        print(str(e))
        exit(1)

    # Map parent steps to child steps
    home_visit_step_mapping = map_home_visit_steps(parent_home_visit_step_data, child_home_visit_step_data)
    enterprise_category_mapping = map_enterprise_categories(parent_enterprise_categories, child_enterprise_categories)
    materials_mapping = map_materials(parent_materials, child_materials)

    """adding material setap data"""
    print('Updating material setup, please wait...')
    child_material_home_visit_mapping = 0
    count = 0
    for parent_material in parent_material_home_visit_mapping:
        parent_step_id = parent_material["home_visit_step_id"]
        # print('parent step id: ', parent_step_id)
        child_step_id = home_visit_step_mapping.get(parent_step_id)

        parent_enterprise_id = parent_material["enterprise_category_id"]
        child_enterprise_id = enterprise_category_mapping.get(parent_enterprise_id)

        parent_material_id = parent_material["materials_id"]
        child_material_id = materials_mapping.get(parent_material_id)
        # print(child_step_id, child_enterprise_id, child_material_id)
        if child_step_id and child_enterprise_id and child_material_id:
            data = {
                "list": [
                    {
                        "cohort_id": child_cohort_id,
                        "home_visit_step_id": child_step_id,
                        "visit_number": parent_material['visit_number'],
                        "enterprise_category_id": child_enterprise_id,
                        "materials_id": child_material_id,
                        "topic": parent_material['topic'],
                        "attribute": parent_material['attribute']
                    }
                ]
            }

            response = requests.post(
                f'{base_url}/upg-enrollment/api/v1/home-visit/step/material',
                json=data, headers={'Authorization': f"Bearer {access_token}"}
            )

            if response.status_code == 200:
                child_material_home_visit_mapping += 1
            else:
                print(f"Failed to update material: {response.text}")
                print(f"Update failed: {data}")

    if len(parent_material_home_visit_mapping) == child_material_home_visit_mapping:
        print(f'Everything updated! {child_material_home_visit_mapping} out of {len(parent_material_home_visit_mapping)}')
    else:
        print(f'{child_material_home_visit_mapping} data updated out of {len(parent_material_home_visit_mapping)}')

else:
    print('Error: Login failed. Try with correct credentials')