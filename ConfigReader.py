import json


class ConfigReader:
    def __init__(self, config_name):
        with open(config_name) as configuration:
            self.config = json.load(configuration)

    def get_config(self):
        return self.config
