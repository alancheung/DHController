from lifxlan import LifxLAN
from datetime import datetime, time
from time import sleep
import sys

print(datetime.now().time())
if datetime.now().time() <= time(16, 33, 0, 0):
    print("Yes")
else:
    print("No")

def lightOnSequence():
    print("One on!")
    officeOne.set_power("on", duration=5000)
    sleep(1)
    print("Two on!")
    officeTwo.set_power("on", duration=4000)
    sleep(1)
    print("Three on!")
    officeThree.set_power("on", duration=3000)
    sleep(1)

sleep(1)
lifx = LifxLAN(7)
officeLightGroup = lifx.get_devices_by_group("Office")
officeLights = officeLightGroup.get_device_list()
officeOne = lifx.get_devices_by_name("Office One")
officeTwo = lifx.get_devices_by_name("Office Two")
officeThree = lifx.get_devices_by_name("Office Three")

if len(officeLights) < 3:
    print(f"Did not discover all office lights! ({len(officeLights)} of 3)")
    sys.exit(-1)
else:
    devices = lifx.get_lights()
    print("\nFound {} light(s):\n".format(len(devices)))
    for d in devices:
        try:
        	print(d)
        except:
            pass

