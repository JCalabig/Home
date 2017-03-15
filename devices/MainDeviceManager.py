import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.DefaultLogger import Log
import RPi.GPIO as gpio

from DeviceManager import DeviceManager
from devices.TimedBuzzer import buzzer_config
from devices.MotionDetector import motion_detector_config
from devices.dht11_device import dht11_config
from devices.DeviceHeartbeat import DeviceHeartbeat


# initialize gpio
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
gpio.cleanup()

machine_id = "iot1"
device_config = {
    "dht11": dht11_config,
    "kitchenLights1": motion_detector_config,
    "buzzer1": buzzer_config
}

manager = DeviceManager(machine_id, device_config)
heartbeat = DeviceHeartbeat(machine_id, ("kitchenLights1", "dht11"))
try:
    manager.block_receive()
    manager.cleanup()
    heartbeat.cleanup()
except Exception:
    Log.error("Exception", exc_info=1)
