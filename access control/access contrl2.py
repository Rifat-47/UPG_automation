"""getting all sunmenu_name with menu_id"""

import requests
import json

login_json = requests.post('https://upgapstg.brac.net/upg-auth/api/v1/account/login',
                          data ={"email": "admin@brac.net","password": "123456"})

if login_json.status_code == 200:
    print('logged in successfully')
    print('Printing submenu: ')
    # deserialize a JSON formatted string into a Python object
    login_data = json.loads(login_json.content)

    access_token = login_data['result']['access_token']

    access_control_json = requests.get("https://upgapstg.brac.net/upg-auth/api/v1/roles/bfa7903a-c654-4473-adb8-9d1e908a4bc6/acl/program/5a4772b9-83d2-4fcb-950f-7bd0006ce78c",
                                       headers={'Authorization': f"Bearer {access_token}"})

    # deserialize a JSON formatted string into a Python object
    access_control_info = json.loads(access_control_json.content)

    all_menu = access_control_info['resultset']
    submenu_name = []
    encountered_menus = set()
    for single_menu in all_menu:
        menu_key = (single_menu['submenu_name'], single_menu['submenu_id'])
        # if single_menu['menu_name'] not in menu_name:
        if menu_key not in encountered_menus:
            submenu_name.append({'name': single_menu['submenu_name'], 'menu-id': single_menu['submenu_id']})
            encountered_menus.add(menu_key)
            print({'name': single_menu['submenu_name'], 'menu-id': single_menu['submenu_id']})

    # print(menu_name)
    print(len(submenu_name))