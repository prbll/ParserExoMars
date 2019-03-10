import sys
import os
import re

def main():
    if len(sys.argv) != 2:
        print("You should pass only 1 argument: file name.")
        exit(1)
    try:
        input_file = open(sys.argv[1], "r")
    except FileNotFoundError:
        print("File is not found.")
        exit(2)

    reg = re.compile("[0-9]{4} [A-Z]{3} [0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
    output_file = open(os.path.splitext(sys.argv[1])[0]+"_parsed.txt", "w")
    #output_file.write("UTC Board Time, Ground latitude and longitude, Sun latitude and longitude(Lat sub_SOLAR and Lon "
    #                  "sub_SOLAR), Device orientation latitude and longitude")
    output_file.write("UTC Board Time" + "\t" + "Ground latitude" + "\t" +
                      "Ground longitude" + "\t" + "Sun latitude(Lat sub_SOLAR)" + "\t" + "Sun longitude(Lon sub_SOLAR)"
                      + "\t" + "Device orientation latitude" + "\t" + "Device orientation longitude" + "\n")
    data = input_file.read()
    #records = re.findall(reg, data)
    for record in reg.finditer(data):
        output_file.write(record.group())
        print(record.start())
        output_file.write("\n")


main()
