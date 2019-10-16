import json
from pdb import  set_trace

import pandas as pd
from boxsdk.exception import BoxAPIException


from src.Client import BoxClient
from src.groups import is_a_group, create_groups

client = BoxClient().client

def get_users():
    users = client.users(user_type='all')
    for user in users:
        print('{0} (User ID: {1})'.format(user.name, user.id))

def search_user_by_email(login):
    users = client.users(filter_term=login)
    return users

def create_users(upload_method, file, group):

    # If the group exists, get group id. If it doesn't create it.
    if is_a_group(group):
        groups = client.get_groups(group)
        for group in groups:
            group_id = group['id']
    else:
        user_input = input("The group %s doesn't exist. Would you like to craete it (yes/no)?" % group)

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

        for row in df.itertuples():
            set_trace()
            try:
                user = client.create_user(row._1 + row._2, row.Email)
                membership_response = client.group(group_id=group_id).add_member(user)


            # if an error is throw by the API, handle it by sending to Redis DLQ
            # the most common error is that user already exists
            except BoxAPIException as e:
                #TODO Implement Logging
                print("ERROR Code: %s. %s: %s" % (e.status, e.message, row.Email))

                # TODO: Implement Redis Q Implementation

    # JSON Handler
    if upload_method == 'json':
        with open(file) as json_file:
            data = json.load(json_file)

            for current_user in data:
                name = current_user['first_name'] + ' ' + current_user['last_name']
                email = current_user['email']
                response = client.create_user(name = name, login=email)

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