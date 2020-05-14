#!/usr/local/bin/env python3

import requests
from ConfigReader import ConfigReader
from Logger import Logger
from datetime import datetime, timedelta
from dateutil import tz
import sys
import os


class Client:
    def __init__(self):
        self.configuration = ConfigReader(sys.argv[1]).get_config()
        self.logger = Logger(self.configuration["logFileName"]).get_logger()
        self.output_folder = self.configuration["outputFolder"]
        self.data = ''
        date = datetime.now()
        date = date.replace(minute=0, second=0, microsecond=0)
        self.request_interval = datetime.strptime(self.configuration["requestInterval"], "%H:%M:%S")
        if self.request_interval:
            delta = timedelta(hours=self.request_interval.hour,
                              minutes=self.request_interval.minute,
                              seconds=self.request_interval.second)
            self.startDateTime = (date - delta).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            self.endDateTime = date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            self.startDateTime = datetime(date.year, date.month, date.day, tzinfo=tz.tzutc()).strftime(
                '%Y-%m-%dT%H:%M:%S.%fZ') \
                if "startDateTime" not in self.configuration else self.configuration["startDateTime"]
            self.endDateTime = date.strftime('%Y-%m-%dT%H:%M:%S.%fZ') \
                if "endDateTime" not in self.configuration else self.configuration["endDateTime"]

    def get_data(self):
        try:
            json_body = RequestBodyBuilder() \
                .add_parameter('BeginDate', self.startDateTime) \
                .add_parameter('EndDate', self.endDateTime)\
                .add_parameter('InputFileType', 'txt')\
                .add_parameter('Instrument', 'acstracking')\
                .add_parameter('Step', self.configuration["step"])\
                .build()
            guid = requests.post(self.configuration["serviceUrl"] + '/Task', json=json_body).json()["GUID"]
            self.logger.log_info("[%s] Task request was sent successfully. GUID: %s." % (datetime.utcnow(), guid))
            print("[%s] Task request was sent successfully. GUID: %s." % (datetime.utcnow(), guid))
            data = requests.get(self.configuration["serviceUrl"] + '/GetFile', {'guid': guid})
            while data.status_code == requests.codes.no_content:
                data = requests.get(self.configuration["serviceUrl"] + '/GetFile', {'guid': guid})

            self.logger.log_info("[%s] Data was received successfully. Start DateTime: %s, End DateTime: %s."
                      % (datetime.utcnow(), self.startDateTime, self.endDateTime))
            print("[%s] Data was received successfully. Start DateTime: %s, End DateTime: %s."
                      % (datetime.utcnow(), self.startDateTime, self.endDateTime))
            self.data = data.text
            return self

        except Exception as message:
            self.logger.log_info("Something went wrong: %s." % str(message))
            print("Something went wrong: " + str(message))
            exit(-3)

    def to_file(self):
        file_name = self.startDateTime.replace(':', '-') + '_' + self.endDateTime.replace(':', '-') + '_Geometry.txt'
        destination_file = os.path.join(self.output_folder, file_name)
        with open(destination_file, "w+") as file:
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


if len(sys.argv) != 2:
    print("You should pass only 1 argument: configuration file.")
    exit(-1)

Client().get_data().to_file()
