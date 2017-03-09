import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import uuid
from utils.DefaultLogger import Log
from ControllerHeartbeat import ControllerHeartbeat

# from I2C_LCD.I2C_LCD_driver import lcd as display
from config import home_monitor_config
from constants import *
from controller.Controller import Controller
from utils.ControlledObject import ControlledObject

tag = str(uuid.uuid4())
Log.info("main thread begin (track:%s)", tag)
controller = None
heartbeat = None
machine_id = "controller1"
try:
    controller = Controller(machine_id, [ControlledObject(home_monitor_config)])
    controller.on_receive({
        EVENT: BEGIN
    }, "events")
    heartbeat = ControllerHeartbeat(machine_id)
    controller.block_receive()
except:
    Log.info("Exception", exc_info=1)
heartbeat.cleanup()
controller.cleanup()
Log.info("main thread exit (track:%s)", tag)
