import json, pika
from utils.DefaultLogger import Log
from constants import *


class Sender:
    def __init__(self, connection, sender_machine_id, routing_key, on_send=None, exchange="home.exch"):
        self._connection = connection
        self._machine_id = sender_machine_id
        self._exchange = exchange
        self._routing_key = routing_key
        self._on_send = on_send
        self._properties = pika.BasicProperties(content_type="application/json",
                                                delivery_mode=2)  # 2 = persistent

    def send(self, payload):
        payload[FROM] = self._machine_id
        if self._connection.channel is None:
            self._connection.connect()
        try:
            if self._on_send is not None:
                self._on_send(payload)
        except Exception:
            Log.error("Exception", exc_info=1)
        self._connection.channel.exchange_declare(exchange=self._exchange,
                                                  type='direct', durable=True)
        self._connection.channel.basic_publish(self._exchange,
                                               self._routing_key,
                                               json.dumps(payload),
                                               self._properties)
        Log.info(">>>>>>>>>>>>>>>>>>>>>>>>>sending: (key:%s)%s", self._routing_key, str(payload))

    def un_initialize(self):
        pass
