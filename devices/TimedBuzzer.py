import RPi.GPIO as gpio
from utils.DefaultLogger import Log
from constants import *
from utils.Countdown import CountdownTimer


class TimedBuzzer:
    _INPUT_PIN = 27
    _DURATION_SECONDS = 2

    def __init__(self, device_id, device_manager, device_config):
        self._device_id = device_id
        self._device_manager = device_manager
        self._device_config = device_config
        gpio.setup(TimedBuzzer._INPUT_PIN, gpio.OUT)
        self._timer = CountdownTimer(TimedBuzzer._DURATION_SECONDS, self.off, name="timed buzzer")
        self._timer.start()

    def cleanup(self):
        self._timer.quit()
        self._timer.join()
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
