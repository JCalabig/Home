import uuid
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
    _INTERVAL = 5

    def __init__(self, machine_id):
        threading.Thread.__init__(self)
        self._read_devices = ["dht11"]
        self._devices = {}
        self._lock = threading.RLock()
        self.track_id = str(uuid.uuid4())
        self._machine_id = machine_id
        self._message_queue = MessageQueue(send_key="commands", receive_key="events",
                                           on_receive=self.on_receive,
                                           send_queue_name="ControllerHeartbeat_{}_send_queue".format(machine_id),
                                           receive_queue_name="ControllerHearbeat_{}_receive_queue".format(machine_id),
                                           tag="controllerHeartbeat")
        self._interval = IntervalExecution(self._interval_action, ControllerHeartbeat._INTERVAL, start=True,
                                           tag="controllerHeartbeatInterval")
        self.start()

    def _interval_action(self):
        with self._lock:
            for key in self._devices:
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
                if device in self._read_devices:
                    self._message_queue.send({
                        TYPE: COMMAND,
                        TARGET: target,
                        DEVICE: device,
                        OP_CODE: "read"
                    })

    def cleanup(self):
        Log.info("ControllerHeartbeat: quitting")
        try:
            self._interval.quit()
            self._message_queue.cleanup()
            Log.info("ControllerHeartbeat: sleeping 10 secs to sync cleanup")
            time.sleep(10)
        except:
            Log.info("Exception", exc_info=1)
        finally:
            Log.info("ControllerHeartbeat: quitting exited")

    def run(self):
        try:
            Log.info("ControllerHeartbeat: thread started (track:%s)", self.track_id)
            self._message_queue.block_receive()
        except:
            Log.info("Exception", exc_info=1)
        finally:
            Log.info("ControllerHeartbeat: thread exited (track:%s)", self.track_id)

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
