import pandas as pd
import sys
import os
import csv
import re
import fileinput
from dateutil import tz
from datetime import datetime
from ConfigReader import ConfigReader
from Logger import Logger


# Парсер файла, использующий библиотеку Pandas
def get_orbit_number(file_name):
    found = re.search(r'ORB\d+', file_name).group(0)
    found = re.search(r'[^0\D]*[1-9]+\d+', found).group(0)
    return found


def add_quotes(value):
    result = '"'
    result += value
    result += '"'
    return result


class PandasParser:
    def __init__(self):
        self.months = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06', 'JUL': '07',
                       'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}
        self.configuration = ConfigReader(sys.argv[1]).get_config()
        self.logger = Logger(self.configuration["logFileName"]).get_logger()
        self.data = ''
        date = datetime.utcnow()
        self.startDateTime = datetime(date.year, date.month, date.day, tzinfo=tz.tzutc()).strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ') \
            if "startDateTime" not in self.configuration else self.configuration["startDateTime"]
        self.endDateTime = date.strftime('%Y-%m-%dT%H:%M:%S.%fZ') \
            if "endDateTime" not in self.configuration else self.configuration["endDateTime"]

    def convert_date(self, date):
        pieces = date.split(' ')
        date_time = '-'.join(pieces[:3])
        for month, key in self.months.items():
            date_time = date_time.replace(month, key)
        date_time += ' '
        time = pieces[3].split('.')
        date_time += time[0]
        return date_time

    def do_work(self):
        input_folder = self.configuration["inputFolder"]
        output_folder = self.configuration["outputFolder"]
        files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
        for file in files:
            output_filename = os.path.splitext(file)[0] + ".csv"
            if self.configuration["skipProcessed"] == 1:
                if os.path.exists(os.path.join(output_folder, output_filename)):
                    self.logger.log_info("%s file skipped cause it was processed earlier." % file)
                    print("%s file skipped cause it was processed earlier." % file)
                    continue

            self.parse(file, input_folder, output_folder, output_filename)

    def parse(self, filename, input_folder, output_folder, output_filename):
        try:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, output_filename)
            self.logger.log_info("Trying to parse %s file..." % filename)
            df = pd.read_csv(input_path, sep='\s{1,}', engine='python', usecols=[8, 9, 15, 16, 23], skiprows=3, header=None, dtype='str')
            date_df = pd.read_csv(input_path, sep='\s{2,}', engine='python', usecols=[0], skiprows=3, header=None, dtype='str')
            orbit_number = get_orbit_number(input_path)

            date_df[0] = date_df[0].apply(self.convert_date)
            date_df[0] = date_df[0].apply(add_quotes)
            df.insert(0, "POINT_DT", date_df[0])
            df.insert(0, "SEANCE_DT", pd.Series([date_df.iloc[0][0] for x in range(len(df.index))]))
            df.insert(2, "ORBIT", pd.Series([orbit_number for x in range(len(df.index))]))

            rows_list = []
            for index in range(len(df.index) * 2):
                record = {}
                if index % 2 == 0:
                    record.update({0: df.iloc[index // 2, 0], 1: df.iloc[index // 2, 1], 2: df.iloc[index // 2, 2],
                                   3: "POINT({} {})".format(df.iloc[index // 2, 4], df.iloc[index // 2, 3]),
                                   4: df.iloc[index // 2, 7], 5: "TRACK"})
                else:
                    record.update({0: df.iloc[index // 2, 0], 1: df.iloc[index // 2, 1], 2: df.iloc[index // 2, 2],
                                   3: "POINT({} {})".format(df.iloc[index // 2, 6], df.iloc[index // 2, 5]),
                                   4: df.iloc[index // 2, 7], 5: "OCCULTATION"})
                rows_list.append(record)

            out_df = pd.DataFrame(rows_list)
            out_df[3] = out_df[3].apply(add_quotes)
            out_df[5] = out_df[5].apply(add_quotes)

        except FileNotFoundError as message:
            self.logger.log_info("File %s was not found in folder %s. Stack Trace: %s." % (filename, input_folder, message))
            print("File is not found.")
            exit(-2)
        except Exception as message:
            self.logger.log_info("Something went wrong: %s." % str(message))
            print("Something went wrong: " + str(message))
            exit(-3)

        self.logger.log_info("%s file was successfully parsed." % filename)
        print("%s file was successfully parsed." % filename)
        self.logger.log_info("Generating output file %s..." % output_filename)
        print("Generating output file %s..." % output_filename)
        try:
            with open(output_path, newline='', mode='w') as output:
                output.write("SEANCE_DT,POINT_DT,ORBIT,WKT,HEIGHT,POINT_TYPE\n")
            out_df.to_csv(output_path, sep=',', index=False, header=False, mode='a', quoting=csv.QUOTE_NONE)
            with fileinput.FileInput(output_path, inplace=True) as file:
                for line in file:
                    print(line.replace(",", ", "), end='')
            with open(output_path, "r+") as file:
                file.seek(0, os.SEEK_END)
                pos = file.tell() - 1
                while pos > 0 and file.read(1) != "\n":
                    pos -= 1
                    file.seek(pos, os.SEEK_SET)
                if pos > 0:
                    file.seek(pos, os.SEEK_SET)
                    file.truncate()

        except Exception as message:
            self.logger.log_info("Something went wrong: %s." % str(message))
            print("Something went wrong: " + str(message))
            exit(-3)

        self.logger.log_info("Successfully completed.")
        print("Successfully completed.")
