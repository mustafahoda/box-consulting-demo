import os
import json
import datetime
import logging
import logging.config

from boxsdk import Client
from boxsdk import OAuth2

from src import users
from src import groups
from src import upload

#TODO: Delete
from pdb import set_trace


# Loads Config Data from config.json
with open('config/config.json') as json_file:
    data = json.load(json_file)
    app_config = data["app_config"]
    client_id = app_config["client_id"]
    client_secret = app_config["client_secret"]
    client_token = app_config["access_token"]
    as_users = app_config["as_users"]
    # log_config = data["logger_config"]


auth = OAuth2(
    client_id=client_id,
    client_secret=client_secret,
    access_token=client_token
)


# Loads Config Data from config.json
with open('config/config.json') as json_file:
    data = json.load(json_file)
    log_config = data["logger_config"]
    log_config['handlers']['file']['filename'] = '%s/static/reports/test.log' % (os.getcwd())

logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)


class BoxClient():
    def __init__(self):
        self.client = Client(auth)
        self.client_creator = self.client.user()
        self.client_created_time = datetime.datetime.now()
        self.as_users = as_users
        self.logger = logging.getLogger(__name__)

    # Common User Methods

    def get_users(self):
        return users.get_users(self.client)

    def get_user_by_email(self, login):
        return users.get_user_by_email(self.client, login)

    def create_users(self, upload_method, file, group_name, query):
        return users.create_users(upload_method, file, group_name, query)

    def delete_all_users(self, force):
        return users.delete_all_users(self.client, force)

    def delete_user(self, email, force):
        return users.delete_user(self.client, email, force)

    # Common Group Methods

    def create_group(self, group_name):
        return groups.create_groups(self.client, self.logger, group_name)

    def is_a_group(self, group_to_check):
        return groups.is_a_group(self.client, group_to_check)

    def get_group_id(self, group_name):
        return groups.get_group_id(self.client, group_name)

    # Common Upload Methods

    def upload_single_file(self, source, destination):
        return upload.upload_single_file(self.client, source, destination)