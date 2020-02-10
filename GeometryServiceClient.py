import requests
import json
from datetime import datetime
from dateutil import tz


class Client:
    def __init__(self):
        self.configuration = self.__read_config()
        self.data = ''

    def get_data(self, date):
        json_body = RequestBodyBuilder() \
            .add_parameter('BeginDate', datetime(date.year, date.month, date.day, tzinfo=tz.tzutc()).strftime('%Y-%m-%dT%H:%M:%SZ')) \
            .add_parameter('EndDate', date.strftime('%Y-%m-%dT%H:%M:%SZ'))\
            .add_parameter('InputFileType', 'txt')\
            .add_parameter('Instrument', 'acstracking')\
            .add_parameter('Step', self.configuration["step"])\
            .build()
        guid = requests.post(self.configuration["serviceUrl"] + '/Task', json=json_body).json()["GUID"]
        data = requests.get(self.configuration["serviceUrl"] + '/GetFile', {'guid': guid})
        while data.status_code == requests.codes.no_content:
            data = requests.get(self.configuration["serviceUrl"] + '/GetFile', {'guid': guid})

        self.data = data.text
        return self

    def to_file(self, date):
        with open(date.strftime("%d-%b-%Y") + '_Geometry.txt', "w+") as file:
            file.write(self.data)
        return

    @staticmethod
    def __read_config():
        with open('ServiceClientConfig.json') as config:
            return json.load(config)


class RequestBodyBuilder:
    def __init__(self):
        self.body = {}

    def add_parameter(self, key, value):
        self.body.update([(key, value)])
        return self

    def build(self):
        return self.body


date = datetime.utcnow()
Client().get_data(date).to_file(date)
