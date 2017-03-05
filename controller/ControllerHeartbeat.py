from utils.DefaultLogger import Log
from constants import *
import threading, time
from rabbitmq.MessageQueue import MessageQueue
from utils.Execution import IntervalExecution


# controller to query for known devices at the beginning
# this list of devices will be used for periodic hearbeat
# devices to send a heartbeat periodically so both sides are autonomous


class ControllerHeartbeat(threading.Thread):
    _INACTIVE_DEVICE_TIMEOUT = 60

    def __init__(self, machine_id, tag=""):
        threading.Thread.__init__(self)
        self.tag = tag
        self._devices = {}
        self._lock = threading.RLock()
        self._machine_id = machine_id
        queue_name = "{}_controller_heartbeat_queue".format(self._machine_id)
        self._message_queue = MessageQueue(self._machine_id, send_key="commands",
                                           receive_key="events", on_receive=self.on_receive,
                                           queue_name=queue_name)
        self._interval = IntervalExecution(self._interval_action, 60, start=True, tag="controllerHeartbeat")
        self.start()

    def _interval_action(self):
        with self._lock:
            for key in self._devices:
                # find active devices
                last_hello = self._devices[key][LAST_HELLO]
                device = self._devices[key][DEVICE]
                target = self._devices[key][TARGET]

                if time.time() - last_hello > ControllerHeartbeat._INACTIVE_DEVICE_TIMEOUT:
                    Log.info("inactive device: last hello from %s was %s", key, last_hello)
                    continue

                self._message_queue.send({
                    TYPE: COMMAND,
                    TARGET: target,
                    DEVICE: device,
                    OP_CODE: "resumeEvents"
                })
                if device == "dht11":
                    self._message_queue.send({
                        TYPE: COMMAND,
                        TARGET: target,
                        DEVICE: device,
                        OP_CODE: "read"
                    })

    def run(self):
        Log.info("%s: started", self.tag)
        self._message_queue.block_receive()
        self._interval.quit()

    def on_receive(self, event_payload, routing_key):
        self.set_payload_defaults(event_payload)
        if event_payload[TARGET] != self._machine_id:
            return
        if event_payload[TYPE] == DEVICE_HELLO:
            self.process_device_hello(event_payload)
        elif event_payload[EVENT] == DATA:
            Log.info("data %s will be handled separately", event_payload[TYPE])

    def set_payload_defaults(self, event_payload):
        event_payload.setdefault(TYPE, EVENT)
        event_payload.setdefault(EVENT, None)
        event_payload.setdefault(TARGET, self._machine_id)

    def process_device_hello(self, event_payload):
        with self._lock:
            from_machine_id = event_payload[FROM]
            device = event_payload[DEVICE]
            key = "{}|{}".format(from_machine_id, device)
            if key not in self._devices:
                self._devices[key] = {
                    TARGET: from_machine_id,
                    DEVICE: device
                }
            self._devices[key][LAST_HELLO] = time.time()