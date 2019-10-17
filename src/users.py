import os
import json
from datetime import datetime
from pdb import  set_trace

import pandas as pd
from boxsdk.exception import BoxAPIException


from src.Client import BoxClient
from src.groups import is_a_group, create_groups

box_client = BoxClient()
client = box_client.client

def get_users():
    users = client.users(user_type='all')
    for user in users:
        print('{0} (User ID: {1})'.format(user.name, user.id))

def search_user_by_email(login):
    users = client.users(filter_term=login)
    return users

def create_users(upload_method, file, group):

    group_id = None

    # If the group exists, get group id. If it doesn't create it.
    if is_a_group(group):
        groups = client.get_groups(group)
        for group in groups:
            group_id = group['id']
    else:
        user_input = input("The group %s doesn't exist. Would you like to create it (yes/no)?" % group)

        # user chose to create a new group
        if user_input == "yes":
            group_response = create_groups(group)
        # user chose NOT to create a new group. Break out of function
        elif user_input == "no":
            print("User chose not to create the group. No users were added your box account")
            return 0


    # Excel Handler
    if upload_method == 'excel':
        df = pd.read_excel(file)
        count = 0
        for row in df.itertuples():
            if count == 10:
                break

            create_user(row._1 + row._2, row.Email, group_id)
            count = count + 1

    # JSON Handler
    elif upload_method == 'json':
        with open(file) as json_file:
            data = json.load(json_file)

            for current_user in data:
                name = current_user['first_name'] + ' ' + current_user['last_name']
                email = current_user['email']
                create_user(name, email, group_id)

    # Create a failed report and export to Excel for any failed users
    if len(box_client.failed_user_uploads) != 0:
        failed_data_frame = pd.DataFrame(box_client.failed_user_uploads)
        path = ('%s/static/reports/failed_user_batch_%s.csv' % (os.getcwd(), box_client.client_created_time.strftime("%Y-%m-%dT%H:%M:%S%z")))
        failed_data_frame.to_csv(path_or_buf=path,header=['name', 'status', 'message'])

    print("Done adding users.")
    print("%s users failed to be uploaded. Check %s to see list users that failed to upload." % (len(box_client.failed_user_uploads), path))


def create_user(name, login, group_id):
    try:
        user = client.create_user(name, login)
        set_trace()

        if login != None:
            membership_response = client.group(group_id=group_id).add_member(user)

    # if an error is throw by the API, handle it by sending to failed_array
    # the most common error is that user already exists
    except BoxAPIException as e:
        print("ERROR Code: %s. %s: %s" % (e.status, e.message, login))
        print("Writing to Failed Inventory")

        failed_create_user_handler(login, e.status, e.message)

        # TODO: Implement Redis Q Implementation

    else:
        print("%s added!" % user)


def delete_all_users(force):
    users = client.users(user_type='all')

    for user in users:
        print('{0} (User ID: {1})'.format(user.name, user.id))
        client.user(user.id).delete(force=force)

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

def failed_create_user_handler(login, status, message):

    # set_trace()

    # if the user failed to be created, add it to a failed list.
    upload_row = [login, status, message]
    box_client.failed_user_uploads.append(upload_row)