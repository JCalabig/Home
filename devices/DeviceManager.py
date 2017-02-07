import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import copy
import logging

import RPi.GPIO as gpio

from constants import *
from devices.TimedBuzzer import buzzer_config
from devices.KitchenLights import kitchen_lights_config
from devices.dht11_device import dht11_config
from rabbitmq.MessageQueue import MessageQueue

logging.root.setLevel(logging.INFO)


class DeviceManager:
    device_to_config = {
        "dht11": dht11_config,
        "kitchenLights1": kitchen_lights_config,
        "buzzer1": buzzer_config
    }

    def send(self, payload):
        self._message_queue.send(payload)

    def block_receive(self):
        self._message_queue.block_receive()

    def on_send(self, event):
        # find all interested devices!!
        return

    def __init__(self, machine_id):
        self._machine_id = machine_id
        self.devices = {}
        self._message_queue = MessageQueue(self._machine_id, send_key="events", on_send=self.on_send,
                                           receive_key="commands", on_receive=self.on_receive)
        self.actions= {
            "initialize": self.initialize,
            "unititialize" : self.un_initialize
        }
        device_list = []
        for device_name in self.device_to_config:
            device_list.append(device_name)
        self.on_receive({
            OP_CODE: "initialize",
            DEVICES: device_list
        }, "commands")

    def device_name_format(self, device_name):
        return "{}.{}".format(self._machine_id, device_name)

    def initialize(self, params):
        if len(self.devices) > 0:
            logging.info("skipping configuration")
            return
        logging.info("initialize devices")

        # initialize gpio
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.cleanup()
        
        for device_name in params[DEVICES]:
            device_id = self.device_name_format(device_name)
            self.devices[device_id] = copy.deepcopy(self.device_to_config[device_name])
        for device_id in self.devices:
            device_config = self.devices[device_id]
            try:
                device_config[DEVICE_OBJECT] = device_config[CONSTRUCTOR](device_id, self, device_config)
            except:
                logging.error("Exception on initializing %s", device_id, exc_info=1)

    def un_initialize(self, params):
        logging.info("un_initializing devices")
        if len(self.devices) == 0:
            return
        for device_id in self.devices:
            device_config = self.devices[device_id]
            logging.info("un_initializing %s", device_id)
            device_config[DE_CONSTRUCTOR](device_config[DEVICE_OBJECT])
        self.devices = {}

    def cleanup(self):
        self.un_initialize(None)
        self._message_queue.cleanup()

    def on_receive(self, event, routing_key):
        if routing_key != "commands":
            logging.info("ignoring %s", routing_key)
            return
        logging.info(str(event))
        event.setdefault(EVENT, None)
        event.setdefault(TARGET, self._machine_id)
        target = event[TARGET]
        if target != self._machine_id:
            return
        op_code = event[OP_CODE]
        if DEVICE in event:
            device_id = self.device_name_format(event[DEVICE])
            if device_id not in self.devices:
                logging.error("device id not present %s", device_id)
                return
            device_config = self.devices[device_id]
            if op_code not in device_config:
                logging.error("op code not recognized: %s", op_code)
                return
            device_config[op_code](device_config[DEVICE_OBJECT])
            return

        logging.info("on_receive event: {}".format(str(event)))
        if op_code not in self.actions:
            logging.error("op code not recognized as an action: %s", op_code)
            return
        self.actions[op_code](event)


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    dm = DeviceManager("me")
    try:
        print ("test")

    except:
        logging.info("Exception", exc_info=1)
    finally:
        dm.cleanup()

