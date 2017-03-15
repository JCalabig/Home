import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.DefaultLogger import Log
from constants import *
from rabbitmq.Receiver import Receiver
from rabbitmq.Sender import Sender
from config import queue_server, username, password


class DeviceManager:
    def send(self, payload):
        Log.info("device manager sending...")
        self._sender.send(payload)

    def block_receive(self):
        try:
            self._receiver.block_receive()
        except:
            Log.error("Exception", exc_info=1)

    def __init__(self, machine_id, device_config):
        self._machine_id = machine_id
        self.devices = device_config

        receiver_routing_and_exchange = "commands"
        receive_queue_name = "Device_{}_receiver_queue".format(machine_id)
        self._receiver = Receiver(queue_server, username, password, routing_key=receiver_routing_and_exchange,
                                  on_receive=self.on_receive, exchange=receiver_routing_and_exchange,
                                  queue_name=receive_queue_name)

        sender_routing_and_exchange = "events"
        sender_queue_name = "Device_{}_sender_queue".format(machine_id)
        self._sender = Sender(queue_server, username, password, routing_key=sender_routing_and_exchange,
                              exchange=sender_routing_and_exchange, queue_name=sender_queue_name)

        for device_name in self.devices:
            try:
                Log.info("initializing %s", device_name)
                device_config = self.devices[device_name]
                device_config[DEVICE_OBJECT] = device_config[CONSTRUCTOR](self._machine_id, self, device_config)
            except Exception:
                Log.error("Exception on initializing %s", device_name, exc_info=1)
                raise

    def cleanup(self):
        for device_name in self.devices:
            try:
                Log.info("cleanup %s", device_name)
                device_config = self.devices[device_name]
                device_config[CLEANUP](device_config[DEVICE_OBJECT])
            except Exception:
                Log.error("Exception on cleanup %s", device_name, exc_info=1)
                raise
        self._receiver.cleanup()
        self._sender.cleanup()

    def on_receive(self, event, routing_key):
        Log.info("on_receive event1")
        if event.get(TARGET, self._machine_id) != self._machine_id:
            return
        op_code = event[OP_CODE]
        Log.info("on_receive event: {}".format(str(event)))
        device_name = event[DEVICE]
        if device_name not in self.devices:
            Log.error("device id not present %s", device_name)
            return
        device_config = self.devices[device_name]
        if op_code not in device_config:
            Log.error("op code not recognized: %s", op_code)
            return
        device_config[op_code](device_config[DEVICE_OBJECT])
