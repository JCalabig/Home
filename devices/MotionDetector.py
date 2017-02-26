from gpiozero import MotionSensor, LED
import RPi.GPIO as gpio
from utils.DefaultLogger import Log
from constants import *
from utils.Countdown import CountdownTimer
from DeviceBase import DeviceBase


class MotionDetector(DeviceBase):
    _RELAY_DISCONNECT = gpio.LOW
    _RELAY_CONNECT = gpio.HIGH

    def __init__(self, device_id, device_manager, device_config):
        DeviceBase.__init__(self, device_id, device_manager, device_config)
        for pin in self.device_config["relayPins"]:
            gpio.setup(pin, gpio.OUT)
            gpio.output(pin, MotionDetector._RELAY_DISCONNECT)
        self._timer = CountdownTimer(10, self.relay_disconnected, name="MotionDetector")
        self._timer.start()
        self._light = LED(device_config["pirLedPin"])
        self._sensor = MotionSensor(device_config["pirInputPin"])
        self._sensor.when_motion = self._when_motion
        self._sensor.when_no_motion = self._when_no_motion

    def cleanup(self):
        self._timer.quit()
        self._timer.join()
        self._light.relay_disconnected()
        self._light.close()
        self._light = None
        self._sensor.when_motion = None
        self._sensor.when_no_motion = None
        self._sensor.close()
        self._sensor = None

    def _when_motion(self):
        Log.debug("motion started")
        self.relay_connected()
        self._light.on()
        self.send_payload({
            TYPE: EVENT,
            EVENT: "motionDetected"
        })

    def _when_no_motion(self):
        Log.debug("motion stopped")
        self._light.off()

    def relay_disconnected(self):
        Log.debug("MotionDetector relay_disconnected")
        for pin in self.device_config["relayPins"]:
            gpio.output(pin, MotionDetector._RELAY_DISCONNECT)

    def relay_connected(self):
        Log.debug("MotionDetector relay_connected")
        for pin in self.device_config["relayPins"]:
            gpio.output(pin, MotionDetector._RELAY_CONNECT)
        self._timer.reset()


motion_detector_config = {
    "relayPins": [23, 24],
    "off": MotionDetector.relay_disconnected,
    "on": MotionDetector.relay_connected,

    "pirInputPin": 4,
    "pirLedPin": 26,
    "pauseEvents": MotionDetector.pause_events,
    "resumeEvents": MotionDetector.resume_events,

    # mandatory
    DEVICE_OBJECT: None,
    CONSTRUCTOR: MotionDetector,
    DE_CONSTRUCTOR: MotionDetector.cleanup
}
