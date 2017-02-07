import pika, logging


class Connection:
    def __init__(self, host, username, password, port=5672):
        self._params = pika.ConnectionParameters(host=host,
                                                 port=port,
                                                 credentials=pika.PlainCredentials(username, password))
        self._connection = pika.BlockingConnection(self._params)
        self.channel = None

    def connect(self):
        try:
            print("connecting")
            self.channel = self._connection.channel()
            self.channel.confirm_delivery()
        except:
            logging.info("Exception", exc_info=1)

    def un_initialize(self):
        self.channel.close()
        self.channel = None
        self._connection.close()
        self._connection = None

