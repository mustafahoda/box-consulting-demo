import json

import pandas as pd
from pdb import  set_trace


from src.Client import BoxClient
from src.groups import is_a_group, create_groups

client = BoxClient().client

def create_users(upload_method, file, group):

    # If the group exists, get group id. If it doesn't create it.
    if is_a_group(group):
        groups = client.get_groups(group)
        for group in groups:
            group_id = group['id']
    else:
        group_response = create_groups(group)

    set_trace()

    # Excel Handler
    if upload_method == 'excel':
        df = pd.read_excel(file)

        for row in df.itertuples():
            user = client.create_user(row._1 + row._2, row.Email)
            membership_response = client.group(group_id=group_id).add_member(user)
            set_trace()


    # JSON Handler
    if upload_method == 'json':
        with open(file) as json_file:
            data = json.load(json_file)

            for current_user in data:
                name = current_user['first_name'] + ' ' + current_user['last_name']
                email = current_user['email']
                set_trace()
                response = client.create_user(name = name, login=email)
                set_trace()