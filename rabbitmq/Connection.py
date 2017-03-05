import pika
from utils.DefaultLogger import Log


class Connection:
    def __init__(self, host, username, password, port=5672):
        self._params = pika.ConnectionParameters(host=host,
                                                 port=port,
                                                 credentials=pika.PlainCredentials(username, password))
        self._connection = pika.BlockingConnection(self._params)
        self.channel = None

    def connect(self):
        try:
            self.channel = self._connection.channel()
            self.channel.confirm_delivery()
        except:
            Log.info("Exception", exc_info=1)

    @staticmethod
    def _ignore_exceptions(obj):
        try:
            if obj is not None:
                obj.close()
        except:
            Log.debug("Exception", exc_info=1)


    def cleanup(self):
        Connection._ignore_exceptions(self.channel)
        Connection._ignore_exceptions(self._connection)
        self.channel = None
        self._connection = None
