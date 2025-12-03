## Cisco NDFC Interface Automation Scripts

The scripts in this directory are used to **bulk-create interfaces on Cisco NDFC (Nexus Dashboard Fabric Controller)**.  
The goal is to quickly provision **Ethernet** or **Port-Channel** interfaces with the same policy on multiple devices and a given port range using an inventory file.

- **`eth_interface.py`**: Assign the policy to **Ethernet1/x** interfaces on the specified devices for the given port range.
- **`po_interface.py`**: Creates **Port-channelX** interfaces with the policy on the specified devices for the given port range.

---

## Requirements

- Python 3.8+ (any recent 3.x version is recommended)
- Python packages:
  - `requests`

Installation (optionally inside a virtual environment):

```bash
python3 -m venv venv
source venv/bin/activate
pip install requests
```

---

## Inventory File Format

Both scripts ask for an **inventory file name** (`Inventory file name:`).  
Each line is expected to be `;` separated, for example:

```text
<mgmt_IP>;<device_name>;<device_serial_number>
```

The important part is:

- **3rd field** → used as `serialNumber` (device serial in NDFC)

---

## Shared Workflow

Both scripts follow the same high-level flow:

1. **User inputs**:
   - NDFC IP address
   - Username / Password
   - Policy name
   - Fabric name
   - Inventory file name
   - Port ID start and end (e.g. 1–48)
2. The script verifies that the inventory file exists.
3. A `requests.Session` is created and used to log in to NDFC.
4. For each line in the inventory file:
   - The device serial number is read.
   - For each port in the given range, an API call is sent to NDFC.
5. For each interface, the script prints the HTTP status code and the first 100 characters of the response body.

---

## Using `eth_interface.py`

This script assign the policy to **Ethernet1/x** interfaces for the given port range.

Run:

```bash
cd Cisco_NDFC_Scripts
python3 eth_interface.py
```

You will be prompted for:

- `NDFC IP address:`
- `Username:`
- `Password:` (not echoed)
- `Policy Name:`
- `Fabric Name:`
- `Inventory file name:` (e.g. `inventory.txt`)
- `Port ID start:` (e.g. `1`)
- `Port ID end:` (e.g. `48`)

For each device and port, the script sends a request to NDFC with:

- Interface name: `Ethernet1/<port_id>`
- `interfaceType`: `INTERFACE_ETHERNET`
- `nvPairs` contains at least `INTF_NAME` and `BBVERSION`.

Example output:

```text
Leaf-101 Ethernet1/1 - Status: 200
Success: {"result":"success", ...}
Leaf-101 Ethernet1/2 - Status: 400
Error response: {...}
```

---

## Using `po_interface.py`

This script creates **Port-channelX** interfaces with the policy for the given port range.

Run:

```bash
cd Cisco_NDFC_Scripts
python3 po_interface.py
```

You will be prompted for:

- `NDFC IP address:`
- `Username:`
- `Password:`
- `Policy Name:`
- `Fabric Name:`
- `Inventory file name:`
- `Port ID start:`
- `Port ID end:`

For each device and each port-channel, the script sends a request to NDFC with:

- Interface name: `Port-channel<port_id>`
- `interfaceType`: `INTERFACE_PORT_CHANNEL`
- `nvPairs` contains (among others):
  - `PC_MODE` = `active`
  - `BPDUGUARD_ENABLED` = `true`
  - `PORTTYPE_FAST_ENABLED` = `true`
  - `MTU` = `jumbo`
  - `SPEED` = `Auto`
  - `PO_ID` = `Port-channel<port_id>`
  - Other fields: `ACCESS_VLAN`, `DESC`, `CONF`, `ADMIN_STATE`, `ENABLE_NETFLOW`, `NETFLOW_MONITOR`

Example output:

```text
Leaf-101 Port-channel1 - Status: 200
Success: {"result":"success", ...}
Leaf-101 Port-channel2 - Status: 500
Error response: {...}
```

---

## Error Handling and Validation

- **Login failure**: If the login HTTP status code is not 200, the script prints the response and exits.
- **Inventory file not found**: If the file does not exist, the script exits immediately with an error message.
- **Invalid port ID**:
  - Non-numeric input, or
  - Start port ID > End port ID  
  In both cases, the script prints an error and exits.
- **Invalid line format**: Lines with fewer than 3 fields are skipped with a warning.

---


