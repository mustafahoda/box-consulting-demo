from src.Client import BoxClient
from pdb import set_trace
from src.users import get_user_by_email

app_client = BoxClient()
box_client = app_client.client

as_users = app_client.as_users

set_trace()

def thread_create_user(client, creator, name, login, group):


    response = app_client.create_user(name, login, group)


# def thread_runner(client, tasks):