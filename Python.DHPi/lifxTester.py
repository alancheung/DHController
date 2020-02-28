from lifxlan import LifxLAN
from time import sleep
import sys

lifx = LifxLAN(7)
officeLightGroup = lifx.get_devices_by_group("Office")
officeLights = officeLightGroup.get_device_list()

if len(officeLights) < 3:
    print(f"Did not discover all office lights! ({len(officeLights)} of 3)")
    sys.exit(-1)

print("Turning lights on..")
officeLightGroup.set_power("on", duration=10000)
print("Command sent, sleeping...")
sleep(10)
print("Woke up")
officeLightGroup.set_power("off", rapid=True)
print("Turning lights off...")