from utils.DefaultLogger import Log
from utils.Countdown import CountdownTimer
from constants import *
from rabbitmq.Connection import Connection
from rabbitmq.Sender import Sender
from config import queue_server, username, password

# controller to query for known devices at the beginning
# this list of devices will be used for periodic hearbeat
# devices to send a heartbeat periodically so both sides are autonomous


class PeriodicHeartbeat:
    def __init__(self, machine_id):
        self._machine_id = machine_id
        send_key = "commands"
        self._connection = Connection(queue_server, username, password)
        self.sender = Sender(self._connection, machine_id, send_key, exchange=send_key)
        self._timer = CountdownTimer(60, self._on_periodic_timer, name="_on_periodic_timer")
        Log.info("PeriodicHeartbeat: starting")
        self._timer.start()

    def _on_periodic_timer(self):
        Log.info("_on_periodic_timer: run!")
        self.sender.send({
            TYPE: COMMAND,
            DEVICE: "dht11",
            OP_CODE: "read"
        })
        for device in ("dht11", "kitchenLights1"):
            self.sender.send({
                TYPE: COMMAND,
                DEVICE: device,
                OP_CODE: "resumeEvents"
            })
        self._timer.reset()

    def cleanup(self):
        self._timer.quit()
        self._timer.join()

