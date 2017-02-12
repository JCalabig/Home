import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import logging
from constants import *
from rabbitmq.MessageQueue import MessageQueue

logging.root.setLevel(logging.INFO)


class DeviceManager:
    def send(self, payload):
        self._message_queue.send(payload)

    def block_receive(self):
        self._message_queue.block_receive()
        self.cleanup()

    def __init__(self, machine_id, device_config):
        self._machine_id = machine_id
        self.devices = device_config
        self._message_queue = MessageQueue(self._machine_id, send_key="events",
                                           receive_key="commands", on_receive=self.on_receive)
        for device_name in self.devices:
            try:
                logging.info("initializing %s", device_name)
                device_config = self.devices[device_name]
                device_config[DEVICE_OBJECT] = device_config[CONSTRUCTOR](self._machine_id, self, device_config)
            except Exception:
                logging.error("Exception on initializing %s", device_name, exc_info=1)
                raise

    def cleanup(self):
        for device_name in self.devices:
            try:
                logging.info("un_initializing %s", device_name)
                device_config = self.devices[device_name]
                device_config[DE_CONSTRUCTOR](device_config[DEVICE_OBJECT])
            except Exception:
                logging.error("Exception on un_initialize %s", device_name, exc_info=1)
                raise

    def on_receive(self, event, routing_key):
        if routing_key != "commands":
            logging.info("ignoring %s", routing_key)
            return
        if event.get(TARGET, self._machine_id) != self._machine_id:
            return
        op_code = event[OP_CODE]
        logging.info("on_receive event: {}".format(str(event)))
        device_name = event[DEVICE]
        if device_name not in self.devices:
            logging.error("device id not present %s", device_name)
            return
        device_config = self.devices[device_name]
        if op_code not in device_config:
            logging.error("op code not recognized: %s", op_code)
            return
        device_config[op_code](device_config[DEVICE_OBJECT])


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    dm = DeviceManager("me")
    try:
        print ("test")
    except:
        logging.info("Exception", exc_info=1)
    finally:
        dm.cleanup()

