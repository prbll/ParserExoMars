import sys
import os
import csv
import math
import pandas as pd
# ogr lib

class TirParser:
    def __init__(self):
        self.MarsRadius = 3389.5

    def parse(self):
        if len(sys.argv) != 2:
            print("You should pass only 1 argument: file name.")
            exit(1)
        try:
            df = pd.read_csv(sys.argv[1], sep='\s{1,}', engine='python', skiprows=2, header=None, dtype='str')

            rows_list = []
            for index in range(len(df.index)):
                record = {}
                record.update({0: df.iloc[index, 10], 1: df.iloc[index, 11],
                               2: df.iloc[index, 9], 3: df.iloc[index, 15]})
                record.update({4: float(record[2])
                                  * math.sqrt((1 / (math.cos(float(record[3])) * math.cos(float(record[3]))))-1)})
                rows_list.append(record)
            out_df = pd.DataFrame(rows_list)
            new_rows_list = []
            last = 0
            for index in range(len(out_df.index)):
                record = {}
                if index == len(out_df.index) - 1:
                    break;
                record.update({0: self.MarsRadius * math.acos(math.sin(float(out_df.iloc[index, 1]))
                                                              * math.sin(float(out_df.iloc[index + 1, 1])) +
                                            math.cos(float(out_df.iloc[index, 1]))
                                                              * math.cos(float(out_df.iloc[index + 1, 1])) *
                                            math.cos(float(out_df.iloc[index, 0]) - float(out_df.iloc[index + 1, 0])))})
                if index == 15:
                    print(math.sin(float(out_df.iloc[index, 1])))
                    print(float(out_df.iloc[index, 1]))
                    print(math.sin(float(out_df.iloc[index + 1, 1])))
                    print(math.cos(float(out_df.iloc[index, 1])))
                    print(math.cos(float(out_df.iloc[index + 1, 1])))
                    print(math.cos(float(out_df.iloc[index, 0]) - float(out_df.iloc[index + 1, 0])))
                    print(record[0])
                last = record[0]
                new_rows_list.append(record)
            record = {0: last}
            new_rows_list.append(record)
            new_out_df = pd.DataFrame(new_rows_list)
            print(new_out_df)
            out_df['6'] = new_out_df[0]

        except FileNotFoundError:
            print("File is not found.")
            exit(2)
        except Exception as message:
            print("Something went wrong: " + str(message))
            exit(3)

        output_file = os.path.splitext(sys.argv[1])[0] + ".csv"
        with open(output_file, newline='', mode='w') as output:
            output.write("Lon, Lat, Dist, Theta, Width of capturing, Distance to next point\n")
        out_df.to_csv(output_file, sep=' ', index=False, header=False, mode='a', quoting=csv.QUOTE_NONE)
