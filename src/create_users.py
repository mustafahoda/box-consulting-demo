import pandas as pd
from boxsdk import Client, OAuth2

from pdb import  set_trace

import json

with open('config.json') as json_file:
    data = json.load(json_file)
    client_id = data["client_id"]
    client_secret = data["client_secret"]
    client_token = data["access_token"]


auth = OAuth2(
    client_id=client_id,
    client_secret=client_secret,
    access_token=client_token
)

client = Client(auth)



def create_users(upload_method, file):

    # Excel Handler
    if upload_method == 'excel':
        df = pd.read_excel(file)

        for row in df.itertuples():
            print(row)
            additional_parameters = {}
            response = client.create_user(row._1 + row._2, row.Email)
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