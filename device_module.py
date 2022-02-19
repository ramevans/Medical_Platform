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
# This variable access the Temperature value from the JSON File
Therometer_info = data['Devices']['Therometer']['Temperature']

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
# this checks the Therometer Device values and indicate to the user if temperature is above or below normal temp.
def temperature_info(Therometer):
    if not isinstance(Therometer, (int,float)):
        return "Please Enter a Proper Value"
    if Therometer < 97:
        #insert Alert Module function here:
        return ('Your Body temperature is Below Normal Temperature')
    elif Therometer > 99:
        #insert Alert Module function here:
        return ('Your Body temperature is Above Normal Temperature')
    return 0

# Error Codes
error_code=check_type(data['Devices'])
if error_code!=0:
    print(error_code, "1")
error_code = temperature_info(Therometer_info)
if error_code!=0:
    print(error_code, "2")
