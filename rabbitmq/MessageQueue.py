from utils.DefaultLogger import Log
from rabbitmq.Connection import Connection
from rabbitmq.Receiver import Receiver
from rabbitmq.Sender import Sender
from config import queue_server, username, password


class MessageQueue:
    def __init__(self, machine_id, send_key, receive_key, on_send=None, on_receive=None, queue_name=None):
        self._connection = Connection(queue_server, username, password)
        self.sender = Sender(self._connection, machine_id, send_key, exchange=send_key, on_send=on_send)
        self.receiver = Receiver(self._connection, machine_id, receive_key,
                                 exchange=receive_key, on_receive=on_receive, queue_name=queue_name)

    def send(self, payload):
        self.sender.send(payload)

    def cleanup(self):
        if self._connection is not None:
            self.sender.cleanup()
            self.receiver.cleanup()
            self._connection.cleanup()
        self.sender = None
        self.receiver = None
        self._connection = None

    def block_receive(self):
        try:
            self.receiver.block_receive()
        except KeyboardInterrupt:
            Log.info("MessageQueue got KeyboardInterrupt")
        self.cleanup()
