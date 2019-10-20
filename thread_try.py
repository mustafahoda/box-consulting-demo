from src.Client import BoxClient
from pdb import set_trace
from src.users import get_user_by_email

app_client = BoxClient()
box_client = app_client.client

as_users = app_client.as_users


def thread_create_user(client, creator, name, login, group):

    Admin3 = box_client.user(user_id='10368548905')

    Admin3_client = box_client.as_user(Admin3)
    set_trace()

    new_user = Admin3_client.create_user('Macbook Pro')
    set_trace()







    response = app_client.create_user(name, login, group)


if __name__ == "__main__":
    thread_create_user(None, None, None, None, None)


# def thread_runner(client, tasks):