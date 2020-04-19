from __future__ import print_function
from datetime import datetime, time

ignore = False
start = datetime.now()
while (datetime.now() - start).seconds < 5 and ignore is False:
    print(f"running with {(datetime.now()- start).seconds}")
    ignore = ignore or (datetime.now() - start).seconds == 1
    print(f"{ignore}")
print (f"done: {ignore}")