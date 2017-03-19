import json
import pika
from utils.DefaultLogger import Log
from QueueBase import QueueBase


class Sender(QueueBase):
    def __init__(self, host, username, password, routing_key, exchange, port=5672):
        super(self.__class__, self).__init__(host, username, password, routing_key,
                                             exchange, port)

    def send(self, payload):
        try:
            self.connect()
            properties = pika.BasicProperties(content_type="application/json",
                                              delivery_mode=2)  # 2 = persistent
            self.channel.basic_publish(self.exchange,
                                       self.routing_key,
                                       body=json.dumps(payload),
                                       properties=properties)
            Log.info(">>send>>:%s", str(payload))
        except:
            Log.error("Exception", exc_info=1)
            self.disconnect()


if __name__ == "__main__":
    queue_server = "192.168.1.22"
    username = "test"
    password = "test"
    exchange_and_routing_key = "events"
    payload = {
        "test": "for all"
    }

    credentials = pika.PlainCredentials(username, password)
    params = pika.ConnectionParameters(host=queue_server, port=5672, credentials=credentials)

    s = Sender(queue_server, username, password, routing_key=exchange_and_routing_key,
               exchange=exchange_and_routing_key)
    s.send(payload)
    s.disconnect()