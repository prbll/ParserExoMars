#!/usr/bin/env python3

import requests
import json
from datetime import datetime
from dateutil import tz


class Client:
    def __init__(self):
        self.configuration = ConfigReader().get_config()
        self.data = ''
        date = datetime.utcnow()
        self.startDateTime = datetime(date.year, date.month, date.day, tzinfo=tz.tzutc()).strftime('%Y-%m-%dT%H:%M:%S.%fZ')\
            if "startDateTime" not in self.configuration else self.configuration["startDateTime"]
        self.endDateTime = date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')\
            if "endDateTime" not in self.configuration else self.configuration["endDateTime"]

    def get_data(self):
        with open(self.configuration["loggingFileName"], 'a+') as log:
            json_body = RequestBodyBuilder() \
                .add_parameter('BeginDate', self.startDateTime) \
                .add_parameter('EndDate', self.endDateTime)\
                .add_parameter('InputFileType', 'txt')\
                .add_parameter('Instrument', 'acstracking')\
                .add_parameter('Step', self.configuration["step"])\
                .build()
            guid = requests.post(self.configuration["serviceUrl"] + '/Task', json=json_body).json()["GUID"]
            log.write("[%s] Task request was sent successfully. GUID: %s.\n" % (datetime.utcnow(), guid))
            data = requests.get(self.configuration["serviceUrl"] + '/GetFile', {'guid': guid})
            while data.status_code == requests.codes.no_content:
                data = requests.get(self.configuration["serviceUrl"] + '/GetFile', {'guid': guid})

            log.write("[%s] Data was received successfully. Start DateTime: %s, End DateTime: %s.\n"
                      % (datetime.utcnow(), self.startDateTime, self.endDateTime))
            self.data = data.text
        return self

    def to_file(self):
        with open(self.startDateTime.replace(':', '-') + '_' + self.endDateTime.replace(':', '-') + '_Geometry.txt', "w+") as file:
            file.write(self.data)
        return


class RequestBodyBuilder:
    def __init__(self):
        self.body = {}

    def add_parameter(self, key, value):
        self.body.update([(key, value)])
        return self

    def build(self):
        return self.body


class Logger:
    @staticmethod
    def initialize_logging():
        with open(ConfigReader().get_config()["loggingFileName"], 'a+'):
            pass


class ConfigReader:
    def __init__(self):
        with open('ServiceClientConfig.json') as configuration:
            self.config = json.load(configuration)

    def get_config(self):
        return self.config


Logger.initialize_logging()
try:
    Client().get_data().to_file()
except Exception as ex:
    with open(ConfigReader().get_config()["loggingFileName"], 'a+') as logger:
        logger.write("[%s] Error occurred: %s.\n" % (datetime.utcnow(), ex))
