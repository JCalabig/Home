import uuid
from time import sleep
from utils.DefaultLogger import Log
from rabbitmq.Receiver import Receiver
from rabbitmq.Sender import Sender
from config import queue_server, username, password


class MessageQueue:
    def __init__(self, send_key, receive_key, on_send=None, on_receive=None, send_queue_name="",
                 receive_queue_name="", tag=""):
        self.track_id = str(uuid.uuid4())
        self._tag = tag

        self._sender = None
        self._send_key = send_key
        self._on_send = on_send
        self._send_queue_name = send_queue_name

        self._receiver = None
        self._receive_key = receive_key
        self._on_receive = on_receive
        self._receive_queue_name = receive_queue_name

        self._quit = False

    def send(self, payload):
        try:
            if self._sender is None or self._sender.quit is True:
                self._sender = Sender(queue_server, username, password, routing_key=self._send_key,
                                      exchange=self._send_key, queue_name=self._send_queue_name,
                                      tag=self._tag + "_sender")
            self._sender.send(payload)
        except:
            Log.info("Exception", exc_info=1)
            if self._sender is not None:
                self._sender.cleanup()

    def cleanup(self):
        self._quit = True
        if self._sender is not None:
            self._sender.cleanup()
        if self._receiver is not None:
            self._receiver.cleanup()

    def block_receive(self):
        self._receiver = Receiver(queue_server, username, password, routing_key=self._send_key,
                                  on_receive=self._on_receive, exchange=self._receive_key,
                                  queue_name=self._receive_queue_name, tag=self._tag + "_receiver")
        self._receiver.block_receive()
