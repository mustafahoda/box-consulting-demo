from src.Client import BoxClient
from pdb import set_trace
from src.users import get_user_by_email
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer as timer

app_client = BoxClient()
box_client = app_client.client

as_users = app_client.as_users


def create_user(config_tuple):
    name = config_tuple[0]
    login = config_tuple[1]
    group = config_tuple[2]


    response = app_client.create_user(name, login, group)


if __name__ == "__main__":

    users_to_add = [
        ("Jeff", "jeffmacbookpro@toodles.com", "students"),
        ("Honest", "honestmacbookkkppproo@toodles.com", "students"),
        ("Eyelashes", "eyelashes@toodles.com", "students"),
        ("Lightbulb", "Ilightuptheworld@toodles.com", "students"),
        ("eyePhone", "eyephoneschangedtheworld@toodles.com", "students"),
        ("backpack", "backpack@toodles.com", "students")
    ]

    # Threading example
    # start = timer()
    # with ThreadPoolExecutor(max_workers=4) as executor:
    #     for _ in executor.map(create_user, users_to_add):
    #         print("done")
    #
    # end1 = timer()

    # Non-threading example
    for _ in users_to_add:
        create_user(_)

    end2 = timer()

    # print("start: %s" % start)
    # print("end1: %s" % end1)
    # print("end2: %s" % end2)




