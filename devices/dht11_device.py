import DHT11.dht11 as dht11
import time
from constants import *
from utils.DefaultLogger import Log
from DeviceBase import DeviceBase


class Dht11Device(DeviceBase):
    _INPUT_PIN = 22

    def __init__(self, device_id, device_manager, device_config):
        DeviceBase.__init__(self, device_id, device_manager, device_config, begin_send=True)
        self._dht11 = dht11.DHT11(pin=Dht11Device._INPUT_PIN)

    def cleanup(self):
        self._dht11 = None

    def read(self):
        Log.info("dht11 reading")
        while True:
            result = self._dht11.read()
            if result.is_valid():
                self.send_payload({
                    TYPE: DATA,
                    "tempC": result.temperature,
                    "tempF": result.temperature * 1.8 + 32.0,
                    "humidity": result.humidity,
                    "optionalMessage": None
                })
                return
            else:
                Log.debug("Retrying")
            time.sleep(1)


dht11_config = {
    "read": Dht11Device.read,
    "pauseEvents": Dht11Device.pause_events,
    "resumeEvents": Dht11Device.resume_events,
    # mandatory
    DEVICE_OBJECT: None,
    CONSTRUCTOR: Dht11Device,
    CLEANUP: Dht11Device.cleanup
}
