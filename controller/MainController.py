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


class DisplayThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._quit = False
        self.lcd = display()

    def quit(self):
        self._quit = True
        self.join()

    def run(self):
        while not self._quit:
            message = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
            self.lcd.lcd_display_string(message, 1)
            time.sleep(1)
        self.lcd.lcd_display_string("bye", 2)


# lcd_thread = DisplayThread()
try:
    # lcd_thread.start()
    controller = Controller("controller1", [ControlledObject(home_monitor_config)])
    controller.on_receive({
        EVENT: BEGIN
    }, "events")
    controller.block_receive()
except Exception:
    Log.info("Exception", exc_info=1)
finally:
    # lcd_thread.quit()
    pass
