import logging
import logging.config
import json

# Loads Config Data from config.json
with open('config.json') as json_file:
    data = json.load(json_file)
    log_config = data["logger_config"]

class AppLogger():
    def __init__(self):
        logging.config.dictConfig(log_config)
        self.logger = logging.getLogger(__name__)


# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
#
# path = ('%s/static/reports/%s.log' % (
#     os.getcwd(), box_client.client_created_time.strftime("%Y-%m-%dT%H:%M:%S%z")))
#
# f_handler = logging.FileHandler(path)
# f_handler.setLevel(logging.INFO)
#
# c_handler = logging.StreamHandler()
# c_handler.setLevel(logging.INFO)
#
# c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# c_handler.setFormatter(c_format)
# f_handler.setFormatter(f_format)
#
# logger.addHandler(c_handler)
# logger.addHandler(f_handler)