from gpiozero import MotionSensor, LED
import RPi.GPIO as gpio
from utils.DefaultLogger import Log
from constants import *
from utils.Execution import IntervalExecution
from DeviceBase import DeviceBase


class MotionDetector(DeviceBase):
    _RELAY_DISCONNECT = gpio.LOW
    _RELAY_CONNECT = gpio.HIGH
    _RELAY_PINS = [23, 24]
    _MOTION_SENSOR_INPUT_PIN = 4
    _LIGHT_PIN = 26
    _RELAY_DISCONNECT_SECONDS = 10

    def __init__(self, device_id, device_manager, device_config):
        DeviceBase.__init__(self, device_id, device_manager, device_config)
        for pin in MotionDetector._RELAY_PINS:
            gpio.setup(pin, gpio.OUT)
            gpio.output(pin, MotionDetector._RELAY_DISCONNECT)
        self._timer = IntervalExecution(self.relay_disconnect, MotionDetector._RELAY_DISCONNECT_SECONDS,
                                        start=True, tag="MotionDetector")
        self._light = LED(MotionDetector._LIGHT_PIN)
        self._sensor = MotionSensor(MotionDetector._MOTION_SENSOR_INPUT_PIN)
        self._sensor.when_motion = self._when_motion
        self._sensor.when_no_motion = self._when_no_motion

    def cleanup(self):
        self._timer.quit()
        self.relay_disconnect()
        self._light.off()
        self._light.close()
        self._light = None
        self._sensor.when_motion = None
        self._sensor.when_no_motion = None
        self._sensor.close()
        self._sensor = None

    def _when_motion(self):
        Log.debug("motion started")
        self.relay_connect()
        self._light.on()
        self.send_payload({
            TYPE: EVENT,
            EVENT: "motionDetected"
        })

    def _when_no_motion(self):
        Log.debug("motion stopped")
        self._light.off()

    def relay_disconnect(self):
        Log.debug("MotionDetector relay_disconnected")
        for pin in MotionDetector._RELAY_PINS:
            gpio.output(pin, MotionDetector._RELAY_DISCONNECT)

    def relay_connect(self):
        Log.debug("MotionDetector relay_connected")
        for pin in MotionDetector._RELAY_PINS:
            gpio.output(pin, MotionDetector._RELAY_CONNECT)
        self._timer.reset()


motion_detector_config = {
    "off": MotionDetector.relay_disconnect,
    "on": MotionDetector.relay_connect,

    "pauseEvents": MotionDetector.pause_events,
    "resumeEvents": MotionDetector.resume_events,

    # mandatory
    DEVICE_OBJECT: None,
    CONSTRUCTOR: MotionDetector,
    CLEANUP: MotionDetector.cleanup
}
