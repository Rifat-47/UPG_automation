"""add designation hierarchy from one program to another program"""
"""parent and child programs are hard-coded here, need to change info while working with other program & cohorts"""

import requests
import json

# getting access token by login
login_json = requests.post('https://upgapstg.brac.net/upg-auth/api/v1/account/login',
                          data ={"email": "admin@brac.net","password": "123456"})

if login_json.status_code == 200:
    print('logged in successfully')
    # deserialize a JSON formatted string into a Python object
    login_data = json.loads(login_json.content)

    access_token = login_data['result']['access_token']

    """ diupg-2023 = cohort id: df90c5c9-7fb3-4633-99db-259b2ce82990 """
    """fetching data from existing cohort to update our expected cohort"""
    hierarchy_json = requests.get("https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy/df90c5c9-7fb3-4633-99db-259b2ce82990",
                        headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    hierarchy_info = json.loads(hierarchy_json.content)

    # hierarchy_info_length & success compare & check if all data loaded successfully
    hierarchy_info_length = len(hierarchy_info['resultset'])
    success = 0

    """need to update cohort_id & program_id"""
    for single_hierarchy in hierarchy_info['resultset']:
        data = [{
            'cohort_id': "f1bd41d6-1bbe-4622-8b5d-d4598471ed59", # upg rural-2024 = cohort id: f1bd41d6-1bbe-4622-8b5d-d4598471ed59
            'is_active': single_hierarchy['is_active'],
            'level': single_hierarchy['level'],
            'parent_role_id': single_hierarchy['parent_role_id'],
            'program_id': "69114ee1-4c0a-4e28-929d-a2c92b115a6e",
            'role_id': single_hierarchy['role_id'],
            'role_name': single_hierarchy['role_name'],
            'parent_role_name': single_hierarchy['parent_role_name']
        }]

        # serialize Python objects into a JSON formatted string
        json_body = json.dumps(data)

        """"""
        # info = requests.post("https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy", json= data, headers={'Authorization': f"Bearer {access_token}"})
        info = requests.post("https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy",
                             data= json_body,
                             headers= {'Authorization': f"Bearer {access_token}", 'Content-Type': 'application/json'})
        if info.status_code == 200:
            success += 1
        else:
            print(data)

    if hierarchy_info_length == success:
        print(f'everything updated! {success} out of {hierarchy_info_length}')
    else:
        print(f'{success} data updated out of {hierarchy_info_length}')

else:
    print("Login failed. Please check your credentials.")
