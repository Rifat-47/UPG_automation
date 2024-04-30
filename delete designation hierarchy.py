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

    """ upg rural-2024 = cohort id: f1bd41d6-1bbe-4622-8b5d-d4598471ed59 """
    hierarchy_json = requests.get("https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy/f1bd41d6-1bbe-4622-8b5d-d4598471ed59",
                        headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    hierarchy_info = json.loads(hierarchy_json.content)

    # hierarchy_info_length & success compare & check if all data loaded successfully
    hierarchy_info_length = len(hierarchy_info['resultset'])

    for single_hierarchy in hierarchy_info['resultset']:
        print(single_hierarchy['id'])
        info = requests.delete(f"https://upgapstg.brac.net/upg-auth/api/v1/roles/hierarchy/{single_hierarchy['id']}",
                               headers={'Authorization': f"Bearer {access_token}"})
else:
    print("Login failed. Please check your credentials.")
