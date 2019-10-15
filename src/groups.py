from src.Client import BoxClient

from pdb import set_trace

client = BoxClient().client

def create_groups(group_name):

    if is_a_group(group_name):
        print('Group already exists.')
    else:
        response = client.create_group(group_name)


def is_a_group(group_to_check):
    groups = client.get_groups(group_to_check)
    list_of_groups = []

    for group in groups:
        list_of_groups.append(group.name)

    if group_to_check in list_of_groups: return True
    else: return False

def assign_user_group(user_id, group):
    pass