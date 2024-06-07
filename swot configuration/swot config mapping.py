"""swot config setup from one program to another program"""
"""Just select the program and cohort of source program and target program, you are good to go"""
"""Swot name and mapping will be done automatically."""
"""Remember, Parent refers to source program and child refers to target program"""

import requests
import json
import sys
from datetime import datetime

# Start measuring execution time
starting_time = datetime.now()

try:
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
            sys.exit(1)

        print('------------------------------------------------')

        child_cohort_id = selected_child_cohort_info['cohort_id']
        child_program_id = selected_child_program_info['Program_id']
        parent_cohort_id = selected_parent_cohort_info['cohort_id']

        # checking the number of swot name on parent and child programme
        parent_all_swot_name_json = requests.get(
            f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/type/cohort/{parent_cohort_id}',
            headers={'Authorization': f"Bearer {access_token}"})
        parent_all_swot_name_data = json.loads(parent_all_swot_name_json.content)
        parent_all_swot_data = parent_all_swot_name_data['resultset']

        child_all_swot_name_json = requests.get(
            f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/type/cohort/{child_cohort_id}',
            headers={'Authorization': f"Bearer {access_token}"})
        child_all_swot_name_info = json.loads(child_all_swot_name_json.content)

        child_correct_swot_name = 0
        child_updated_swot_name = 0
        child_deactivated_swot_name = 0

        if 'resultset' in child_all_swot_name_info:
            for child_swot_name in child_all_swot_name_info['resultset']:
                matched = False
                for parent_swot_name in parent_all_swot_data:
                    if child_swot_name['title'] == parent_swot_name['title']:
                        matched = True
                        parent_swot_name['checked'] = True
                        if child_swot_name["is_activate"] != parent_swot_name["is_activate"]:
                            data = {"title": child_swot_name["title"], "is_activate": parent_swot_name['is_activate']}
                            update_child_data_json = requests.patch(
                                f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/type/update/{child_swot_name["id"]}/cohort/{child_cohort_id}',
                                json=data, headers={'Authorization': f"Bearer {access_token}"})
                            if update_child_data_json.status_code == 200:
                                child_updated_swot_name += 1
                        else:
                            child_correct_swot_name += 1
                        break
                if not matched:
                    data = {"title": child_swot_name["title"], "is_activate": False}
                    deactivate_child_data_json = requests.patch(
                        f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/type/update/{child_swot_name['id']}/cohort/{child_cohort_id}',
                        json=data, headers={'Authorization': f"Bearer {access_token}"})
                    if deactivate_child_data_json.status_code == 200:
                        child_deactivated_swot_name += 1
            print('Total swot name matched with parent: ', child_correct_swot_name)
            print('Total swot name updated: ', child_updated_swot_name)
        else:
            print(f'No previous swot name data for {child}')

        print('Adding new swot name in child program, please wait...')
        child_added_swot_name = 0
        for parent_swot_name in parent_all_swot_data:
            if not parent_swot_name.get('checked'):
                data = {
                    "swot_types": [{
                        "cohort_id": child_cohort_id,
                        "title": parent_swot_name["title"]
                    }]
                }
                child_add_swot_name_json = requests.post(
                    f'https://upgapstg.brac.net//upg-enrollment/api/v1/swot/type',
                    json=data, headers={'Authorization': f"Bearer {access_token}"})
                if child_add_swot_name_json.status_code == 200:
                    child_added_swot_name += 1
        print('Total newly added data:', child_added_swot_name)
        total = child_correct_swot_name + child_updated_swot_name + child_added_swot_name
        print('Finally total swot name: ', total)

        print('-------------------------------------------------------')
        print('Swot name is updated, lets map the swot, please wait...')

        """child's existing data"""
        # geting child current data
        child_current_swot_map_data_json = requests.get(
            f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/cohort/{child_cohort_id}',
            headers={'Authorization': f"Bearer {access_token}"})
        child_current_swot_map_data_info = json.loads(child_current_swot_map_data_json.content)
        print(f'Fetched child swot map data! total {len(child_current_swot_map_data_info['resultset'])}!')

        """fetching data from parent cohort"""
        parent_swot_map_data_json = requests.get(
            f"https://upgapstg.brac.net/upg-enrollment/api/v1/swot/cohort/{parent_cohort_id}",
            headers={'Authorization': f"Bearer {access_token}"})

        # deserialize a JSON formatted string into a Python object
        parent_swot_map_data_info = json.loads(parent_swot_map_data_json.content)
        print(f'Fetched parent swot map data! total {len(parent_swot_map_data_info['resultset'])}!')

        print('Child swot map updating, please wait....')

        child_correct_swot_map = 0
        child_updated_swot_map = 0
        if 'resultset' in child_current_swot_map_data_info:
            for child_swot_map in child_current_swot_map_data_info['resultset']:
                matched = False
                for parent_swot_map in parent_swot_map_data_info['resultset']:
                    if child_swot_map['swot_type_name'] == parent_swot_map['swot_type_name'] and child_swot_map['title'] == parent_swot_map['title']:
                        matched = True
                        parent_swot_map['counted'] = True
                        if child_swot_map["is_activate"] != parent_swot_map["is_activate"]:
                            data = {"title": child_swot_map["title"], "is_activate": parent_swot_map['is_activate']}
                            update_child_data_json = requests.patch(
                                f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/update/{child_swot_map["id"]}/cohort/{child_swot_map["cohort_id"]}/swot-type/{child_swot_map['swot_type_id']}',
                                json=data, headers={'Authorization': f"Bearer {access_token}"})
                            if update_child_data_json.status_code == 200:
                                child_updated_swot_map += 1
                        else:
                            child_correct_swot_map += 1
                        break
                if not matched:
                    data = {"title": child_swot_map["title"], "is_activate": False}
                    url = (f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/update/'
                           f'{child_swot_map["id"]}/cohort/{child_swot_map["cohort_id"]}/swot-type/{child_swot_map["swot_type_id"]}')
                    requests.patch(url, json=data, headers={'Authorization': f"Bearer {access_token}"})
            print('Total swot map matched with parent: ', child_correct_swot_map)
            print('Total swot map updated: ', child_updated_swot_map)
        else:
            print(f'No previous child data for {child}')

        child_all_swot_name_json = requests.get(
            f'https://upgapstg.brac.net/upg-enrollment/api/v1/swot/type/cohort/{child_cohort_id}',
            headers={'Authorization': f"Bearer {access_token}"})
        child_all_swot_name_info = json.loads(child_all_swot_name_json.content)

        child_swot_name_dic = {}
        for swot_data in child_all_swot_name_info["resultset"]:
            child_swot_name_dic[swot_data["title"]] = swot_data["id"]
        # print(child_swot_name_dic)

        print('Adding new swot map in child program, please wait...')
        child_added_swot_map = 0
        for parent_swot_map in parent_swot_map_data_info['resultset']:
            if not parent_swot_map.get('counted') and parent_swot_map['swot_type_name'] in child_swot_name_dic:
                swot_type_id = child_swot_name_dic[parent_swot_map['swot_type_name']]
                data = {
                    "swots": [{
                        "cohort_id": child_cohort_id,
                        "swot_type_id": swot_type_id,
                        "swot_type_name": parent_swot_map['swot_type_name'],
                        "title": parent_swot_map['title']
                    }]
                }
                child_add_swot_map_request_json = requests.post('https://upgapstg.brac.net/upg-enrollment/api/v1/swot/',json=data,
                    headers={'Authorization': f"Bearer {access_token}"})
                if child_add_swot_map_request_json.status_code == 200:
                    child_added_swot_map += 1
        print('Total new swot map added: ', child_added_swot_map)
        total = child_correct_swot_map + child_updated_swot_map + child_added_swot_map
        print('Finally swot mapped: ', total)
    else:
        print('Login failed. Try with correct credentials')
except TimeoutError as e:
    if e.errno == 10060:
        print("It seems you are having an internet connection problem.")
    else:
        print(f"An unexpected error occurred: {e}")


# End measuring execution time
ending_Time = datetime.now()
total_time = ending_Time - starting_time

# Extract minutes and seconds from the time difference
minutes = total_time.seconds // 60
seconds = total_time.seconds % 60

time_difference_str = f"{minutes}min {seconds}s"
print("Time taken:", time_difference_str)