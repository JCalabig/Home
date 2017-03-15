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

        sender_routing_and_exchange = "events"
        sender_queue_name = "DeviceHeartbeat_{}_sender_queue".format(machine_id)
        self._sender = Sender(queue_server, username, password, routing_key=sender_routing_and_exchange,
                              exchange=sender_routing_and_exchange, queue_name=sender_queue_name)

        self._interval = IntervalExecution(self._interval_action, DeviceHeartbeat._INTERVAL, start=True,
                                           tag="controllerHeartbeatInterval")

    def _interval_action(self):
        for device in self._devices:
            self._sender.send({
                TYPE: DEVICE_HELLO,
                TARGET: self._machine_id,
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
            Log.info("ControllerHeartbeat: quitting exited")
