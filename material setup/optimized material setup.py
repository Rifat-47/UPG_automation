import requests
import json
import sys

# Function to get access token
def get_access_token(email, password):
    response = requests.post('https://upgapstg.brac.net/upg-auth/api/v1/account/login',
                             data={"email": email, "password": password})
    if response.status_code == 200:
        return response.json()['result']['access_token']
    else:
        raise Exception('Login failed. Check your credentials.')


# Function to fetch programs and cohorts
def fetch_programs_and_cohorts(access_token):
    response = requests.get('https://upgapstg.brac.net/upg-participant-selection/api/v1/program',
                            headers={'Authorization': f"Bearer {access_token}"})
    programs = response.json()['resultset']

    program_dict = []
    for program in programs:
        if program['is_active']:
            cohorts_response = requests.get(
                f'https://upgapstg.brac.net/upg-participant-selection/api/v1/cohort/{program["id"]}',
                headers={'Authorization': f"Bearer {access_token}"})
            cohorts = cohorts_response.json()['resultset']
            active_cohorts = [
                {'cohort_serial': i + 1, 'cohort_name': cohort['cohort'], 'cohort_id': cohort['id']}
                for i, cohort in enumerate(cohorts) if cohort['is_active']
            ]
            program_dict.append({
                'Serial': len(program_dict) + 1,
                'Program_name': program['program_name'],
                'Program_id': program['id'],
                'Cohorts': active_cohorts
            })
    return program_dict


# Function to select a program and cohort
def select_program_and_cohort(program_dict, prompt):
    print(prompt)
    for program in program_dict:
        print(program['Serial'], program['Program_name'])
    selected_program_index = int(input('Select Program: ')) - 1
    selected_program = program_dict[selected_program_index]

    print(f"Select Cohort of {selected_program['Program_name']}:")
    for cohort in selected_program['Cohorts']:
        print(cohort['cohort_serial'], cohort['cohort_name'])
    selected_cohort_index = int(input('Select Cohort: ')) - 1
    selected_cohort = selected_program['Cohorts'][selected_cohort_index]

    return selected_program, selected_cohort


# Function to fetch all materials
def fetch_all_materials(access_token):
    response = requests.get(f"https://upgapstg.brac.net/upg-enrollment/api/v1/materials/all",
                            headers={'Authorization': f"Bearer {access_token}"})
    return response.json()['resultset']


# Function to delete materials
def delete_materials(materials, cohort_id, access_token):
    deleted_count = 0
    for material in materials:
        material_id = material['id']
        response = requests.delete(
            f"https://upgapstg.brac.net/upg-enrollment/api/v1/materials/delete/{cohort_id}/{material_id}",
            headers={'Authorization': f"Bearer {access_token}"})
        if response.json().get('result', {}).get('is_success'):
            deleted_count += 1
    return deleted_count


# Function to add materials
def add_materials(materials, cohort_id, program_id, access_token):
    updated_count = 0
    for material in materials:
        data = {
            "name": material["name"],
            "cohort_id": cohort_id,
            "program_id": program_id,
            "cohort_name": material["cohort_name"],
            "program_name": material["program_name"],
            "description": material["description"],
            "file": material["file"]
        }
        response = requests.post(
            'https://upgapstg.brac.net/upg-enrollment/api/v1/materials/create',
            json=data, headers={'Authorization': f"Bearer {access_token}"})
        if response.status_code == 200:
            updated_count += 1
    return updated_count


# Main script
try:
    access_token = get_access_token("admin@brac.net", "123456")
    print('Logged in successfully')

    program_dict = fetch_programs_and_cohorts(access_token)

    print('***** All Programs *****')
    parent_program, parent_cohort = select_program_and_cohort(program_dict, 'Select Parent Program and Cohort:')
    child_program, child_cohort = select_program_and_cohort(program_dict, 'Select Child Program and Cohort:')

    if (parent_program['Program_name'], parent_cohort['cohort_name']) == (
    child_program['Program_name'], child_cohort['cohort_name']):
        print("Program & cohort of parent and child are similar, can't proceed further.")
        sys.exit(1)

    all_materials = fetch_all_materials(access_token)

    parent_materials = [m for m in all_materials if
                        m["program_name"] == parent_program['Program_name'] and m['cohort_name'] == parent_cohort[
                            'cohort_name']]
    child_materials = [m for m in all_materials if
                       m["program_name"] == child_program['Program_name'] and m['cohort_name'] == child_cohort[
                           'cohort_name']]

    print(f'Parent materials: {len(parent_materials)}')
    print(f'Current child materials: {len(child_materials)}')

    deleted_materials_count = delete_materials(child_materials, child_cohort['cohort_id'], access_token)
    if len(child_materials) == deleted_materials_count:
        print(f"All existing materials deleted. Total {deleted_materials_count} deleted.")
    else:
        print(f"{deleted_materials_count} out of {len(child_materials)} materials have been deleted.")

    updated_materials_count = add_materials(parent_materials, child_cohort['cohort_id'], child_program['Program_id'],
                                            access_token)
    if len(parent_materials) == updated_materials_count:
        print(f'All materials updated! {updated_materials_count} out of {len(parent_materials)}')
    else:
        print(f'{updated_materials_count} materials updated out of {len(parent_materials)}')

except Exception as e:
    print(e)
    sys.exit(1)