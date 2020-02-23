from lifxlan import LifxLAN

lifx = LifxLAN(7)
group = lifx.get_devices_by_group("Office")
devices = group.get_device_list()

print("\nFound {} light(s):\n".format(len(devices)))
for d in devices:
    try:
        print(d)
    except:
        pass