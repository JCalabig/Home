from constants import *


class ControlledObject:
    def __init__(self, config, state=BEGIN, mode=HOME):
        self.state = state
        self.mode = mode
        self.transition_config = config

    @staticmethod
    def _init_config(c):
        c.setdefault(CONDITION, None)
        c.setdefault(STATE, None)
        c.setdefault(NEXT_STATE, None)
        c.setdefault(ACTIONS, [])

    def is_applicable(self, event, config):
        if config[STATE] is not None and self.state != config[STATE]:
            return False

        if config[CONDITION] is None:
            return True
        return eval(config[CONDITION], {}, {
            MODE: self.mode,
            EVENT: event
        })

    def evaluate(self, event_payload):
        actions = []
        next_state = None
        for config in self.transition_config:
            self._init_config(config)
            if self.is_applicable(event_payload[EVENT], config):
                actions.extend(config[ACTIONS])
                next_state = config[NEXT_STATE] or next_state
        return next_state, actions
