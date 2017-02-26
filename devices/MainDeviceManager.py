from utils.DefaultLogger import Log
import RPi.GPIO as gpio

from DeviceManager import DeviceManager
from devices.TimedBuzzer import buzzer_config
from devices.MotionDetector import motion_detector_config
from devices.dht11_device import dht11_config


# initialize gpio
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
gpio.cleanup()

manager = DeviceManager("iot1", {
    "dht11": dht11_config,
    "kitchenLights1": motion_detector_config,
    "buzzer1": buzzer_config
})
try:
    manager.block_receive()
except Exception:
    Log.error("Exception", exc_info=1)
