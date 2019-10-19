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
