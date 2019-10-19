import os
import json
import logging
# TODO Remove pdb import
from pdb import  set_trace

import pandas as pd
from boxsdk import exception

from src.Client import BoxClient
from src.groups import is_a_group, create_groups, get_group_id

box_client = BoxClient()
client = box_client.client


def get_users():

    users_dict = dict()
    users = client.users(user_type='all')

    for user in users:
        users_dict[user.id] = user.name

    return users_dict


def search_user_by_email(login):

    users = client.users(filter_term=login)
    return users


def create_users(upload_method, file, group_name):

    success_count = 0
    fail_count = 0

    group_id = get_group_id(group_name)

    # If the group doesn't exist, create it!
    if not group_id:
        user_input = input("The group %s doesn't exist. Would you like to create it (yes/no)?" % group_name)

        # user chose to create a new group
        if user_input == "yes":
            group_response = create_groups(group_name)
            print("Group %s created" % group_name)
        # user chose NOT to create a new group. Break out of function
        elif user_input == "no":
            print("User chose not to create the group. No users were added your box account")
            return 0


    # Excel Handler
    if upload_method == 'excel':
        # create a Pandas Dataframe to store Excel Data
        df = pd.read_excel(file)

        # Todo: is there a better way to iterate through DataFrame rows?
        for row in df.itertuples():
            create_user_response = create_user(row._1 + row._2, row.Email, group_id)

            if create_user_response: success_count += 1
            else: fail_count += 1

    # JSON Handler
    elif upload_method == 'json':
        with open(file) as json_file:
            data = json.load(json_file)

            for current_user in data:
                create_user_response = create_user(current_user['first_name'] + ' ' + current_user['last_name'], current_user['email'], group_id)

                if create_user_response: success_count  += 1
                else: fail_count += 1

    # TODO: Implement with Logging
    # Create a failed report and export to Excel for any failed users
    if len(box_client.reporting_list) != 0:
        failed_data_frame = pd.DataFrame(box_client.reporting_list)
        path = ('%s/static/reports/failed_user_batch_%s.csv' % (os.getcwd(), box_client.client_created_time.strftime("%Y-%m-%dT%H:%M:%S%z")))
        failed_data_frame.to_csv(path_or_buf=path,header=['name', 'status', 'message'])


    return {'success_count': success_count, 'fail_count': fail_count}


def create_user(name, login, group):

    success = False

    if name == None or login == None or group == None:   return success

    group_id = get_group_id(group)

    try:
        user = client.create_user(name, login)

        if login != None:
            membership_response = client.group(group_id=group_id).add_member(user)

    # if an error is throw by the API, handle it by sending to failed_array
    # the most common error is that user already exists
    except exception.BoxAPIException as e:

        # TODO: Fix with logs
        print("ERROR Code: %s. %s: %s" % (e.status, e.message, login))
        print("Writing to Failed Inventory")

        failed_reporting_list(login, e.status, e.message)
        return success

    else:
        logging.debug(f'{user} created')

        success = True
        return success


def delete_all_users(force):

    # TODO: Return something cleaner and fix in main app.py

    delete_count = 0
    users = client.users(user_type='all')

    for user in users:

        # if the current user is accessed, which is also the admin, don't delete it.
        if user == client.user().get(): continue

        delete_response = client.user(user.id).delete(force=force)
        if delete_response == True:
            logging.warning('Deleted: {0} (User ID: {1})'.format(user.name, user.id))
            delete_count += 1

    return delete_count

def delete_user(email, force):

    user_id = None

    # Retrieve a list of box users with that email address. Then assign the correct id
    users = search_user_by_email(email)

    for user in users:
        user_id = user.id

    # if unable to retrieve a user_id
    if user_id == None: return False

    delete_response = client.user(user_id).delete(force=force)
    return delete_response

def failed_reporting_list(login, status, message):

    # if the user failed to be created, add it to a failed list.
    upload_row = [login, status, message]
    box_client.failed_reporting_list.append(upload_row)

def success_reporting_list(login, status, message):

    # if the user is successfully created, add it to a success list.
    upload_row = [login, status, message]
    box_client.success_reporting_list.append(upload_row)

if __name__ == "__main__":
    create_user('LOL', 'asdfadsjf;lkafs@gmail.com', 'student')