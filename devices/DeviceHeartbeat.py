import uuid
from utils.DefaultLogger import Log
from constants import *
import threading, time
from rabbitmq.Receiver import Receiver
from rabbitmq.Sender import Sender
from config import queue_server, username, password
from utils.Execution import IntervalExecution


# controller to query for known devices at the beginning
# this list of devices will be used for periodic hearbeat
# devices to send a heartbeat periodically so both sides are autonomous


class DeviceHeartbeat:
    _INTERVAL = 5

    def __init__(self, machine_id, devices):
        self._machine_id = machine_id
        self._devices = devices

        receiver_routing_and_exchange = "commands"
        receive_queue_name = "DeviceHeartbeat_{}_receiver_queue".format(machine_id)
        self._receiver = Receiver(queue_server, username, password, routing_key=receiver_routing_and_exchange,
                                  on_receive=self.on_receive, exchange=receiver_routing_and_exchange,
                                  queue_name=receive_queue_name)

        sender_routing_and_exchange = "events"
        self._sender = Sender(queue_server, username, password, routing_key=sender_routing_and_exchange,
                              exchange=sender_routing_and_exchange)

        self._interval = IntervalExecution(self._interval_action, DeviceHeartbeat._INTERVAL, start=True,
                                           tag="controllerHeartbeatInterval")
        self._max_send = 5
        self._send_count = self._max_send

    def _interval_action(self):
        if self._send_count <= 0:
            self._send_count = -1
            Log.info("DeviceHeartbeat: send_payload: will not send.")
            return
        self._send_count -= 1
        for device in self._devices:
            self._sender.send({
                TYPE: DEVICE_HELLO,
                FROM: self._machine_id,
                DEVICE: device
            })

    def cleanup(self):
        Log.info("DeviceHeartbeat: quitting")
        try:
            self._interval.quit()
            self._sender.cleanup()
            Log.info("DeviceHeartbeat: sleeping 10 secs to sync cleanup")
            time.sleep(10)
        except:
            Log.info("Exception", exc_info=1)
        finally:
            Log.info("DeviceHeartbeat: quitting exited")

    def set_payload_defaults(self, event_payload):
        event_payload.setdefault(TYPE, EVENT)
        event_payload.setdefault(EVENT, None)
        event_payload.setdefault(TARGET, self._machine_id)

    def on_receive(self, event_payload, routing_key):
        self.set_payload_defaults(event_payload)
        if event_payload[TARGET] != self._machine_id:
            return
        Log.info("DeviceHeartbeat: received heartbeat from controller")
        self._send_count = self._max_send
