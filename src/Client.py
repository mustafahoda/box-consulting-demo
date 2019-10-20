import json
import datetime

from boxsdk import Client
from boxsdk import OAuth2


# Loads Config Data from config.json
with open('config/config.json') as json_file:
    data = json.load(json_file)
    app_config = data["app_config"]
    client_id = app_config["client_id"]
    client_secret = app_config["client_secret"]
    client_token = app_config["access_token"]
    as_users = app_config["as_users"]


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
        self.as_users = as_users
