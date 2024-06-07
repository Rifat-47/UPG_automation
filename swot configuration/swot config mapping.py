"""swot config mapping setup from one program to another program"""
"""Just select the program and cohort of source program and target program, you are good to go"""
"""Remember, Parent refers to source program and child refers to target program"""


import requests
import json
import sys
from datetime import datetime

# Start measuring execution time
starting_time = datetime.now()

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

    """child's existing data"""
    child_cohort_id = selected_child_cohort_info['cohort_id']
    child_program_id = selected_child_program_info['Program_id']

    # geeting child current data
    child_current_data_json = requests.get(
        f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/cohort/{child_cohort_id}',
        headers={'Authorization': f"Bearer {access_token}"})
    child_current_data_info = json.loads(child_current_data_json.content)
    print(f'fetched child data! total {len(child_current_data_info['resultset'])}!')

    """fetching data from parent cohort"""
    parent_cohort_id = selected_parent_cohort_info['cohort_id']
    parent_data_json = requests.get(
        f"https://upgapstg.brac.net/upg-enrollment/api/v1/swot/cohort/{parent_cohort_id}",
        headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    parent_data_info = json.loads(parent_data_json.content)
    print(f'fetched parent data! total {len(parent_data_info['resultset'])}!')

    print('data updating, please wait....')

    child_current_data = child_current_data_info['resultset']
    parent_current_data = parent_data_info['resultset']

    correct_data = 0
    child_data_updated = 0
    if 'resultset' in child_current_data_info:
        for child_data in child_current_data:
            matched = False
            for parent_data in parent_current_data:
                if child_data['swot_type_name'] == parent_data['swot_type_name'] and child_data['title'] == parent_data['title']:
                    matched = True
                    parent_data['counted'] = True
                    if child_data["is_activate"] != parent_data["is_activate"]:
                        data = {"title": child_data["title"], "is_activate": parent_data['is_activate']}
                        update_child_data_json = requests.patch(
                            f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/update/{child_data["id"]}/cohort/{child_data["cohort_id"]}/swot-type/{child_data['swot_type_id']}',
                            json=data, headers={'Authorization': f"Bearer {access_token}"})
                        if update_child_data_json.status_code == 200:
                            child_data_updated += 1
                    else:
                        correct_data += 1
                    break
            if not matched:
                data = {"title": child_data["title"], "is_activate": False}
                url = (f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/update/'
                       f'{child_data["id"]}/cohort/{child_data["cohort_id"]}/swot-type/{child_data["swot_type_id"]}')
                requests.patch(url, json=data, headers={'Authorization': f"Bearer {access_token}"})
        print('Total Child updated: ', child_data_updated)
    else:
        print(f'No previous child data for {child}')

    parent_all_swot_name_json = requests.get(
        f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/type/cohort/{parent_cohort_id}',
        headers={'Authorization': f"Bearer {access_token}"})
    parent_all_swot_name_data = json.loads(parent_all_swot_name_json.content)
    parent_all_swot_data = parent_all_swot_name_data['resultset']

    child_all_swot_name_json = requests.get(
        f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/type/cohort/{child_cohort_id}',
        headers={'Authorization': f"Bearer {access_token}"})
    child_all_swot_name_info = json.loads(child_all_swot_name_json.content)
    child_all_swot_data = child_all_swot_name_info["resultset"]

    if not len(parent_all_swot_data) == len(child_all_swot_data):
        print(
            'Number of swot name are different in parent and child. Please, match them manually & run the script again for mapping.')

    child_swot_dic = {}
    for swot_data in child_all_swot_data:
        child_swot_dic[swot_data["title"]] = swot_data["id"]
    # print(child_swot_dic)

    print('adding data, please wait...')
    added_data = 0
    for parent_data in parent_current_data:
        if not parent_data.get('counted') and parent_data['swot_type_name'] in child_swot_dic:
            swot_type_id = child_swot_dic[parent_data['swot_type_name']]
            data = {
                "swots": [{
                    "cohort_id": child_cohort_id,
                    "swot_type_id": swot_type_id,
                    "swot_type_name": parent_data['swot_type_name'],
                    "title": parent_data['title']
                }]
            }
            create_data_request_json = requests.post('https://upgapstg.brac.net/upg-enrollment/api/v1/swot/',json=data,
                headers={'Authorization': f"Bearer {access_token}"})
            if create_data_request_json.status_code == 200:
                added_data += 1
    print('Total newly added data:', added_data)
    print('All done...')
    total = correct_data + child_data_updated + added_data
    print('Finally: ', total)
else:
    print('Login failed. Try with correct credentials')


# End measuring execution time
ending_Time = datetime.now()
total_time = ending_Time - starting_time

# Extract minutes and seconds from the time difference
minutes = total_time.seconds // 60
seconds = total_time.seconds % 60

time_difference_str = f"{minutes}min {seconds}s"
print("Time taken:", time_difference_str)