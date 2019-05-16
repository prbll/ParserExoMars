import pandas as pd
import sys
import os
import csv
import re
import fileinput


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

    def convert_date(self, date):
        pieces = date.split(' ')
        date_time = '-'.join(pieces[:3])
        for month, key in self.months.items():
            date_time = date_time.replace(month, key)
        date_time += ' '
        time = pieces[3].split('.')
        date_time += time[0]
        return date_time

    def parse(self):
        if len(sys.argv) != 2:
            print("You should pass only 1 argument: file name.")
            exit(1)
        try:
            df = pd.read_csv(sys.argv[1], sep='\s{2,}', engine='python', skiprows=3, header=None, dtype='str')
            columns_to_drop = [1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28]
            orbit_number = get_orbit_number(sys.argv[1])

            df[0] = df[0].apply(self.convert_date)
            df[0] = df[0].apply(add_quotes)
            df.insert(0, "0", pd.Series([df.iloc[0][0] for x in range(len(df.index))]))
            df.insert(2, "2", pd.Series([orbit_number for x in range(len(df.index))]))
            df = df.drop(columns=columns_to_drop)

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

        except FileNotFoundError:
            print("File is not found.")
            exit(2)
        except Exception as message:
            print("Something went wrong: " + str(message))

        output_file = os.path.splitext(sys.argv[1])[0] + ".csv"

        with open(output_file, newline='', mode='w') as output:
            output.write("SEANCE_DT,POINT_DT,ORBIT,WKT,HEIGHT,POINT_TYPE\n")
        out_df.to_csv(output_file, sep=',', index=False, header=False, mode='a', quoting=csv.QUOTE_NONE)
        with fileinput.FileInput(output_file, inplace=True) as file:
            for line in file:
                print(line.replace(",", ", "), end='')
        with open(output_file, "r+") as file:
            file.seek(0, os.SEEK_END)
            pos = file.tell() - 1
            while pos > 0 and file.read(1) != "\n":
                pos -= 1
                file.seek(pos, os.SEEK_SET)
            if pos > 0:
                file.seek(pos, os.SEEK_SET)
                file.truncate()

