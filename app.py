from pdb import set_trace

import click

from src.Client import BoxClient
app_client = BoxClient()


@click.group()
def cli1():
    pass

@cli1.command()
def print_users():

    users_list = app_client.get_users()

    for id, name in zip(users_list.keys(), users_list.values()):
        click.echo("%s : %s" % (id, name))


@cli1.command()
@click.option('-f', '--file', type=click.Path(exists=True), nargs = 1)
@click.option('-m', '--upload-method', type=click.Choice(['excel', 'json', 'db'], case_sensitive=False))
@click.option('-q', '--query', required=False)
@click.argument('group', type=click.Choice(['students', 'faculty']), nargs=1)
def create_users_batch(upload_method, file, group, query):

    if upload_method == 'db' and query is None:
        click.echo("A SQL Query must be entered when choosing the database upload method")
        return 0


    if ((upload_method == 'excel') or (upload_method == 'json')) and file is None:
        click.echo("A file path must be entered in order to use the upload method %s" % upload_method)
        return 0

    create_users_response = app_client.create_users(upload_method, file, group, query)

    # TODO: Keep count of how many users were added and print it.


@cli1.command()
@click.argument('login')
@click.option('-f', '--force', type=click.Choice(['True', 'False']), help="True: if you'd like to delete files belonging to the user. False: if you'd like to maintain files after user has been deleted", required=True)
def delete_single_user(login, force):

    click.echo("If you are sure you'd like to delete %s, enter DELETE. This action can not be undone. Any other key if you don't want to delete." % login)
    user_input = input()

    if user_input == 'DELETE':
        response = app_client.delete_user(login, force)

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
        response = app_client.delete_all_users(force)
        click.echo("%s users were deleted" % response['success_count'])
        click.echo("%s users failed to be deleted" % response['fail_count'])
    else:
        click.echo("No users were deleted.")


@cli1.command()
@click.argument('name', nargs = 2)
@click.argument('login')
@click.argument('group', type=click.Choice(['students', 'faculty']))
def create_single_user(name, login, group):

    payload = (name[0] + " " + name[1], login, group)
    set_trace()
    response = app_client.create_user(payload)


@cli1.command()
@click.argument('source', type=click.Path(exists=True), nargs = 1)
@click.argument('destination_folder_id')
def upload_single_file(source, destination_folder_id):

    response = app_client.upload_single_file(source, destination_folder_id)


@cli1.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('destination_folder_id')
def upload_all_files_from_directory(source, destination_folder_id):
    set_trace()
    app_client.upload_all_files_from_directory(source, destination_folder_id)


@cli1.command()
@click.argument('folder_id')
def print_items_in_folder(folder_id):
    items = app_client.get_items_in_folder(folder_id)

    for id, name in zip(items.keys(), items.values()):
        click.echo("%s : %s" % (id, name))


cli = click.CommandCollection(sources=[cli1])

if __name__ == "__main__":

    cli()
