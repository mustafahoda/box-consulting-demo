import os
import json
import logging
import logging.config
# TODO Remove pdb import
from pdb import  set_trace
from timeit import default_timer as timer

import pandas as pd
from boxsdk import exception

from src.Client import BoxClient
from src.DB import DB
from src.groups import create_groups, get_group_id


box_client = BoxClient()
client = box_client.client

def upload_single_file(source, destination_folder_id):
    response = client.folder(folder_id=destination_folder_id).upload(source)
    return response