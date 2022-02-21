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
# These variables access the Devices values from the JSON File
Therometer_info = data['Devices']['Therometer']['Temperature']
Blood_Pressure_Reader_info_sys = data['Devices']['Blood Pressure Reader']['Systolic Blood Pressure']
Blood_Pressure_Reader_info_dia = data['Devices']['Blood Pressure Reader']['Diastolic Blood Pressure']
Heart_rate_monitor_info = data['Devices']['Heart Rate Monitor']['BPM']
Oximeter_details = data['Devices']['Oximeter']['SpO2']
Weight_Scale_info = data['Devices']['Weight Scale']['Ibs']
Glucometer_details = data['Devices']['Glucometer']['mg/dL']

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

def blood_pressure_info(info_sys,info_dia):
    if not isinstance(info_sys, int) or not isinstance(info_dia, int):
        #insert Alert Module function here:
        return "Please Enter a Proper Value"
    if info_dia < 80 and info_sys > 120:
        #insert Alert Module function here:
        return ('Your Systolic Blood Pressure is Above Normal Level and Your Diastolic Blood Pressure is Below Normal Level')

    if info_dia < 80:
        #insert Alert Module function here:
        return ('Your Diastolic Blood Pressure is Below Normal Level')
    if info_sys > 120:
        #insert Alert Module function here:
        return ('Your Systolic Blood Pressure is Above Normal Level')
    return 0

def heart_rate_info(rate):
    if not isinstance(rate, (int,float)):
        return "Please Enter a Proper Value"
    if rate < 55:
        #insert Alert Module function here:
        return ('Your Heart Rate is Below Normal')
    elif rate > 100:
        #insert Alert Module function here:
        return ('Your Heart Rate is Above Normal')
    return 0

def oximeter_info(o2_rate):
    if not isinstance(o2_rate, (int,float)):
        return "Please Enter a Proper Value"
    if o2_rate < 95:
        #insert Alert Module function here:
        return ('Your Blood Oxygen is Below Normal')
    elif o2_rate > 100:
        #insert Alert Module function here:
        return ('Your Blood Oxygen is Above Normal')
    return 0

def weight_info(weight):
    if not isinstance(weight, (int,float)):
        return "Please Enter a Proper Value"
    return 0

def glucometer_info(Blood):
    if not isinstance(Blood, (int,float)):
        return "Please Enter a Proper Value"
    if Blood < 140:
        #insert Alert Module function here:
        return ('Your Blood Sugar is Below Normal')
    elif Blood > 200:
        #insert Alert Module function here:
        return ('Your Blood Sugar is Above Normal')
    return 0

# Error Codes
error_code=check_type(data['Devices'])
if error_code!=0:
    print(error_code, "1")
error_code = temperature_info(Therometer_info)
if error_code!=0:
    print(error_code, "2")

error_code = blood_pressure_info(Blood_Pressure_Reader_info_sys,Blood_Pressure_Reader_info_dia)
if error_code!=0:
    print(error_code, "3")

error_code = heart_rate_info(Heart_rate_monitor_info)
if error_code!=0:
    print(error_code, "4")

error_code = oximeter_info(Oximeter_details)
if error_code!=0:
    print(error_code, "5")

error_code = weight_info(Weight_Scale_info)
if error_code!=0:
    print(error_code, "6")
error_code = glucometer_info(Glucometer_details)
if error_code!=0:
    print(error_code, "7")

