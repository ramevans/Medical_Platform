# Ramon Evans raevans@bu.edu Copyright 2022
#!/usr/bin/python3

import json
#Reads the Device Json file and prints out the output, if JSON File is not in the proper format it will exit the program
try:
    with open('test_devices.json') as json_file:
        data = json.load(json_file)
except:
    print("JSON error")
    exit()
    #print (data)

# this checks if the these fields are the proper structure type
def check_type(all_device):
    #print(type(all_device))
    for device_info in all_device:
        device=all_device[device_info]
        if not isinstance(device['Device Name'],str):
            return "Incorrect Device Name (" + str(device_info)+")"
        if not isinstance(device['Device MAC Address'],str):
            return "Incorrect Device MAC Address (" + str(device_info)+")"
        if not isinstance(device['User'],str):
            return "Incorrect User (" + str(device_info)+")"
    return 0

error_code=check_type(data['Devices'])
if error_code!=0:
    print(error_code, "1")
