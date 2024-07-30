"""enterprise mapping from one program to another"""
"""mandatatory:
        enterprise category, group, get enterprise by category.
        enterprise category name, enterprise name must be similer for best result.
"""

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

    child_program_name = selected_child_program_info['Program_name']
    child_program_id = selected_child_program_info['Program_id']
    child_cohort_name = selected_child_cohort_info['cohort_name']
    child_cohort_id = selected_child_cohort_info['cohort_id']

    parent_program_name = selected_parent_program_info['Program_name']
    parent_program_id = selected_parent_program_info['Program_id']
    parent_cohort_name = selected_parent_cohort_info['cohort_name']
    parent_cohort_id = selected_parent_cohort_info['cohort_id']

    """stars here"""
    """fetching all enterprise mapping data"""
    all_enterprise_mapping_json = requests.get(f'https://upgapstg.brac.net/upg-participant-selection/api/v1/enterprise/group-wise-enterprise/all',
                                               headers={'Authorization': f"Bearer {access_token}"})
    all_enterprise_mapping_data = json.loads(all_enterprise_mapping_json.content)
    all_enterprise_mapping_info = all_enterprise_mapping_data['resultset']

    current_child_enterprise_map_list = []
    parent_enterprise_map_list = []
    for single_enterprise_map in all_enterprise_mapping_info:
        if single_enterprise_map['cohort_id'] == parent_cohort_id:
            parent_enterprise_map_list.append(single_enterprise_map)
        if single_enterprise_map['cohort_id'] == child_cohort_id:
            current_child_enterprise_map_list.append(single_enterprise_map)

    print("Current child enterprise mapping length: ", len(current_child_enterprise_map_list))
    print('Parent enterprise mapping length: ', len(parent_enterprise_map_list))

    """delete child's existing enterprise mapping"""
    print('Deleting existing enterprise mapping data, please wait...')
    child_deleted_enterprise_map = 0
    for c_enterprise_mapping in current_child_enterprise_map_list:
        enterprise_mapping_id = c_enterprise_mapping['id']
        delete_enterprise_mapping_json = requests.delete(
            f"https://upgapstg.brac.net/upg-participant-selection/api/v1/enterprise/group-wise-enterprise/delete/{enterprise_mapping_id}",
            headers={'Authorization': f"Bearer {access_token}"})
        delete_enterprise_mapping_request = json.loads(delete_enterprise_mapping_json.content)
        # print(delete_enterprise_mapping_request)
        if delete_enterprise_mapping_request['status'] == 'ok':
            child_deleted_enterprise_map += 1

    if len(current_child_enterprise_map_list) == child_deleted_enterprise_map:
        print(f"All existing inputs deleted. Total {child_deleted_enterprise_map} deleted.")
    else:
        print(
            f'{child_deleted_enterprise_map} out of {len(current_child_enterprise_map_list)} inputs has been deleted.')

    """child enterprise category"""
    child_enterprise_category = {}
    all_enterprise_category_json = requests.get(f'https://upgapstg.brac.net/upg-participant-selection/api/v1/enterprise-category/all',
                                                headers={'Authorization': f"Bearer {access_token}"})
    all_enterprise_category_data = json.loads(all_enterprise_category_json.content)
    for enterprise_category in all_enterprise_category_data['resultset']:
        if enterprise_category['cohort_id'] == child_cohort_id:
            child_enterprise_category[enterprise_category["name"]] = enterprise_category["id"]

    """child: get enterprises by category id"""
    # child_enterprise_category = {'category_name': 'id'}
    get_enterprise_by_category_map = {}
    for c_enterprise_category in child_enterprise_category:
        category_id = child_enterprise_category[c_enterprise_category]
        get_enterprise_by_category_json = requests.get(f'https://upgapstg.brac.net/upg-participant-selection/api/v1/enterprise/get-enterprise-by-category/{category_id}',
                                                       headers={'Authorization': f"Bearer {access_token}"})
        get_enterprise_by_category_data = json.loads(get_enterprise_by_category_json.content)['resultset']
        extra_dic = {}
        for x in get_enterprise_by_category_data:
            extra_dic[x["name"]] = x["id"]
        get_enterprise_by_category_map[c_enterprise_category] = extra_dic
    # print(get_enterprise_by_category_map)
        # break

    """child program groups"""
    child_all_groups_json = requests.get(f'https://upgapstg.brac.net/upg-participant-selection/api/v1/{child_cohort_id}/group',
                                         headers={'Authorization': f"Bearer {access_token}"})
    child_all_groups_data = json.loads(child_all_groups_json.content)
    child_all_groups_info = child_all_groups_data['resultset']

    """update enterprise mapping to child"""
    print('Updating enterprise mapping setup, please wait...')
    enterprise_mapping_updated = 0
    # print('get_enterprise_by_category_map: ', get_enterprise_by_category_map)

    for enterprise_map in parent_enterprise_map_list:
        category_name_key = ''
        if (enterprise_map["enterprise_category_name"]).endswith('.'):
            alert = enterprise_map["enterprise_category_name"]
            category_name_key = alert[:-1]
        else:
            category_name_key = enterprise_map["enterprise_category_name"]
        enterprise_category_id = child_enterprise_category.get(category_name_key)
        required_group = None
        for group in child_all_groups_info:
            if enterprise_map["group_name"].lower()[-1] == group["group"].lower()[-1]:
                required_group = group
                break

        all_enterprises = get_enterprise_by_category_map.get(category_name_key)
        if all_enterprises is None:
            print("None: ", enterprise_map["enterprise_category_name"])
        else:
            required_enterprise_id = all_enterprises.get(enterprise_map["enterprise_option_name"])

            data = {
                "id": None,
                "cohort_id": child_cohort_id,
                "program_id": child_program_id,
                "is_active": enterprise_map["is_active"],
                "cohort_name": child_cohort_name,
                "program_name": child_program_name,
                "enterprise_category_name": enterprise_map["enterprise_category_name"],
                "enterprise_option_name": enterprise_map["enterprise_option_name"],
                "grant_in_percentage": enterprise_map["grant_in_percentage"],
                "loan_in_percentage": enterprise_map["loan_in_percentage"],
                "budget": enterprise_map["given_budget"],
                "max_amount_of_main_asset": enterprise_map["max_amount_of_main_asset"],
                "max_amount_of_supporting_asset": enterprise_map["max_amount_of_supporting_asset"],
                "number_of_installment": required_group["no_of_installment"],
                "bi_weekly_install": enterprise_map["bi_weekly_install"],
                "enterprise_category_id": enterprise_category_id,
                "enterprise_id": required_enterprise_id,
                "group_id": required_group["id"],
                "group_name": required_group["group"],
            }
            # print(data)
            # break

            """adding enterprise mapping in child program"""
            child_enterprise_mapping_update_request = requests.post(
                'https://upgapstg.brac.net/upg-participant-selection/api/v1/enterprise/group-wise-enterprise/add',
                json=data, headers={'Authorization': f"Bearer {access_token}"})

            if child_enterprise_mapping_update_request.status_code == 200:
                enterprise_mapping_updated += 1
            else:
                print(data)

    if len(parent_enterprise_map_list) == enterprise_mapping_updated:
        print(f'Everything updated! {enterprise_mapping_updated} out of {len(parent_enterprise_map_list)}')
    else:
        print(f'{enterprise_mapping_updated} data updated out of {len(parent_enterprise_map_list)}')

else:
    print('Login failed. Try with correct credentials')
