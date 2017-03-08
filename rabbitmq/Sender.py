import json
from utils.DefaultLogger import Log
from QueueBase import QueueBase


class Sender(QueueBase):
    def __init__(self, host, username, password, routing_key, on_send, exchange, queue_name="", tag="", port=5672):
        super(self.__class__, self).__init__(host, username, password, routing_key,
                                             exchange, queue_name, tag, port)
        self._on_send = on_send

    def send(self, payload):
        try:
            if self._on_send is not None:
                self._on_send(payload)
            self.channel.basic_publish(self.exchange,
                                       self.routing_key,
                                       json.dumps(payload),
                                       self.properties)
            Log.info(">>send>>:%s", str(payload))
        except:
            Log.error("Exception", exc_info=1)
