# check_interfaces.py
from scapy.arch.windows import get_windows_if_list

print("Available Interfaces (friendly names):\n")
for iface in get_windows_if_list():
    print(f"Name: {iface['name']}")
    print(f"  Description: {iface['description']}")
    print(f"  GUID: {iface['guid']}")
    print()