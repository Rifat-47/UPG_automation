"""home visit steps question from one program to another program"""
"""Just select the program and cohort of source program and target program, you are good to go"""
"""NB: Home visit - steps config is a must for doing this task"""
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

        """deactivating the cohort"""
        # getting all cohorts of child program
        child_program_cohorts_request_json = requests.get(
            f"https://upgapstg.brac.net/upg-participant-selection/api/v1/cohort/{child_program_id}",
            headers={'Authorization': f"Bearer {access_token}"})
        child_program_cohorts_request_info = json.loads(child_program_cohorts_request_json.content)
        child_program_cohorts_data = child_program_cohorts_request_info['resultset']
        data_for_activate_deactivate_cohort = {}
        for child_cohort in child_program_cohorts_data:
            if child_cohort['id'] == child_cohort_id:
                del child_cohort['id']
                data_for_activate_deactivate_cohort = child_cohort
                break

        # deactivating child cohort info
        data_for_activate_deactivate_cohort['slNo'] = 1
        data_for_activate_deactivate_cohort['is_active'] = False
        deactivate_cohort_request_json = requests.patch(
            f"https://upgapstg.brac.net/upg-participant-selection/api/v1/cohort/update/{child_cohort_id}",
            json=data_for_activate_deactivate_cohort,
            headers={'Authorization': f"Bearer {access_token}"})
        deactivate_cohort_request = json.loads(deactivate_cohort_request_json.content)
        if not deactivate_cohort_request['result']['is_success']:
            print('Cohort is not deactivated, try again!')
            sys.exit(3)
        else:
            print('Cohort is deactivated...')


        """delete existing step question config"""
        all_steps_child_json = requests.get(
            f"https://upgapstg.brac.net/upg-enrollment/api/v1/home-visit/step/cohort/{child_cohort_id}",
            headers={'Authorization': f"Bearer {access_token}"})
        all_steps_child_info = json.loads(all_steps_child_json.content)
        all_steps_child_data = all_steps_child_info['resultset']
        for single_step in all_steps_child_data:
            """all question for single step"""
            child_step_id = single_step["id"]
            child_all_question_single_step_json = requests.get(
                f"https://upgapstg.brac.net/upg-enrollment/api/v1/home-visit/question/cohort/{child_cohort_id}/step/{child_step_id}",
                headers={'Authorization': f"Bearer {access_token}"})
            child_all_question_single_step_data = json.loads(child_all_question_single_step_json.content)['resultset']
            if len(child_all_question_single_step_data) > 0:
                single_question_deleted = 0
                for child_single_question in child_all_question_single_step_data:
                    question_id = child_single_question['id']
                    delete_question_request_json = requests.delete(
                        f"https://upgapstg.brac.net/upg-enrollment/api/v1/home-visit/question?cohort_id={child_cohort_id}&step_id={child_step_id}&id={question_id}",
                        headers={'Authorization': f"Bearer {access_token}"})
                    if delete_question_request_json.status_code == 200:
                        single_question_deleted += 1
                        # print('question deleted...')
                print(f"{single_question_deleted} out of {len(child_all_question_single_step_data)} question deleted for '{single_step['title']}'")
            else:
                print(f"Nothing to delete for '{single_step['title']}'")

        """activating the cohort again"""
        data_for_activate_deactivate_cohort['is_active'] = True
        activate_cohort_request_json = requests.patch(
            f"https://upgapstg.brac.net/upg-participant-selection/api/v1/cohort/update/{child_cohort_id}",
            json=data_for_activate_deactivate_cohort,
            headers={'Authorization': f"Bearer {access_token}"})
        activate_cohort_request = json.loads(activate_cohort_request_json.content)
        if not activate_cohort_request['result']['is_success']:
            print('Cohort is not activated, try again!')
            sys.exit(4)
        else:
            print('Cohort is activated...')

        """parent program starts here"""
        all_steps_parent_json = requests.get(
            f"https://upgapstg.brac.net/upg-enrollment/api/v1/home-visit/step/cohort/{parent_cohort_id}",
            headers={'Authorization': f"Bearer {access_token}"})
        all_steps_parent_info = json.loads(all_steps_parent_json.content)
        all_steps_parent_data = all_steps_parent_info['resultset']

        for single_step in all_steps_parent_data:
            """all question for single step"""
            parent_step_id = single_step["id"]
            all_question_single_step_json = requests.get(
                f"https://upgapstg.brac.net/upg-enrollment/api/v1/home-visit/question/cohort/{parent_cohort_id}/step/{parent_step_id}",
                headers={'Authorization': f"Bearer {access_token}"})
            all_question_single_step_data = json.loads(all_question_single_step_json.content)['resultset']
            # collecting home_visit_step_id
            home_visit_step_id = ''
            for single_child_step in all_steps_child_data:
                if single_child_step['title'] == single_step['title']:
                    home_visit_step_id = single_child_step['id']
                    break
            if home_visit_step_id == '':
                print(f'Step id not matched for {single_step['title']}')
                # break
                continue

            if len(all_question_single_step_data) > 0:
                new_question_added = 0
                for single_parent_question in all_question_single_step_data:
                    new_data = {
                        "home_visit_step_questions": [
                            {
                                "cohort_id": child_cohort_id,
                                "home_visit_step_id": home_visit_step_id,
                                "attribute": single_parent_question['attribute'],
                                "topic": single_parent_question['topic'],
                                "question": single_parent_question['question'],
                                "is_form_tagged": single_parent_question['is_form_tagged'],
                                "form_id": single_parent_question["form_id"],
                                "screen_name": single_parent_question["screen_name"]
                            }
                        ]
                    }
                    add_child_question_json = requests.post(
                        f"https://upgapstg.brac.net/upg-enrollment/api/v1/home-visit/question",
                        json=new_data, headers={'Authorization': f"Bearer {access_token}"})
                    if add_child_question_json.status_code == 200:
                        new_question_added += 1
                print(f'Total {new_question_added} out of {len(all_question_single_step_data)} question is added for {single_step['title']}')
            else:
                print(f'No question is available for {single_step['title']}.')
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

"""doc"""
cohort_id = ''
all_steps_of_program = f"https://upgapstg.brac.net/upg-enrollment/api/v1/home-visit/step/cohort/{cohort_id}"

step_id = ''
all_data_of_a_step = f"https://upgapstg.brac.net/upg-enrollment/api/v1/home-visit/question/cohort/{cohort_id}/step/{step_id}"

print('===================================================')