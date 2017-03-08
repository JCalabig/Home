import pika


class QueueBase(object):
    def __init__(self, host, username, password, routing_key, exchange, queue_name="", tag="", port=5672):
        self._params = pika.ConnectionParameters(host=host, port=port,
                                                 credentials=pika.PlainCredentials(username, password))
        self._connection = pika.BlockingConnection(self._params)
        self.channel = self._connection.channel()
        self.channel.confirm_delivery()
        self.exchange = exchange
        self.routing_key = routing_key
        self.tag = tag
        self.channel.exchange_declare(exchange=self.exchange, type='direct', durable=True)
        result = self.channel.queue_declare(queue=queue_name, exclusive=False)
        self.queue_name = result.method.queue
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name, routing_key=self.routing_key)
        self.properties = pika.BasicProperties(content_type="application/json",
                                               delivery_mode=2)  # 2 = persistent
        self.quit = False

    def cleanup(self):
        self.quit = True
        if self.channel.is_open is True:
            self.channel.close()
        if self._connection.is_open is True:
            self._connection.close()
