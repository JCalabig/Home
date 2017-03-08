from time import sleep
from QueueBase import QueueBase
import json
from utils.DefaultLogger import Log


class Receiver(QueueBase):
    def __init__(self, host, username, password, routing_key, on_receive, exchange, queue_name="", tag="", port=5672):
        super(self.__class__, self).__init__(host, username, password, routing_key,
                                             exchange, queue_name, tag, port)
        self._on_receive = on_receive

    def _consume_callback(self, method, body):
        Log.info("<<receive<<:%s", body)
        try:
            if self._on_receive is not None:
                self._on_receive(json.loads(body), method.routing_key)
        except:
            Log.info("Exception", exc_info=1)
            raise
        finally:
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def block_receive(self):
        Log.info("block_receive: {} waiting for {} on {}.".format(self.tag, self.routing_key, self.exchange))
        for message in self.channel.consume(self.queue_name, inactivity_timeout=1):
            if self.quit is True:
                Log.info("block_receive: {} quitting. {} on {}.".format(self.tag, self.routing_key, self.exchange))
                break
            if message is None:
                continue
            method, properties, body = message
            self._consume_callback(method, body)
        Log.info("block_receive: {} exited. {} on {}.".format(self.tag, self.routing_key, self.exchange))

    def cleanup(self):
        super(self.__class__, self).cleanup()
        Log.info("sleeping 5 secs to sync cleanup")
        sleep(5)