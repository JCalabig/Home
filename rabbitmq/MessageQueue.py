from time import sleep
from utils.DefaultLogger import Log
from rabbitmq.Receiver import Receiver
from rabbitmq.Sender import Sender
from config import queue_server, username, password


class MessageQueue:
    def __init__(self, send_key, receive_key, on_send=None, on_receive=None, tag=""):
        self._tag = tag

        self._sender = None
        self._send_key = send_key
        self._on_send = on_send

        self._receiver = None
        self._receive_key = receive_key
        self._on_receive = on_receive

        self._quit = False

    def send(self, payload):
        try:
            if self._sender is None or self._sender.quit is True:
                self._sender = Sender(queue_server, username, password, routing_key=self._send_key,
                                      on_send=self._on_send, exchange=self._send_key,
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
        Log.info("MessageQueue %s block_receive thread started", self._tag)
        try:
            while self._quit is False:
                try:
                    if self._receiver is None or self._receiver.quit is True:
                        self._receiver = Receiver(queue_server, username, password, routing_key=self._send_key,
                                                  on_receive=self._on_receive, exchange=self._receive_key,
                                                  tag=self._tag + "_receiver")
                    self._receiver.block_receive()
                except KeyboardInterrupt:
                    Log.info("MessageQueue %s got KeyboardInterrupt", self._tag)
                    self.cleanup()
                    return
                except:
                    Log.debug("Exception", exc_info=1)
                    sleep(10)
                    if self._receiver is not None:
                        self._receiver.cleanup()
        finally:
            Log.info("MessageQueue %s block_receive thread exited", self._tag)
