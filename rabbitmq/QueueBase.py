import pika


class QueueBase(object):
    def __init__(self, host, username, password, routing_key, exchange, port=5672):
        self._host = host
        self.exchange = exchange
        self.routing_key = routing_key
        self._port = port
        self.username = username
        self.password = password
        self.properties = pika.BasicProperties(content_type="application/json",
                                               delivery_mode=2)  # 2 = persistent
        self._params = None
        self._connection = None
        self.channel = None
        self.quit = False

    def is_connected(self):
        if self._connection is None or self.channel is None:
            return False
        return self._connection.is_open and self.channel.is_open

    def connect(self):
        if self.is_connected() is True:
            return
        self.disconnect()
        credentials = pika.PlainCredentials(self.username, self.password)
        self._params = pika.ConnectionParameters(host=self._host, port=self._port, credentials=credentials)
        self._connection = pika.BlockingConnection(self._params)
        self.channel = self._connection.channel()
        self.channel.confirm_delivery()
        self.channel.exchange_declare(exchange=self.exchange, type='direct')

    def disconnect(self):
        try:
            if self.channel.is_open is True:
                self.channel.close()
        except:
            pass
        try:
            if self._connection.is_open is True:
                self._connection.close()
        except:
            pass

    def cleanup(self):
        self.quit = True
        self.disconnect()
