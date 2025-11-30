from requests import Session
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import time
import getpass
import os
import sys

# Get NDFC IP address from user
ndfc_ip = input("NDFC IP address: ")

url = f'https://{ndfc_ip}/login'
global_interface_url = f"https://{ndfc_ip}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/globalInterface/pti?isMultiEdit=true"

# Get username and password from user
username = input("Username: ")
password = getpass.getpass("Password: ")

# Get policy name and fabric name from user
policy_name = input("Policy Name: ")
fabric_name = input("Fabric Name: ")

# Get inventory file name from user
inventory_file = input("Inventory file name: ")

# Get port ID range from user
try:
    port_id_start = int(input("Port ID start: "))
    port_id_end = int(input("Port ID end: "))
    if port_id_start > port_id_end:
        print("Error: Start port ID must be less than or equal to end port ID")
        sys.exit(1)
except ValueError:
    print("Error: Port ID must be a valid integer")
    sys.exit(1)

payload = {
  "userName": username,
  "userPasswd": password,
  "domain": "local"
}

# Validate inventory file exists
if not os.path.exists(inventory_file):
    print(f"Error: Inventory file '{inventory_file}' not found")
    sys.exit(1)

# Create session once and reuse it
s = Session()
s.verify = False
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Login once
print("Logging in...")
response = s.post(url=url, json=payload, verify=False)
if response.status_code != 200:
    print(f"Error: Login failed with status code {response.status_code}")
    print(f"Response: {response.text}")
    sys.exit(1)
print("Login successful!")

# Process inventory file
with open(inventory_file, 'r') as f:
    for line in f.readlines():
        if not line.strip():  # Skip empty lines
            continue
        try:
            splittedline = line.split(';')
            if len(splittedline) < 3:
                print(f"Warning: Skipping invalid line: {line.strip()}")
                continue
            
            for port_id in range(port_id_start, port_id_end + 1):
                interface_name = "Ethernet1/" + str(port_id)
                post_eth = {
                    "policy": policy_name,
                    "interfaces": [{
                        "serialNumber": splittedline[2].strip(),
                        "fabricName": fabric_name,
                        "ifName": interface_name,
                        "interfaceType": "INTERFACE_ETHERNET",
                        "nvPairs": {"BBVERSION": "", "INTF_NAME": interface_name}
                    }]
                }

                eth_create_response = s.post(global_interface_url, json=post_eth, verify=False)
                print(f"{splittedline[1].strip()} {interface_name} - Status: {eth_create_response.status_code}")
                if eth_create_response.status_code != 200:
                    print(f"Error response: {eth_create_response.text}")
                else:
                    print(f"Success: {eth_create_response.content.decode('utf-8')[:100]}")
        except Exception as e:
            print(f"Error processing line '{line.strip()}': {str(e)}")
            continue
