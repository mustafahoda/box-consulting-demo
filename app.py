import json
from pdb import set_trace

from boxsdk import OAuth2, Client
import click

from src import users

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
@click.argument('file', type=click.Path(exists=True), nargs = 1)
@click.argument('group', type=click.Choice(['students', 'faculty']), nargs=1)
def create_users_batch(upload_method, file, group):

    click.echo(file)
    click.echo(upload_method)

    users.create_users(upload_method, file, group)


@cli1.command()
def get_users():
    users = client.users(user_type='all')
    for user in users:
        print('{0} (User ID: {1})'.format(user.name, user.id))



@cli1.command()
@click.option('-f', '--force', type=click.Choice(['True', 'False']), help="True: if you'd like to delete files belonging to the user. False: if you'd like to maintain files after user has been deleted", required=True)
def delete_all_users(force):

    click.echo("If you are sure you'd like to delete all users, enter DELETE. Any other key if you don't want to delete.")
    user_input = input()

    if user_input == 'DELETE':
        users.delete_all_users(force)
    else:
        click.echo("No users were deleted.")

@cli1.command()
@click.argument('login')
@click.option('-f', '--force', type=click.Choice(['True', 'False']), help="True: if you'd like to delete files belonging to the user. False: if you'd like to maintain files after user has been deleted", required=True)
def delete_user(login, force):
    response = users.delete_user(login, force)

    if response:
        click.echo("Successfully deleted user with login %s" % login)
    else:
        click.echo("Failed to delete user with login %s" % login)

# @click.command()
# def migrate_files():
#     pass

cli = click.CommandCollection(sources=[cli1])

if __name__ == "__main__":
    cli()
