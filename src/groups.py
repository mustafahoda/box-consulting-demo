import logging
import logging.config
import json
import os

from src.Client import BoxClient

box_client = BoxClient()
client = box_client.client

# Loads Config Data from config.json
with open('config.json') as json_file:
    data = json.load(json_file)
    log_config = data["logger_config"]
    log_config['handlers']['file']['filename'] = '%s/static/reports/%s.log' % (os.getcwd(), box_client.client_created_time.strftime("%Y-%m-%dT%H:%M:%S%z"))

logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)


def create_groups(group_name):

    if is_a_group(group_name):
        logger.warning('Group already exists.')
    else:
        response = client.create_group(group_name)


def is_a_group(group_to_check):

    """
    returns whether a group is a present in the enterprise

    :param group_to_check:
    :return:
    """
    groups = client.get_groups(group_to_check)
    list_of_groups = []

    for group in groups:
        list_of_groups.append(group.name)

    if group_to_check in list_of_groups: return True
    else: return False

def assign_user_group(user_id, group):
    pass

def get_group_id(group_name):

    """
    Returns the group id as an int by searching for the group name

    :param group_name:
    :return: int
    """

    group_id = None
    groups = client.get_groups(group_name)

    for group in groups:
        if group.name == group_name:
            group_id = group.id
            return group_id

    return group_id

