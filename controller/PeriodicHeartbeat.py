from utils.DefaultLogger import Log
from utils.Countdown import CountdownTimer
from constants import *
import threading
from rabbitmq.MessageQueue import MessageQueue

# controller to query for known devices at the beginning
# this list of devices will be used for periodic hearbeat
# devices to send a heartbeat periodically so both sides are autonomous


class PeriodicHeartbeat(threading.Thread):
    def __init__(self, machine_id):
        threading.Thread.__init__(self)
        self._machine_id = machine_id
        self._queue_name = "{}_controller_heartbeat_queue".format(machine_id)
        self._message_queue = MessageQueue(self._machine_id, send_key="commands",
                                           receive_key="events", on_receive=self.on_receive,
                                           queue_name=self._queue_name)
        self._timer = CountdownTimer(60, self._on_periodic_timer, name="_on_periodic_timer")
        Log.info("PeriodicHeartbeat: starting")
        self._timer.start()

    def _on_periodic_timer(self):
        Log.info("_on_periodic_timer: run!")
        self._message_queue.send({
            TYPE: COMMAND,
            DEVICE: "dht11",
            OP_CODE: "read"
        })
        for device in ("dht11", "kitchenLights1"):
            self._message_queue.send({
                TYPE: COMMAND,
                DEVICE: device,
                OP_CODE: "resumeEvents"
            })
        self._timer.reset()

    def on_receive(self, event_payload, routing_key):
        self.set_payload_defaults(event_payload)
        if event_payload[TARGET] != self._machine_id:
            return
        if event_payload[TYPE] == "hello":
            self.process_event(event_payload)
        elif event_payload[EVENT] == DATA:
            Log.info("%s will be handled separately", event_payload[TYPE])

    def set_payload_defaults(self, event_payload):
        event_payload.setdefault(TYPE, EVENT)
        event_payload.setdefault(EVENT, None)
        event_payload.setdefault(TARGET, self._machine_id)

    def process_event(self, event_payload):
        Log.info("controller event: [%s]", event_payload[EVENT])

    def run(self):
        self._message_queue.block_receive()
        self._timer.quit()
        self._timer.join()

