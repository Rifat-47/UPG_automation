"""getting all sunmenu_name with menu_id"""

import requests
import json

login_json = requests.post('https://upgapstg.brac.net/upg-auth/api/v1/account/login',
                          data ={"email": "admin@brac.net","password": "123456"})

if login_json.status_code == 200:
    print('logged in successfully')

    # deserialize a JSON formatted string into a Python object
    login_data = json.loads(login_json.content)

    access_token = login_data['result']['access_token']

    """getting all roles of the program"""
    roles_json = requests.get("https://upgapstg.brac.net/upg-auth/api/v1/roles",
                              headers={'Authorization': f"Bearer {access_token}"})
    roles_data = json.loads(roles_json.content)
    roles_info = roles_data['resultset']
    # print(roles_info)

    """getting all app module of the program"""
    modules_json = requests.get("https://upgapstg.brac.net/upg-auth/api/v1/acl/menu",
                                headers={'Authorization': f"Bearer {access_token}"})
    modules_data = json.loads(modules_json.content)
    modules_info = modules_data['resultset']
    new_modules_info = []
    for i in modules_info:
        if not i['id'].startswith('w'):
            new_modules_info.append(i)

    for i in new_modules_info:
        print({i['menu_name']: i['id']})



    """getting all access control info of a user"""
    roleId = 'bfa7903a-c654-4473-adb8-9d1e908a4bc6'  # PO
    programId = '5a4772b9-83d2-4fcb-950f-7bd0006ce78c'  # DIUPG
    access_control_json = requests.get(f"https://upgapstg.brac.net/upg-auth/api/v1/roles/{roleId}/acl/program/{programId}",
                                       headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    access_control_info = json.loads(access_control_json.content)
    all_menu = access_control_info['resultset']

    menu_dic_list = []
    for single in all_menu:
        menu_name = single['menu_name']
        submenu_name = single['submenu_name']

        found = False
        for single_item in menu_dic_list:
            if menu_name in single_item:
                single_item[menu_name].append(submenu_name)
                found = True
                break
        if not found:
            menu_dic_list.append({menu_name: [submenu_name]})


payload_to_update = {
    'role_id': 'bfa7903a-c654-4473-adb8-9d1e908a4bc6',
    'role_name': 'PO',
    'program_id': '5a4772b9-83d2-4fcb-950f-7bd0006ce78c',
    'menu_id': 'm2',
    'menu_name': 'Participant Selection',
    'menu_order': 1,
    'submenu_id': 'sm4',
    'submenu_name': 'PRA & Questionnaire',
    'submenu_order': 1,
    'actions': {'create': False, 'get': False, 'remove': False, 'update': False},
    'is_active': True
}