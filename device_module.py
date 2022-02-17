# Ramon Evans raevans@bu.edu Copyright 2022
#!/usr/bin/python3

import json

#Reads the Device Json file and prints out the output
with open('devices.json') as json_file:
    data = json.load(json_file)
print (data)
