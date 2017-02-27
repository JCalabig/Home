import json
from utils.DefaultLogger import Log


class Receiver:
    def __init__(self, connection, receiver_machine_id, routing_key, on_receive, exchange="home.exch"):
        self._connection = connection
        self._machine_id = receiver_machine_id
        self._on_receive = on_receive
        self._exchange = exchange
        self._routing_key = routing_key

    def consume_callback(self, ch, method, properties, body):
        Log.info("<<receive<<:%s", body)
        try:
            self._on_receive(json.loads(body), method.routing_key)
        except:
            Log.error("Exception", exc_info=1)
            raise
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def block_receive(self):
        if self._connection.channel is None:
            self._connection.connect()
        self._connection.channel.exchange_declare(exchange=self._exchange,
                                                  type='direct', durable=True)
        self._connection.channel.queue_declare(queue=self._machine_id, exclusive=False)
        self._connection.channel.queue_bind(exchange=self._exchange,
                                            queue=self._machine_id,
                                            routing_key=self._routing_key)
        self._connection.channel.basic_consume(self.consume_callback,
                                               queue=self._machine_id)

        Log.info("block_receive: waiting for {}. To exit press CTRL+C".format(self._routing_key))
        self._connection.channel.start_consuming()

    def cleanup(self):
        pass
