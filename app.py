from pdb import set_trace

import click

from src import users

@click.group()
def cli1():
    pass

@cli1.command()
def print_users():

    users_list = users.get_users()

    for user in users_list:
        click.echo("%s : %s" % (user.id, user.message))


@cli1.command()
@click.argument('file', type=click.Path(exists=True), nargs = 1)
@click.argument('group', type=click.Choice(['students', 'faculty']), nargs=1)
@click.option('-m', '--upload-method', type=click.Choice(['excel', 'json'], case_sensitive=False))
@click.option('-q', '--query',)
def create_users_batch(upload_method, file, group, query):

    create_users_response = users.create_users(upload_method, file, group, query)

    # TODO: Keep count of how many users were added and print it.

@cli1.command()
@click.argument('query')
def create_users_db(query):

    create_users_response = users.create_users('db', None, 'students', query)


@cli1.command()
@click.argument('login')
@click.option('-f', '--force', type=click.Choice(['True', 'False']), help="True: if you'd like to delete files belonging to the user. False: if you'd like to maintain files after user has been deleted", required=True)
def delete_single_user(login, force):

    click.echo("If you are sure you'd like to delete %s, enter DELETE. This action can not be undone. Any other key if you don't want to delete." % login)
    user_input = input()

    if user_input == 'DELETE':
        response = users.delete_user(login, force)

        if response:
            click.echo("Successfully deleted user with login %s" % login)
        else:
            click.echo("Failed to delete user with login %s" % login)

    else:
        click.echo("Delete command not entered. No users were deleted")


@cli1.command()
@click.option('-f', '--force', type=click.Choice(['True', 'False']), help="True: if you'd like to delete files belonging to the user. False: if you'd like to maintain files after user has been deleted", required=True)
def delete_all_users(force):


    click.echo("If you are sure you'd like to delete all users, enter DELETE. This action can not be undone! Any other key if you don't want to delete.")
    user_input = input()

    if user_input == 'DELETE':
        response = users.delete_all_users(force)
        click.echo("%s users were deleted" % response['success_count'])
        click.echo("%s users failed to be deleted" % response['fail_count'])
    else:
        click.echo("No users were deleted.")






# @click.command()
# def migrate_files():
#     pass

cli = click.CommandCollection(sources=[cli1])

if __name__ == "__main__":

    while True:
        cli()
