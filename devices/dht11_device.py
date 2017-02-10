import DHT11.dht11 as dht11
import time
from constants import *
import logging
from DeviceBase import DeviceBase

# dht 11 power pin to be just +3.3VCC

class Dht11Device(DeviceBase):
    def __init__(self, device_id, device_manager, device_config):
        super(self.__class__, self).__init__(device_id, device_manager, device_config)
        self._dht11 = dht11.DHT11(pin=device_config["inputPin"])
        # can always send data to controller
        self.can_send = True

    def un_init(self):
        self._dht11 = None

    def read(self):
        logging.info("dht11 read")
        try:
            while True:
                result = self._dht11.read()
                if result.is_valid():
                    self.send_payload({
                        TYPE: DATA,
                        "tempC": result.temperature,
                        "tempF": result.temperature*1.8 + 32.0,
                        "humidity": result.humidity,
                        "optionalMessage": None
                    })
                    return
                else:
                    logging.info("Retrying")
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt")

dht11_config = {
    "inputPin": 22,
    "read": Dht11Device.read,
    "pauseEvents": Dht11Device.pause_events,
    "resumeEvents": Dht11Device.resume_events,
    # mandatory
    DEVICE_OBJECT: None,
    CONSTRUCTOR: Dht11Device,
    DE_CONSTRUCTOR: Dht11Device.un_init
}


