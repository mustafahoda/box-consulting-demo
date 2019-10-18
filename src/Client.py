from pdb import set_trace

import datetime
import json

from boxsdk import Client, OAuth2
from boxsdk import exception



# Loads Config Data from config.json
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


class BoxClient():
    def __init__(self):
        self.client = Client(auth)
        self.client_creator = self.client.user()
        self.client_created_time = datetime.datetime.now()
        self.failed_user_uploads = list()

        # try:
        #     self.connection_valid = self.client.get_current_enterprise()
        # except exception.BoxOAuthException:
        #     self.connection_valid = False
        # else:
        #     self.connection_valid = True
