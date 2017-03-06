from time import sleep
from utils.DefaultLogger import Log
from rabbitmq.Connection import Connection
from rabbitmq.Receiver import Receiver
from rabbitmq.Sender import Sender
from config import queue_server, username, password


class MessageQueue:
    def __init__(self, machine_id, send_key, receive_key, on_send=None, on_receive=None, queue_name=None, tag=""):
        self._tag = tag
        self._machine_id = machine_id
        self._send_key = send_key
        self._receive_key = receive_key
        self._on_send = on_send
        self._on_receive = on_receive
        self._queue_name = queue_name
        self._sender = None
        self._sender_connection = None
        self._receiver = None
        self._receiver_connection = None
        self._quit = False

    def send(self, payload):
        try:
            if self._sender_connection is None:
                self._sender_connection = Connection(queue_server, username, password)
            if self._sender is None:
                self._sender = Sender(self._sender_connection, self._machine_id, self._send_key,
                                      exchange=self._send_key, on_send=self._on_send)
            self._sender.send(payload)
        except:
            Log.info("Exception", exc_info=1)
            MessageQueue._ignore_exceptions(self._sender)
            MessageQueue._ignore_exceptions(self._sender_connection)
            self._sender = None
            self._sender_connection = None

    @staticmethod
    def _ignore_exceptions(obj):
        try:
            if obj is not None:
                obj.cleanup()
        except:
            Log.debug("Exception", exc_info=1)

    def cleanup(self):
        self._quit = True
        MessageQueue._ignore_exceptions(self._receiver)
        MessageQueue._ignore_exceptions(self._receiver_connection)
        MessageQueue._ignore_exceptions(self._sender)
        MessageQueue._ignore_exceptions(self._sender_connection)
        self._receiver = None
        self._receiver_connection = None
        self._sender = None
        self._sender_connection = None

    def block_receive(self):
        Log.info("MessageQueue %s block_receive thread started", self._tag)
        try:
            while True:
                try:
                    if self._receiver_connection is None:
                        self._receiver_connection = Connection(queue_server, username, password)
                    if self._receiver is None:
                        self._receiver = Receiver(self._receiver_connection, self._machine_id, self._receive_key,
                                                  exchange=self._receive_key, on_receive=self._on_receive,
                                                  queue_name=self._queue_name, tag=self._tag)
                    self._receiver.block_receive()
                except KeyboardInterrupt:
                    Log.info("MessageQueue %s got KeyboardInterrupt", self._tag)
                    self.cleanup()
                    return
                except:
                    Log.debug("Exception", exc_info=1)
                    sleep(10)
                    MessageQueue._ignore_exceptions(self._receiver)
                    MessageQueue._ignore_exceptions(self._receiver_connection)
                    self._receiver = None
                    self._receiver_connection = None
                    if self._quit is True:
                        return
        finally:
            Log.info("MessageQueue %s block_receive thread exited", self._tag)
