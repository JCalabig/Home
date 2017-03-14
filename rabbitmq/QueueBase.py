import pika


class QueueBase(object):
    def __init__(self, host, username, password, routing_key, exchange, queue_name="", tag="", port=5672):
        self._host = host
        self.queue_name = queue_name
        self.exchange = exchange
        self.routing_key = routing_key
        self._port = port
        self.tag = tag
        self.username = username
        self.password = password
        self.properties = pika.BasicProperties(content_type="application/json",
                                               delivery_mode=2)  # 2 = persistent
        self._params = None
        self._connection = None
        self.channel = None
        self.quit = False

    def is_connected(self):
        if self._connection is None:
            return False
        return self._connection.is_open

    def connect(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        self._params = pika.ConnectionParameters(host=self._host, port=self._port, credentials=credentials)
        self._connection = pika.BlockingConnection(self._params)

    def disconnect(self):
        try:
            if self._connection.is_open is True:
                self._connection.close()
        except:
            pass

    def is_open(self):
        if self.channel is None:
            return False
        return self.channel.is_open

    def open_channel(self):
        self.channel = self._connection.channel()
        self.channel.confirm_delivery()
        self.channel.exchange_declare(exchange=self.exchange, type='direct')
        self.channel.queue_declare(queue=self.queue_name, exclusive=False)
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name, routing_key=self.routing_key)

    def close_channel(self):
        try:
            if self.channel.is_open is True:
                self.channel.close()
        except:
            pass

    def cleanup(self):
        self.quit = True
        self.close_channel()
        self.disconnect()
