from boxsdk import OAuth2, Client
import click
import pandas as pd

import json
from pdb import set_trace

import json

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

client = Client(auth)
user = client.user().get();

@click.command()
@click.option('-m', '--upload-method', type=click.Choice(['excel', 'json'], case_sensitive=False))
@click.argument('file', type=click.Path(exists=True))
def create_users_batch(upload_method, file):

    click.echo(file)
    click.echo(upload_method)

    # Excel Handler
    if upload_method == 'excel':
        click.echo('excel')
        df = pd.read_excel(file)

        for row in df.itertuples():
            click.echo(row)

            response = client.create_user(row._1 + row._2, row.Email)
            # set_trace()


    # JSON Handler
    if upload_method == 'json':
        click.echo('json')

@click.command()
def get_users():
    users = client.users(user_type='all')
    for user in users:
        print('{0} (User ID: {1})'.format(user.name, user.id))



@click.command()
def delete_users():

    user_input = input("If you are sure you'd like to delete all users, enter DELETE: ")

    if user_input == 'DELETE':
        users = client.users(user_type='all')
        for user in users:
            print('{0} (User ID: {1})'.format(user.name, user.id))

            client.user(user.id).delete(force=True)


# @click.command()
# def migrate_files():
#     pass

if __name__ == "__main__":
    # create_users_batch(
    # delete_users()
    get_users()
