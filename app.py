from boxsdk import OAuth2, Client
import click
import pandas as pd

import json
from pdb import set_trace

import json

from src import create_users

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

@click.group()
def cli1():
    pass

@cli1.command()
@click.option('-m', '--upload-method', type=click.Choice(['excel', 'json'], case_sensitive=False))
@click.argument('file', type=click.Path(exists=True))
def create_users_batch(upload_method, file):


    click.echo(file)
    click.echo(upload_method)

    create_users.create_users(upload_method, file)



@cli1.command()
def get_users():
    users = client.users(user_type='all')
    for user in users:
        print('{0} (User ID: {1})'.format(user.name, user.id))



@cli1.command()
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

cli = click.CommandCollection(sources=[cli1])

if __name__ == "__main__":
    cli()
