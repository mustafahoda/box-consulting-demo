import os
import json
import datetime
import logging
import logging.config
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from boxsdk import Client, exception
from boxsdk import OAuth2

#TODO: Delete
from pdb import set_trace

# Loads Config Data from config.json
from src.DB import DB
# from src import threader

with open('config/config.json') as json_file:
    data = json.load(json_file)
    app_config = data["app_config"]
    client_id = app_config["client_id"]
    client_secret = app_config["client_secret"]
    client_token = app_config["access_token"]
    as_users = app_config["as_users"]
    # log_config = data["logger_config"]
    admins = data['app_config']['as_users']


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
        """
        Return a dictionary with users and their ids
        :return:
        """

        users_dict = dict()
        users = self.client.users(user_type='all')

        for user in users:
            users_dict[user.id] = user.name

        return users_dict

    def get_user_by_email(self, login):
        """
        Searches for a user by email and returns a Box User Object
        :param login:
        :return:
        """

        user = None
        users = self.client.users(filter_term=login)

        for user in users:
            if user.login == login:
                return user

        return user

    def create_users(self, upload_method, file, group_name, query):
        """
        Create users at scale

        :param upload_method:
        :param file:
        :param group_name:
        :return: a dictionary containing on how many users were created and how many failed to be created
        """

        success_count = 0
        fail_count = 0

        group_id = self.get_group_id(group_name)

        # If the group doesn't exist, create it.
        if not group_id:
            user_input = input("The group %s doesn't exist. Would you like to create it (yes/no)? " % group_name)

            if user_input == "yes":
                group_response = self.create_groups(logger, group_name)

                msg = "Group '%s' successfully created" % group_name
                logger.info(msg)

            elif user_input == "no":

                msg = "No users were added because user opted to not create a new group"
                logger.warning(msg)

                return {'success_count': success_count, 'fail_count': fail_count}

        # Excel Handler
        if upload_method == 'excel':
            # create a Pandas Dataframe to store Excel Data
            df = pd.read_excel(file)

            row_count = len(df)
            set_trace()

            if row_count > 10:
                payload = list()
                # generate payload

                for row in df.itertuples():
                    payload_tuple = (row._1 + ' ' + row._2, row.Email, group_name)
                    payload.append(payload_tuple)


                self.create_users_with_thread(payload)

            else:
                # Todo: is there a better way to iterate through DataFrame rows?
                for row in df.itertuples():
                    create_user_response = self.create_user(row._1 + row._2, row.Email, group_name)

                    if create_user_response:
                        success_count += 1
                    else:
                        fail_count += 1

        # JSON Handler
        elif upload_method == 'json':
            with open(file) as json_file:
                data = json.load(json_file)

                row_count = len(data)
                set_trace()

                if row_count > 10:
                    payload = list()
                    for current_user in data:
                        payload_tuple = (
                        current_user['first_name'] + ' ' + current_user['last_name'], current_user['email'], group_name)
                        payload.append(payload_tuple)

                        self.create_users_with_thread(payload)

                else:
                    for current_user in data:
                        create_user_response = self.create_user(current_user['first_name'] + ' ' + current_user['last_name'],
                                                           current_user['email'], group_name)

                        if create_user_response:
                            success_count += 1
                        else:
                            fail_count += 1

        # PostgreSQL Handler
        elif upload_method == 'db':

            db = DB()

            with db.conn.cursor() as cursor:
                cursor.execute(query)
                records = cursor.fetchall()

                num_rows = cursor.rowcount

                if num_rows > 10:
                    payload = list()
                    for row in records:
                        payload_tuple = (row[1] + row[2], row[3], group_name)
                        payload.append(payload_tuple)

                        self.create_users_with_thread(payload)


                else:
                    for row in records:
                        login = row[3]
                        create_user_response = self.create_user(row[1] + row[2], login, group_name)

                        if create_user_response:
                            success_count += 1
                        else:
                            fail_count += 1

        return {'success_count': success_count, 'fail_count': fail_count}

    def create_user(self, payload):

        """
        Creates a single user

        :param name: Name of the user
        :param login: what's the login for the user you are creating
        :param group_name: which group do you want the user to be assigned to
        :return:
        """


        # Payload Unpacking
        name = payload[0]
        login = payload[1]
        group_name = payload[2]

        success = False
        group_id = None

        if name == None or login == None:   return success

        if group_name == None:
            group_id = self.get_group_id(group_name)

        try:
            user = self.client.create_user(name, login)

            # TODO: Deal with this later
            if group_id != None:
                membership_response = self.client.group(group_id=group_id).add_member(user)

            # set_trace()

        # if an error is throw by the API, handle it by sending to failed_array
        # the most common error is that user already exists
        except exception.BoxAPIException as e:

            msg = "Status Code: %s. %s: <%s>" % (e.status, e.message, login)
            logger.error(msg)

            return success

        else:
            msg = "User was successfully created:  %s " % user
            logger.info(msg)

            success = True
            return success

    def delete_all_users(self, force):
        """
        Delete all users at scale. Can not be undone.

        :param force:
        :return:
        """

        success_count = 0
        fail_count = 0
        users = self.client.users(user_type='all')

        for user in users:
            # if the current user is accessed, which is also the admin, don't delete it.
            if user == self.client.user().get() or user.id in admins: continue

            delete_response = self.client.user(user.id).delete(force=force)

            if delete_response == True:
                msg = 'Deleted: {0} (User ID: {1})'.format(user.name, user.id)
                logger.info(msg)
                success_count += 1
            else:
                msg = 'Unable to delete user. %s : %s' % (user.id, user.login)
                logger.error(msg)
                fail_count += 1

        return {'success_count': success_count, 'fail_count': fail_count}

    def delete_user(self, email, force):
        """
        Delete a single user

        :param email:
        :param force:
        :return:
        """

        success = False

        user = self.get_user_by_email(email)
        if user == None: return success

        success = self.client.user(user.id).delete(force=force)

        if success:
            msg = 'Deleted: {0} (User ID: {1})'.format(user.name, user.id)
            logger.info(msg)

        else:
            msg = 'Unable to delete user. %s : %s' % (user.id, user.login)
            logger.error(msg)

        return success

    def generate_payload(self, upload_method, file, group_name, query):

        # Excel Handler
        if upload_method == 'excel':
            # create a Pandas Dataframe to store Excel Data
            df = pd.read_excel(file)

            row_count = len(df)

            if row_count > 10:
                payload = list()
                # generate payload

                for row in df.itertuples():
                    payload_tuple = (row._1 + ' ' + row._2, row.Email, group_name)
                    payload.append(payload_tuple)

                # self.create_users_with_thread(payload)

        # JSON Handler
        elif upload_method == 'json':
            with open(file) as json_file:
                data = json.load(json_file)

                row_count = len(data)

                if row_count > 10:
                    payload = list()
                    for current_user in data:
                        payload_tuple = (
                            current_user['first_name'] + ' ' + current_user['last_name'], current_user['email'],
                            group_name)
                        payload.append(payload_tuple)

                        # self.create_users_with_thread(payload)

        # PostgreSQL Handler
        elif upload_method == 'db':

            db = DB()

            with db.conn.cursor() as cursor:
                cursor.execute(query)
                records = cursor.fetchall()

                num_rows = cursor.rowcount

                if num_rows > 10:
                    payload = list()
                    for row in records:
                        payload_tuple = (row[1] + row[2], row[3], group_name)
                        payload.append(payload_tuple)

                        # self.create_users_with_thread(payload)

        return payload

    def create_users_with_thread(self, payload):

        print("Begin Threading Operation")

        with ThreadPoolExecutor(max_workers=10) as executors:
            for _ in executors.map(self.create_user, payload):
                print("done")

    # Common Group Methods
    def create_groups(self, logger, group_name):

        if self.is_a_group(self.client, group_name):
            logger.warning('Group already exists.')
        else:
            response = self.client.create_group(group_name)

    def is_a_group(self, group_to_check):

        """
        returns whether a group is a present in the enterprise

        :param group_to_check:
        :return:
        """

        groups = self.client.get_groups(group_to_check)
        list_of_groups = []

        for group in groups:
            list_of_groups.append(group.name)

        if group_to_check in list_of_groups:
            return True
        else:
            return False

    def get_group_id(self, group_name):

        """
        Returns the group id as an int by searching for the group name

        :param group_name:
        :return: int
        """

        group_id = None
        groups = self.client.get_groups(group_name)

        for group in groups:
            if group.name == group_name:
                group_id = group.id
                return group_id

        return group_id

    # Common Upload Methods

    def upload_single_file(self, source, destination_folder_id):

        response = self.client.folder(folder_id=destination_folder_id).upload(source)

        return response

    def upload_all_files_from_directory(self, source, destination_folder_id):

        # 1. Check if the path exists
        if not(os.path.exists(source)):
            print("Path doesn't exist.")
            return 0

        content = []
        # 2. Get all files in directory
        for path, subdirs, files in os.walk(source):
            for name in files:
                content.append(os.path.join(path, name))

        set_trace()

        for file in content:
            self.upload_single_file(source=file, destination_folder_id = destination_folder_id)

    # Common Folder Methods

    def get_items_in_folder(self, folder_id):

        items_dict = dict()

        items = self.client.folder(folder_id).get_items()

        for item in items:
            items_dict[item.id] = item.name

        return items_dict