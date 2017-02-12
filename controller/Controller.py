import copy
import logging
from utils.Countdown import CountdownTimer
from constants import *
from rabbitmq.MessageQueue import MessageQueue


# controller to have a periodic thread to ask for DHT11 data!

class Controller:
    def __init__(self, machine_id, controlled_states):
        self._machine_id = machine_id
        self._message_queue = MessageQueue(self._machine_id, send_key="commands",
                                           receive_key="events", on_receive=self.on_receive)
        self._controlled_states = controlled_states
        self._timer = CountdownTimer(2, self.get_temp_readings, name="dht controller")
        self._timer.start()

    def get_temp_readings(self):
        #self.send({
        #    TYPE: COMMAND,
        #    DEVICE: "dht11",
        #    OP_CODE: "read"
        #})
        pass

    def send(self, payload):
        self._message_queue.send(payload)

    def block_receive(self):
        self._message_queue.block_receive()
        self._timer.quit()
        self._timer.join()

    def on_receive(self, event_payload, routing_key):
        if routing_key != "events":
            logging.info("ignoring %s", routing_key)
            return
        self.set_payload_defaults(event_payload)
        if event_payload[TARGET] != self._machine_id:
            return
        if event_payload[TYPE] == EVENT:
            self.process_event(event_payload)
        else:
            logging.info("%s will be handled separately", event_payload[TYPE])

    def set_payload_defaults(self, event_payload):
        event_payload.setdefault(TYPE, EVENT)
        event_payload.setdefault(EVENT, None)
        event_payload.setdefault(TARGET, self._machine_id)

    def process_event(self, event_payload):
        logging.info("... on event %s", str(event_payload))
        for controlled_state in self._controlled_states:
            next_state, actions = controlled_state.evaluate(event_payload)
            for action in actions:
                self.do_action(action, controlled_state, event_payload)
            if next_state is not None:
                controlled_state.state = next_state
            logging.info("state after actions: %s, mode: %s after event %s",
                         controlled_state.state, controlled_state.mode, str(event_payload))

    def do_action(self, action, controlled_state, event_payload):
        name = action[ACTION]
        logging.info("performing action: {} on event {}".format(name, str(event_payload)))
        try:
            if name == SET_MODE_AWAY:
                controlled_state.mode = AWAY
                logging.info("set mode: away")
            elif name == SET_MODE_HOME:
                controlled_state.mode = HOME
                logging.info("set mode: Home")
            elif name == SEND:
                payload = copy.deepcopy(action)
                del payload[ACTION]
                self.send(payload)
        except Exception:
            logging.info("Exception", exc_info=1)
