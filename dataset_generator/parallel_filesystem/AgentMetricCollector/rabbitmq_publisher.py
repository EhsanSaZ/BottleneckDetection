import threading
import time
import traceback
import zmq
from pika.exceptions import StreamLostError

import global_vars
import pika


class SendToRabbit(threading.Thread):
    def __init__(self, backend_socket_name, zmq_context, rabbit_host, rabbit_port=5672, rabbitmq_heartbeat_interval=60):
        super().__init__()
        self.rabbit_host = rabbit_host
        self.rabbit_port = rabbit_port
        self.rabbitmq_HEARTBEAT_INTERVAL = rabbitmq_heartbeat_interval
        self.xsub_backend_socket_name = backend_socket_name
        self.context = zmq_context
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self.xsub_backend_socket = None
        self.poller = zmq.Poller()

    def check_rabbit_connection(self):
        if not self.rabbitmq_channel or self.rabbitmq_channel.is_closed:
            if self.rabbitmq_connection and self.rabbitmq_connection.is_open:
                self.rabbitmq_connection.close()
            self.rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbit_host, port=self.rabbit_port, heartbeat=self.rabbitmq_HEARTBEAT_INTERVAL))
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.queue_declare(queue='transfer_monitoring_logs')
            self.rabbitmq_channel.queue_declare(queue='HEARTBEAT_QUEUE', arguments={'x-message-ttl': 500})
        # print(f"Monitoring agent is ready to publish data to rabbitmq.")

    def run(self):
        while True:
            try:
                if self.xsub_backend_socket is None:
                    self.xsub_backend_socket = self.context.socket(zmq.XSUB)
                    self.xsub_backend_socket.bind("inproc://{}".format(self.xsub_backend_socket_name))
                    self.poller.register(self.xsub_backend_socket, zmq.POLLIN)

                socks = dict(self.poller.poll(self.rabbitmq_HEARTBEAT_INTERVAL * 500))
                self.check_rabbit_connection()
                if socks.get(self.xsub_backend_socket) == zmq.POLLIN:
                    msg = self.xsub_backend_socket.recv()
                    print("send msg")
                    self.rabbitmq_channel.basic_publish(exchange='', routing_key='transfer_monitoring_logs', body=msg)
                else:
                    print(time.time(), "send HB")
                    self.rabbitmq_channel.basic_publish(exchange='', routing_key='HEARTBEAT_QUEUE', body=b'')
            except StreamLostError as e:
                self.rabbitmq_channel = None
                self.rabbitmq_connection = None
                traceback.print_exc()
            except Exception as e:
                self.rabbitmq_channel = None
                self.rabbitmq_connection = None
                if self.xsub_backend_socket:
                    self.poller.unregister(self.xsub_backend_socket)
                    self.xsub_backend_socket.setsockopt(zmq.LINGER, 0)
                    self.xsub_backend_socket.close()
                    self.xsub_backend_socket = None
                traceback.print_exc()
        # We never get here if everything is ok…
        if self.xsub_backend_socket:
            self.xsub_backend_socket.setsockopt(zmq.LINGER, 0)
            self.xsub_backend_socket.close()


# obj = SendToRabbit("t", zmq.Context(), "localhost", 5672, 60)
# obj.start()