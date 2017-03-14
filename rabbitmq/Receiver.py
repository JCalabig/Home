import uuid
from time import sleep
from QueueBase import QueueBase
import json
from utils.DefaultLogger import Log


class Receiver(QueueBase):
    def __init__(self, host, username, password, routing_key, on_receive, exchange, queue_name="", port=5672):
        super(self.__class__, self).__init__(host, username, password, routing_key,
                                             exchange, queue_name, port)
        self._on_receive = on_receive

    def _yield_get(self, inactivity_timeout=1):
        if self.quit is True:
            yield None
            return
        for message in self.channel.consume(self.queue_name, inactivity_timeout=inactivity_timeout):
            if message is None:
                yield None
                continue
            method, properties, body = message
            if self.quit is True:
                self.channel.basic_ack(delivery_tag=method.delivery_tag)
                yield None
                return
            else:
                yield message
                self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def block_receive(self):
        Log.info("MessageQueue block_receive thread started (queue:%s)", self.queue_name)
        try:
            while self.quit is False:
                try:
                    self.connect()
                    for message in self._yield_get():
                        if message is not None and self._on_receive is not None:
                            method, properties, body = message
                            self._on_receive(json.loads(body), method.routing_key)
                except KeyboardInterrupt:
                    Log.info("MessageQueue block_receive thread got keyboard interrupt(queue:%s)", self.queue_name)
                    self.quit = True
                except:
                    Log.info("Exception", exc_info=1)
                    Log.info("sleeping 2 secs on queue connection failure")
                    sleep(2)
                self.disconnect()
        finally:
            Log.info("MessageQueue block_receive thread exited (queue:%s)", self.queue_name)

    def cleanup(self):
        try:
            super(self.__class__, self).cleanup()
            Log.info("sleeping 5 secs to sync cleanup")
            sleep(5)
        except:
            pass

if __name__ == "__main__":
    from config import queue_server, username, password

    def on_receive(self, event_payload, routing_key):
        pass


    r = Receiver(queue_server, username, password, "events", on_receive=on_receive, exchange="events",
                 queue_name="Controller_controller1_receive_queue")
    r.block_receive()