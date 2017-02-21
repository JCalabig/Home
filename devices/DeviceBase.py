import datetime
import logging
from constants import *


class DeviceBase:
    def __init__(self, device_id, device_manager, device_config, send_max=512, begin_send=False):
        self.device_id = device_id
        self.device_manager = device_manager
        self.device_config = device_config
        self._max_send = send_max
        self._send_count = self._max_send if begin_send is True else 0

    def send_payload(self, payload):
        self._send_count -= 1
        logging.info("send_payload: send_count remaining = {}".format(self._send_count))
        if self._send_count <= 0:
            self._send_count = -1
            logging.info("send_payload: will not send.")
            return
        payload[FROM] = self.device_id
        payload[TIMESTAMP] = str(datetime.datetime.now())
        self.device_manager.send(payload)

    def pause_events(self):
        logging.info("pause_events")
        self._send_count = 0

    def resume_events(self):
        logging.info("resume_events")
        self._send_count = self._max_send

