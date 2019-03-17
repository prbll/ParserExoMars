import sys
import os
import re
import RecordCreator


# Парсер файла, использующий стандартные функции языка Python
class Parser:
    @staticmethod
    def parse():
        if len(sys.argv) != 2:
            print("You should pass only 1 argument: file name.")
            exit(1)
        try:
            input_file = open(sys.argv[1], "r")
        except FileNotFoundError:
            print("File is not found.")
            exit(2)
        except Exception as message:
            print("Something went wrong: " + str(message))

        reg = re.compile("[0-9]{4} [A-Z]{3} [0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        output_file = open(os.path.splitext(sys.argv[1])[0]+"_parsed.txt", "w")
        header = ["UTC Board Time", "Ground latitude", "Ground longitude", "Device orientation latitude",
                  "Device orientation longitude", "Sun latitude(Lat sub_SOLAR)", "Sun longitude(Lon sub_SOLAR)"]
        output_file.write(RecordCreator.RecordCreator.CreateRecord(values=header))
        data = input_file.read()
        last_record = 0
        for record in reg.finditer(data):
            if last_record == 0:
                output_file.write(record.group() + "\t")
                last_record = record.start()
                continue
            values = list(map(str.strip, list(filter(None, data[last_record:record.start()-1].split('  ')))))
            amount_of_values = len(values)
            body = [values[3], values[4], values[5], values[6], values[amount_of_values-3], values[amount_of_values-2]]
            output_file.write(RecordCreator.RecordCreator.CreateRecord(values=body))
            output_file.write(record.group() + "\t")
            last_record = record.start()

        values = list(map(str.strip, list(filter(None, data[last_record:].split('  ')))))
        amount_of_values = len(values)
        body = [values[2], values[3], values[amount_of_values - 3], values[amount_of_values - 2], values[4], values[5]]
        output_file.write(RecordCreator.RecordCreator.CreateRecord(body))

