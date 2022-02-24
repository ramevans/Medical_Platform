import requests

BASE = "http://127.0.0.1:5000/"


response = requests.put(BASE + "Devices/Therometer", {
        "Device Name": "Therometer",
        "Device MAC Address": "9",
        "User": "patient",
        "Temperature": 98 
    } )
print(response.json())
input()
response = requests.get(BASE + "Devices/Therometer")
print(response.json())
