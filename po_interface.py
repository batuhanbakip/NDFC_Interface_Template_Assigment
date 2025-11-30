from requests import Session
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import getpass
import copy
import os
import sys

# Get NDFC IP address from user
ndfc_ip = input("NDFC IP address: ")

url = f'https://{ndfc_ip}/login'
global_interface_url = f"https://{ndfc_ip}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/globalInterface"

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

post_data_po = { 
  "policy": policy_name,
  "interfaceType":"INTERFACE_PORT_CHANNEL",
  "interfaces":[
    {
      "serialNumber":"",
      "interfaceType":"INTERFACE_PORT_CHANNEL",
      "fabricName": fabric_name,
      "ifName":"",
      "nvPairs":{
        "MEMBER_INTERFACES":"",
        "PC_MODE":"active",
        "BPDUGUARD_ENABLED":"true",
        "PORTTYPE_FAST_ENABLED":"true",
        "MTU":"jumbo",
        "SPEED":"Auto",
        "ACCESS_VLAN":"",
        "DESC":"",
        "CONF":"",
        "ADMIN_STATE":"true",
        "ENABLE_NETFLOW":"false",
        "NETFLOW_MONITOR":"",
        "PO_ID":""
      }
   }
 ],
 "skipResourceCheck":"false"
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
                # Use deepcopy to avoid modifying the original dictionary
                post_po = copy.deepcopy(post_data_po)
                post_po['interfaces'][0]['serialNumber'] = splittedline[2].strip()
                port_channel = "Port-channel" + str(port_id)
                post_po['interfaces'][0]['ifName'] = port_channel
                post_po['interfaces'][0]['nvPairs']['PO_ID'] = port_channel

                po_create_response = s.post(global_interface_url, json=post_po, verify=False)
                print(f"{splittedline[1].strip()} {port_channel} - Status: {po_create_response.status_code}")
                if po_create_response.status_code != 200:
                    print(f"Error response: {po_create_response.text}")
                else:
                    print(f"Success: {po_create_response.content.decode('utf-8')[:100]}")
        except Exception as e:
            print(f"Error processing line '{line.strip()}': {str(e)}")
            continue


