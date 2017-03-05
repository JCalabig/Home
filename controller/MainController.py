import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import datetime
from utils.DefaultLogger import Log
import threading
import time

# from I2C_LCD.I2C_LCD_driver import lcd as display
from config import home_monitor_config
from constants import *
from controller.Controller import Controller
from utils.ControlledObject import ControlledObject


controller = None
try:
    controller = Controller("controller1", [ControlledObject(home_monitor_config)])
    controller.on_receive({
        EVENT: BEGIN
    }, "events")
    controller.block_receive()
except Exception:
    Log.info("Exception", exc_info=1)
finally:
    pass
