# ------------------------- DEFINE IMPORTS ---------------------------
from __future__ import print_function
import argparse

# ------------------------- DEFINE ARGUMENTS -------------------------
# argParser.add_argument("-a", "--min-area", type=int, default=500, help="Minimum area size before motion detection")
#argParser.add_argument('--ononly', dest='ononly', action='store_true', help="Disable turning lights off command")
#argParser.add_argument('--remote', dest='interactive', action='store_false', help="Disable Pi hardware specific functions")
#argParser.set_defaults(interactive=True)

argParser = argparse.ArgumentParser()
args = vars(argParser.parse_args())
print(f"Args: {args}")

# ------------------------- DEFINE GLOBALS ---------------------------

# ------------------------- DEFINE FUNCTIONS -------------------------

# ------------------------- DEFINE INITIALIZE ------------------------

# ------------------------- DEFINE RUN -------------------------------
try:
    print("Run")
except KeyboardInterrupt:
    print("KeyboardInterrupt caught! Cleaning up...")