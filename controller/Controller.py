import datetime
import copy
from utils.DefaultLogger import Log
from constants import *
from rabbitmq.Receiver import Receiver
from rabbitmq.Sender import Sender
from config import queue_server, username, password


class Controller:
    def __init__(self, machine_id, controlled_states):
        self._machine_id = machine_id

        receiver_routing_and_exchange = "events"
        receive_queue_name = "Controller_{}_receiver_queue".format(machine_id)
        self._receiver = Receiver(queue_server, username, password, routing_key=receiver_routing_and_exchange,
                                  on_receive=self.on_receive, exchange=receiver_routing_and_exchange,
                                  queue_name=receive_queue_name)

        sender_routing_and_exchange = "commands"
        self._sender = Sender(queue_server, username, password, routing_key=sender_routing_and_exchange,
                              exchange=sender_routing_and_exchange)

        self._controlled_states = controlled_states

    def cleanup(self):
        self._receiver.cleanup()
        self._sender.cleanup()

    def send(self, payload):
        payload[TIMESTAMP] = str(datetime.datetime.now())
        payload[FROM] = self._machine_id
        self._sender.send(payload)

    def block_receive(self):
        self._receiver.block_receive()

    def on_receive(self, event_payload, routing_key):
        self.set_payload_defaults(event_payload)
        if event_payload[TARGET] != self._machine_id:
            return
        if event_payload[TYPE] == EVENT:
            self.process_event(event_payload)

    def set_payload_defaults(self, event_payload):
        event_payload.setdefault(TYPE, EVENT)
        event_payload.setdefault(EVENT, None)
        event_payload.setdefault(TARGET, self._machine_id)

    def process_event(self, event_payload):
        Log.info("controller event: [%s]", event_payload[EVENT])
        for controlled_state in self._controlled_states:
            next_state, actions = controlled_state.evaluate(event_payload)
            for action in actions:
                self.do_action(action, controlled_state, event_payload)
            if next_state is not None:
                controlled_state.state = next_state
            Log.info("after event [%s]: state: [%s], mode: [%s]",
                     event_payload[EVENT], controlled_state.state, controlled_state.mode)

    def do_action(self, action, controlled_state, event_payload):
        name = action[ACTION]
        Log.info("do action: [{}] on event [{}]".format(name, event_payload[EVENT]))
        try:
            if name == SET_MODE_AWAY:
                controlled_state.mode = AWAY
                Log.info("set mode: Away")
            elif name == SET_MODE_HOME:
                controlled_state.mode = HOME
                Log.info("set mode: Home")
            elif name == SEND:
                payload = copy.deepcopy(action)
                Log.info("sending: [%s].[%s]", action[DEVICE], action[OP_CODE])
                del payload[ACTION]
                self.send(payload)
        except:
            Log.info("Exception", exc_info=1)
