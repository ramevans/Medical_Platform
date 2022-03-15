# Ramon Evans raevans@bu.edu Copyright 2022
#!/usr/bin/python3

import json
#Reads the Device Json file and prints out the output
try:
    with open('test_chat.json') as json_file:
        data = json.load(json_file)
        print(data)
except:
    print("JSON error")
    exit()
