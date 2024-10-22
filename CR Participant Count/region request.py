"""send request for fetching data"""

import requests
import json

base_url = 'https://upgbd.brac.net'
credential = {"email": "admin@brac.net", "password": "12345@#"}
login_json = requests.post(f'{base_url}/upg-auth/api/v1/account/login',
                           data=credential)

if login_json.status_code == 200:
    print('Success! Logged in successfully!!')
    # deserialize a JSON formatted string into a Python object
    login_data = json.loads(login_json.content)

    access_token = login_data['result']['access_token']

    regions_id = [
        "252906aa-2624-465d-8bb7-32fded71a04c",
        "f0a780df-11ec-4dbf-805c-ea9e26ee2559",
    ]

    for regionID in regions_id:
        try:
            print(regionID)
            api_request = requests.get(
                f"{base_url}/upg-reports/api/v1/cr-report/home-and-group-visit-participant-count?cohort_id=e64173ea-09d7-4ddc-af63-3158e14ae3b2&filter_type=region&filter_values={regionID}&visit_numbers=10,21,34,47",
                headers={'Authorization': f"Bearer {access_token}"},
                timeout=400)  # Set the timeout to 60 seconds
            api_request.raise_for_status()  # Raise an exception for HTTP errors
            api_request_data = api_request.json()
            print({regionID: api_request_data})
        except:
            continue
