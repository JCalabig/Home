import RPi.GPIO as gpio
import logging
from constants import *
from utils.Countdown import CountdownTimer


class TimedBuzzer:
    def __init__(self, device_id, device_manager, device_config):
        self._device_id = device_id
        self._device_manager = device_manager
        self._device_config = device_config
        gpio.setup(self._device_config["pin"], gpio.OUT)
        self._timer = CountdownTimer(2, self.off, name="timed buzzer")
        self._timer.start()

    def un_init(self):
        self._timer.quit()
        self._timer.join()
        gpio.output(self._device_config["pin"], False)

    def off(self):
        logging.info("buzzer off")
        gpio.output(self._device_config["pin"], False)

    def on(self):
        logging.info("buzzer on")
        gpio.output(self._device_config["pin"], True)
        self._timer.reset()

buzzer_config = {
    "pin": 27,
    "off": TimedBuzzer.off,
    "on": TimedBuzzer.on,

    # mandatory
    DEVICE_OBJECT: None,
    CONSTRUCTOR: TimedBuzzer,
    DE_CONSTRUCTOR: TimedBuzzer.un_init
}


