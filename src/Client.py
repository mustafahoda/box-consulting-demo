from pdb import set_trace

import datetime
import json

from boxsdk import Client, OAuth2
from boxsdk import exception



# Loads Config Data from config.json
with open('config.json') as json_file:
    data = json.load(json_file)
    app_config = data["app_config"]
    client_id = app_config["client_id"]
    client_secret = app_config["client_secret"]
    client_token = app_config["access_token"]


auth = OAuth2(
    client_id=client_id,
    client_secret=client_secret,
    access_token=client_token
)


class BoxClient():
    def __init__(self):
        self.client = Client(auth)
        self.client_creator = self.client.user()
        self.client_created_time = datetime.datetime.now()
        self.success_reporting_list = list()
        self.failed_reporting_list = list()