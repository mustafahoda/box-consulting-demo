from datetime import datetime
import json
from pdb import  set_trace

import psycopg2

# Loads Config Data from config.json
with open('config/config.json') as json_file:
    data = json.load(json_file)
    db_config = data["db_config"]
    db_name = db_config["db_name"]
    db_user = db_config["db_user"]
    db_password = db_config["db_password"]
    db_host = db_config["db_host"]
    db_port = db_config["db_port"]


class DB():
    def __init__(self):
        self.conn = psycopg2.connect("dbname=%s user=%s password=%s host=%s port=%s" % (db_name, db_user, db_password, db_host, db_port))
        self.conn_time = datetime.now()

    def close(self):
        self.conn.close()