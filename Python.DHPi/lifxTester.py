from lifxlan import LifxLAN
from time import sleep
import sys

lifx = LifxLAN(7)
officeLightGroup = lifx.get_devices_by_group("Office")
officeLights = officeLightGroup.get_device_list()
officeOne = next(filter(lambda l: l.get_label() == "Office One", officeLights), None)
officeTwo = next(filter(lambda l: l.get_label() == "Office Two", officeLights), None)
officeThree = next(filter(lambda l: l.get_label() == "Office Three", officeLights), None)
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




if len(officeLights) < 3:
    print(f"Did not discover all office lights! ({len(officeLights)} of 3)")
    sys.exit(-1)

print("Turning lights off..")
officeLightGroup.set_power("off", duration=2000)
print("Command sent, sleeping...")
sleep(2)
print("Woke up")
lightOnSequence()
print("Done!")