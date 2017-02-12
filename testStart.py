from config import queue_server, username, password
from constants import *
from rabbitmq.Connection import Connection
from rabbitmq.Sender import Sender

connection = Connection(queue_server, username, password)

sender = Sender(connection, "controller1", "events", exchange="events")
sender.send({
    TO: "controller1",
    EVENT:"reset"
    })
sender.un_initialize()
connection.un_initialize()
