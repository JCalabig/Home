import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import datetime
from utils.DefaultLogger import Log
from ControllerHeartbeat import ControllerHeartbeat

# from I2C_LCD.I2C_LCD_driver import lcd as display
from config import home_monitor_config
from constants import *
from controller.Controller import Controller
from utils.ControlledObject import ControlledObject


controller = None
machine_id = "controller1"
try:
    controller = Controller(machine_id, [ControlledObject(home_monitor_config)])
    controller.on_receive({
        EVENT: BEGIN
    }, "events")
    heartbeat = ControllerHeartbeat(machine_id)
    controller.block_receive()
    heartbeat.cleanup()
    controller.cleanup()
except Exception:
    Log.info("Exception", exc_info=1)
