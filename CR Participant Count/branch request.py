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

    branches_id = [
        "4f719106-0a56-4ea0-8c4b-c69a94521e5e",
        "5fd239e9-4006-4d66-a014-d8bac244f781",
        "5373f8d1-23cf-4f5a-9e69-4ddcef4439a2",
        "00423b68-c1d2-4c13-847e-374c1dbc6885",
        "75611b6b-6a57-447e-8dcd-054bc14a1549",
        "b5fec398-82da-457c-8ad6-b41446710178",
        "be5fe4c6-a58c-4562-aa40-ba29d0aae7de",
        "cf1550f1-6c09-471b-957f-3273e9e08da1",
        "95badf44-4627-4d56-924b-0e291ab4515d",
        "bbcefc16-d05f-4810-ab59-30c0fccdbaa1",
        "0de10162-a694-428e-840f-3bdd3489b7ad",
        "439beef0-4688-4fd6-addb-3e7fd4b4c6fa",
        "3d074214-0621-4c89-a089-0df1c983b737",
        "0323a12e-a12e-49b8-91a4-bce0ea7b7fc0",
    ]

    for branch_id in branches_id:
        try:
            api_request = requests.get(
                f"{base_url}/upg-reports/api/v1/cr-report/home-and-group-visit-participant-count?cohort_id=e64173ea-09d7-4ddc-af63-3158e14ae3b2&filter_type=branch&filter_values={branch_id}&visit_numbers=10,21,34,47",
                headers={'Authorization': f"Bearer {access_token}"},
                timeout=30)  # Set the timeout to 60 seconds
            # url = f"{base_url}/upg-reports/api/v1/cr-report/home-and-group-visit-participant-count?cohort_id=e64173ea-09d7-4ddc-af63-3158e14ae3b2&filter_type=branch&filter_values={branch_id}&visit_numbers=10,21,34,47"
            api_request.raise_for_status()  # Raise an exception for HTTP errors
            api_request_data = api_request.json()
            print({branch_id: api_request_data})
        except:
            continue
