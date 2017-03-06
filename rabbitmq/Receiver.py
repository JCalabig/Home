import json
from utils.DefaultLogger import Log


class Receiver:
    def __init__(self, connection, receiver_machine_id, routing_key, on_receive,
                 queue_name=None, exchange="home.exch", tag=""):
        self._connection = connection
        self._machine_id = receiver_machine_id
        self._on_receive = on_receive
        self._exchange = exchange
        self._routing_key = routing_key
        self._tag = tag
        self._queue_name = queue_name or receiver_machine_id

    def consume_callback(self, ch, method, properties, body):
        Log.info("<<receive<<:%s", body)
        try:
            if self._on_receive is not None:
                self._on_receive(json.loads(body), method.routing_key)
        except:
            Log.info("Exception", exc_info=1)
            raise
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def block_receive(self):
        if self._connection.channel is None:
            self._connection.connect()
        self._connection.channel.exchange_declare(exchange=self._exchange,
                                                  type='direct', durable=True)
        self._connection.channel.queue_declare(queue=self._queue_name, exclusive=False)
        self._connection.channel.queue_bind(exchange=self._exchange,
                                            queue=self._queue_name,
                                            routing_key=self._routing_key)
        self._connection.channel.basic_consume(self.consume_callback,
                                               queue=self._queue_name)

        Log.info("block_receive: {} waiting for {} on {}. To exit press CTRL+C".format(self._tag, self._routing_key,
                                                                                       self._exchange))
        self._connection.channel.start_consuming()
        Log.info("block_receive: {} exited consuming for {} on {}".format(self._tag, self._routing_key,
                                                                          self._exchange))

    def cleanup(self):
        try:
            Log.info("{} calling stop consuming on {}".format(self._tag, self._routing_key,
                                                              self._exchange))
            self._connection.channel.stop_consuming()
        except:
            Log.info("Exception", exc_info=1)
        pass
