from gpiozero import MotionSensor, LED
import RPi.GPIO as gpio
import logging
from constants import *
from utils.Countdown import CountdownTimer
from DeviceBase import DeviceBase


class KitchenLight(DeviceBase):
    def __init__(self, device_id, device_manager, device_config):
        DeviceBase.__init__(self, device_id, device_manager, device_config)
        for pin in self.device_config["relayPins"]:
            gpio.setup(pin, gpio.OUT)
            gpio.output(pin, gpio.HIGH)
        self._timer = CountdownTimer(10, self.off, name="kitchen light")
        self._timer.start()
        self._motion_sensor_led = LED(device_config["pirLedPin"])
        self._motion_sensor = MotionSensor(device_config["pirInputPin"])
        self._motion_sensor.when_motion = self._when_motion
        self._motion_sensor.when_no_motion = self._when_no_motion

    def cleanup(self):
        self._timer.quit()
        self._timer.join()
        for pin in self.device_config["relayPins"]:
            gpio.output(pin, gpio.LOW)
        self._motion_sensor_led.off()
        self._motion_sensor_led.close()
        self._motion_sensor_led = None
        self._motion_sensor.when_motion = None
        self._motion_sensor.when_no_motion = None
        self._motion_sensor.close()
        self._motion_sensor = None

    def _when_motion(self):
        logging.debug("motion started")
        self.on()
        self._motion_sensor_led.on()
        self.send_payload({
            TYPE: EVENT,
            EVENT: "motionDetected"
        })

    def _when_no_motion(self):
        logging.debug("motion stopped")
        self._motion_sensor_led.off()

    def off(self):
        logging.debug("kitchen lights off")
        for pin in self.device_config["relayPins"]:
            gpio.output(pin, gpio.HIGH)

    def on(self):
        logging.debug("kitchen lights on")
        for pin in self.device_config["relayPins"]:
            gpio.output(pin, gpio.LOW)
        self._timer.reset()

kitchen_lights_config = {
    "relayPins": [23, 24],
    "off": KitchenLight.off,
    "on": KitchenLight.on,

    "pirInputPin": 4,
    "pirLedPin": 26,
    "pauseEvents": KitchenLight.pause_events,
    "resumeEvents": KitchenLight.resume_events,

    # mandatory
    DEVICE_OBJECT: None,
    CONSTRUCTOR: KitchenLight,
    DE_CONSTRUCTOR: KitchenLight.cleanup
}


