import copy
from utils.DefaultLogger import Log
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
        self._timer = CountdownTimer(60, self.get_temp_readings, name="get_temp_readings")
        self._timer.start()

    def get_temp_readings(self):
        Log.info("get_temp_readings: requesting")
        self.send({
            TYPE: COMMAND,
            DEVICE: "dht11",
            OP_CODE: "read"
        })
        self._timer.reset()

    def send(self, payload):
        self._message_queue.send(payload)

    def block_receive(self):
        self._message_queue.block_receive()
        self._timer.quit()
        self._timer.join()

    def on_receive(self, event_payload, routing_key):
        self.set_payload_defaults(event_payload)
        if event_payload[TARGET] != self._machine_id:
            return
        if event_payload[TYPE] == EVENT:
            self.process_event(event_payload)
        else:
            Log.info("%s will be handled separately", event_payload[TYPE])

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
        except Exception:
            Log.info("Exception", exc_info=1)
