import datetime
import logging
from constants import *


class DeviceBase:
    def __init__(self, device_id, device_manager, device_config):
        self.device_id = device_id
        self.device_manager = device_manager
        self.device_config = device_config
        # don't send unless the Controller asks it to send
        self.can_send = False

    def send_payload(self, payload):
        if self.can_send is False:
            logging.info("send_payload: will not send. can_send == False")
            return
        payload[FROM] = self.device_id
        payload[TIMESTAMP] = str(datetime.datetime.now())
        self.device_manager.send(payload)

    def pause_events(self):
        logging.info("pause_events")
        self.can_send = False

    def resume_events(self):
        logging.info("resume_events")
        self.can_send = True

