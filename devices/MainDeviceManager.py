import logging
import RPi.GPIO as gpio

from DeviceManager import DeviceManager
from devices.TimedBuzzer import buzzer_config
from devices.KitchenLights import kitchen_lights_config
from devices.dht11_device import dht11_config


logging.root.setLevel(logging.INFO)

# initialize gpio
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
gpio.cleanup()

manager = DeviceManager("iot1", {
    "dht11": dht11_config,
    "kitchenLights1": kitchen_lights_config,
    "buzzer1": buzzer_config
})
try:
    manager.block_receive()
except Exception:
    logging.info("Exception", exc_info=1)
