import RPi.GPIO as gpio
from utils.DefaultLogger import Log
from constants import *
from utils.Execution import IntervalExecution


class TimedBuzzer:
    _INPUT_PIN = 27
    _DURATION_SECONDS = 2

    def __init__(self, device_id, device_manager, device_config):
        self._device_id = device_id
        self._device_manager = device_manager
        self._device_config = device_config
        gpio.setup(TimedBuzzer._INPUT_PIN, gpio.OUT)
        self._timer = IntervalExecution(self.off, TimedBuzzer._DURATION_SECONDS, tag="TimedBuzzer", start=True)

    def cleanup(self):
        self._timer.quit()
        gpio.output(TimedBuzzer._INPUT_PIN, False)

    def off(self):
        Log.info("buzzer off")
        gpio.output(TimedBuzzer._INPUT_PIN, False)

    def on(self):
        Log.info("buzzer on")
        gpio.output(TimedBuzzer._INPUT_PIN, True)
        self._timer.reset()

buzzer_config = {
    "off": TimedBuzzer.off,
    "on": TimedBuzzer.on,

    # mandatory
    DEVICE_OBJECT: None,
    CONSTRUCTOR: TimedBuzzer,
    CLEANUP: TimedBuzzer.cleanup
}
