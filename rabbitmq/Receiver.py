from time import sleep
from QueueBase import QueueBase
import json
from utils.DefaultLogger import Log


class Receiver(QueueBase):
    def __init__(self, host, username, password, routing_key, on_receive, exchange, queue_name="", port=5672):
        super(self.__class__, self).__init__(host, username, password, routing_key,
                                             exchange, port)
        self.queue_name = queue_name
        self._on_receive = on_receive

    def connect(self):
        super(self.__class__, self).connect()
        self.channel.queue_declare(queue=self.queue_name, exclusive=False)
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name, routing_key=self.routing_key)

    def _yield_get(self, inactivity_timeout=1):
        if self.quit is True:
            return
        for message in self.channel.consume(self.queue_name, inactivity_timeout=inactivity_timeout):
            if self.quit is True:
                return
            if message is None:
                continue
            yield message
            method, properties, body = message
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def block_receive(self):
        Log.info("MessageQueue block_receive thread started (queue:%s)", self.queue_name)
        while self.quit is False:
            try:
                self.connect()
                for method, properties, body in self._yield_get():
                    if self._on_receive is not None:
                        self._on_receive(json.loads(body), method.routing_key)
            except KeyboardInterrupt:
                Log.info("MessageQueue block_receive thread got keyboard interrupt(queue:%s)", self.queue_name)
                self.quit = True
            except:
                Log.info("Exception", exc_info=1)
            Log.info("sleeping 2 secs on queue connection failure")
            sleep(2)
            self.disconnect()
        Log.info("MessageQueue block_receive thread exited (queue:%s)", self.queue_name)

    def cleanup(self):
        try:
            super(self.__class__, self).cleanup()
            Log.info("sleeping 5 secs to sync cleanup")
            sleep(5)
        except:
            pass

if __name__ == "__main__":
    queue_server = "192.168.1.22"
    username = "test"
    password = "test"
    exchange_and_routing_key = "events"

    def on_receive(event_payload, routing_key):
        print (str(event_payload))

    r = Receiver(queue_server, username, password, routing_key=exchange_and_routing_key, exchange="events",
                 on_receive=on_receive, queue_name="Controller_controller1_receive_queue")
    r.block_receive()