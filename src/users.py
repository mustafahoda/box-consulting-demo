import os
import json
import logging
import logging.config
from concurrent.futures import ThreadPoolExecutor

# TODO Remove pdb import
from pdb import  set_trace

import pandas as pd
from boxsdk import exception

from src.groups import create_groups, get_group_id
from src.DB import DB


# Loads Config Data from config.json
with open('config/config.json') as json_file:
    data = json.load(json_file)
    log_config = data["logger_config"]
    log_config['handlers']['file']['filename'] = '%s/static/reports/test.log' % (os.getcwd())
    admins = data['app_config']['as_users']

logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)


def get_users(client):
    """
    Return a dictionary with users and their ids
    :return:
    """

    users_dict = dict()
    users = client.users(user_type='all')

    for user in users:
        users_dict[user.id] = user.name

    return users_dict

def get_user_by_email(client, login):
    """
    Searches for a user by email and returns a Box User Object
    :param login:
    :return:
    """

    user = None
    users = client.users(filter_term=login)

    for user in users:
        if user.login == login:
            return user

    return user

def create_users(client, upload_method, file, group_name, query):
    """
    Create users at scale

    :param upload_method:
    :param file:
    :param group_name:
    :return: a dictionary containing on how many users were created and how many failed to be created
    """

    success_count = 0
    fail_count = 0

    group_id = get_group_id(client, group_name)

    # If the group doesn't exist, create it.
    if not group_id:
        user_input = input("The group %s doesn't exist. Would you like to create it (yes/no)? " % group_name)

        if user_input == "yes":
            group_response = create_groups(client, logger, group_name)

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

            set_trace()

            create_users_with_thread(payload)

        else:
            # Todo: is there a better way to iterate through DataFrame rows?
            for row in df.itertuples():
                create_user_response = create_user(row._1 + row._2, row.Email, group_name)

                if create_user_response: success_count += 1
                else: fail_count += 1

    # JSON Handler
    elif upload_method == 'json':
        with open(file) as json_file:
            data = json.load(json_file)

            row_count = len(data)
            set_trace()

            if row_count > 10:
                payload = list()
                for current_user in data:
                    payload_tuple = (current_user['first_name'] + ' ' + current_user['last_name'], current_user['email'], group_name)
                    payload.append(payload_tuple)

                create_users_with_thread(client, payload)

            else:
                for current_user in data:
                    create_user_response = create_user(current_user['first_name'] + ' ' + current_user['last_name'], current_user['email'], group_name)

                    if create_user_response: success_count  += 1
                    else: fail_count += 1

    # PostgreSQL Handler
    elif upload_method == 'db':

        db = DB()

        with db.conn.cursor() as cursor:
            cursor.execute(query)
            records = cursor.fetchall()

            num_rows = cursor.rowcount
            set_trace()

            if num_rows > 10:
                payload = list()
                for row in records:
                    payload_tuple = (row[1] + row[2], row[3], group_name)
                    payload.append(payload_tuple)

                create_users_with_thread(client, payload)


            else:
                for row in records:
                    login = row[3]
                    create_user_response = create_user(row[1] + row[2], login, group_name)

                    if create_user_response: success_count += 1
                    else: fail_count += 1

    return {'success_count': success_count, 'fail_count': fail_count}

def create_user(client, payload):

    """
    Creates a single user

    :param name: Name of the user
    :param login: what's the login for the user you are creating
    :param group_name: which group do you want the user to be assigned to
    :return:
    """

    set_trace()

    # Payload Unpacking
    name = payload[0]
    login = payload[1]
    group_name = payload[2]

    success = False
    group_id = None

    if name == None or login == None:   return success

    if group_name == None:
        group_id = get_group_id(group_name)

    try:
        user = client.create_user(name, login)


        # TODO: Deal with this later
        if group_id != None:
            membership_response = client.group(group_id=group_id).add_member(user)

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

def delete_all_users(client, force):
    """
    Delete all users at scale. Can not be undone.

    :param force:
    :return:
    """

    success_count = 0
    fail_count = 0
    users = client.users(user_type='all')

    for user in users:
        set_trace()
        # if the current user is accessed, which is also the admin, don't delete it.
        if user == client.user().get() or user.id in admins: continue

        delete_response = client.user(user.id).delete(force=force)

        if delete_response == True:
            msg = 'Deleted: {0} (User ID: {1})'.format(user.name, user.id)
            logger.info(msg)
            success_count += 1
        else:
            msg = 'Unable to delete user. %s : %s' % (user.id, user.login)
            logger.error(msg)
            fail_count += 1

    return {'success_count':success_count, 'fail_count':fail_count}

def delete_user(client, email, force):
    """
    Delete a single user

    :param email:
    :param force:
    :return:
    """

    success = False

    user = get_user_by_email(email)
    if user == None: return success

    success = client.user(user.id).delete(force=force)

    if success:
        msg = 'Deleted: {0} (User ID: {1})'.format(user.name, user.id)
        logger.info(msg)

    else:
        msg = 'Unable to delete user. %s : %s' % (user.id, user.login)
        logger.error(msg)

    return success

def create_users_with_thread(payload):

    print("THREADINNNGGG")
    set_trace()

    with ThreadPoolExecutor(max_workers=15) as executors:
        for _ in executors.map(create_user, client, payload):
            print("done")



