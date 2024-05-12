"""delete particular designation hierarchy of a cohort in a program"""

import requests
import json

"""{
            "id": "b7c0e60c-2e2c-4396-8d31-7389b67f0a85",
            "client_created_at": "1713991659",
            "client_updated_at": null,
            "cohort_id": "f1bd41d6-1bbe-4622-8b5d-d4598471ed59",
            "created_at": "2024-04-24T20:47:39.119Z",
            "created_by": "cac6aebd-d346-4112-ab7c-b2701f66d90e",
            "is_active": true,
            "level": "10",
            "parent_role_id": "f48e33a5-35fb-4b63-b39d-9d3126e071a8",
            "program_id": "69114ee1-4c0a-4e28-929d-a2c92b115a6e",
            "role_id": "d652a854-eee9-41ab-89ca-6d57d6684540",
            "updated_at": "2024-04-24T20:47:39.119Z",
            "updated_by": null,
            "role_name": "Director",
            "parent_role_name": "ADMIN",
            "cohort_name": "2024",
            "program_name": "UPG (Rural)"
        }"""

# getting access token by login
login_json = requests.post('https://upgapstg.brac.net/upg-auth/api/v1/account/login',
                          data ={"email": "admin@brac.net","password": "123456"})

def delete_hierarchy(option = 'all', value = ''):
    print(option, value)
    match_found = False
    for single_hierarchy in hierarchy_info['resultset']:
        # print(single_hierarchy['id'])
        if single_hierarchy[option] == value:
            info = requests.delete(f"https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy/{single_hierarchy['id']}",
                               headers={'Authorization': f"Bearer {access_token}"})
            if info.status_code == 200:
                print('Designation Hierarchy Deleted')
            else:
                print("Something went wrong while deleting the hierarchy.")
            match_found = True

    if not match_found:
        print("Doesn't match with your option & value")


if login_json.status_code == 200:
    print('logged in successfully')
    # deserialize a JSON formatted string into a Python object
    login_data = json.loads(login_json.content)

    access_token = login_data['result']['access_token']

    """ upg rural-2024 = cohort id: f1bd41d6-1bbe-4622-8b5d-d4598471ed59 """
    hierarchy_json = requests.get("https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy/f1bd41d6-1bbe-4622-8b5d-d4598471ed59",
                        headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    hierarchy_info = json.loads(hierarchy_json.content)

    # hierarchy_info_length & success compare & check if all data loaded successfully
    hierarchy_info_length = len(hierarchy_info['resultset'])

    options = {
        1 : 'all',
        2 : 'according to Designation',
        3 : 'according to Reports To',
        4 : 'according to Level'
    }

    while True:
        print("which heirarchy you want to delete?")
        for key, value in options.items():
            print(f"{key}: {value}")

        choice = int(input("enter your choice: "))
        if choice == 1:
            count = 0
            for single_hierarchy in hierarchy_info['resultset']:
                # print(single_hierarchy['id'])
                info = requests.delete(f"https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy/{single_hierarchy['id']}",
                                       headers={'Authorization': f"Bearer {access_token}"})
                if info.status_code == 200:
                    count += 1
            print(f"{count} data deleted.")
            break
        elif choice == 2:
            designation = input("Enter 'Designation': ")
            delete_hierarchy("role_name", designation)
            break
        elif choice == 3:
            designation = input("Enter 'Reports To': ")
            delete_hierarchy("parent_role_name", designation)
            break
        elif choice == 4:
            level = input("Enter 'Level': ")
            delete_hierarchy("level", level)
            break
        else:
            print("----------")
            print("Enter correct choice: ")
            continue
else:
    print("Login failed. Please check your credentials.")

