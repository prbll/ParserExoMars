import pandas as pd
import sys
import os
import csv


class PandasParser:
    @staticmethod
    def parse():
        if len(sys.argv) != 2:
            print("You should pass only 1 argument: file name.")
            exit(1)

        try:
            df = pd.read_csv(sys.argv[1], sep='\s{2,}', engine='python', skiprows=3, header=None, dtype='str')
        except FileNotFoundError:
            print("File is not found.")
            exit(2)
        except Exception as message:
            print("Something went wrong: " + str(message))

        output_file = os.path.splitext(sys.argv[1])[0]+"_pandasParsed.txt"

        with open(output_file, newline='', mode='w') as output:
            writer = csv.writer(output)
            writer.writerow(["UTC Board Time" "\t" "Ground latitude" "\t" "Ground longitude" "\t"
                             "Device orientation latitude" "\t" "Device orientation longitude" "\t"
                             "Sun latitude(Lat sub_SOLAR)" "\t" "Sun longitude(Lon sub_SOLAR)"])
        drops = [1, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20]
        df.drop(columns=drops).to_csv(output_file, sep='\t', index=False, header=False, mode='a')
