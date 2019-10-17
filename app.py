from pdb import set_trace

import click

from src import users



@click.group()
def cli1():
    pass

@cli1.command()
@click.option('-m', '--upload-method', type=click.Choice(['excel', 'json'], case_sensitive=False))
@click.argument('file', type=click.Path(exists=True), nargs = 1)
@click.argument('group', type=click.Choice(['students', 'faculty']), nargs=1)
def create_users_batch(upload_method, file, group):

    users.create_users(upload_method, file, group)


@cli1.command()
def get_users():
    users.get_users()


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

    while True:
        cli()
