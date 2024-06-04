import requests
import json
import sys

# getting access token by login
login_json = requests.post('https://upgapstg.brac.net/upg-auth/api/v1/account/login',
                          data ={"email": "admin@brac.net","password": "123456"})

login_data = json.loads(login_json.content)
access_token = login_data['result']['access_token']

data = {
    "name": "NF- Home Visit 1",
    "cohort_id": "6a1325d4-07cc-4985-b7cc-c945c4f536fe",
    "program_id": "adf3afb1-9e95-4a46-b4b9-67d4eb6b11af",
    "cohort_name": "2023",
    "program_name": "Load Test",
    "description": "সুস্থ ও অসুস্থ গবাদিপশু ও হাঁস মুরগির চেনার উপায়/ক্ষুদ্র ব্যবসা কি? ক্ষুদ্র ব্যবসার সুবিধাসমূহ/নৌকা-জাল এন্টারপ্রাইজের সাথে সম্পর্কযুক্ত কিছু উপকরণের সঙ্গে পরিচিতি",
    "file": "https://upgapstg.brac.net/upg-files/api/v1/file-serve/d54eb626-f67d-408b-bcd1-891eab805a6d.pdf"
}

file_upload_request = requests.post(
            "https://upgapstg.brac.net/upg-enrollment/api/v1/materials/create",
            json=data, headers={'Authorization': f"Bearer {access_token}"})


program_info = json.loads(file_upload_request.content)
print(program_info)