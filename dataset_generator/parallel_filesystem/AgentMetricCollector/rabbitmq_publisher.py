import json
import threading
import time, os
import traceback
import zmq
from pika.exceptions import StreamLostError
import uuid

import global_vars
import pika


class SendToRabbit(threading.Thread):
    def __init__(self, backend_socket_name, zmq_context, cluster_name, rabbit_log_queue_name, heartbeat_queue_name,
                 rabbit_host, rabbit_port=5672, rabbitmq_heartbeat_interval=60):
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
        # self.rabbit_log_queue_name = rabbit_log_queue_name
        self.heartbeat_queue_name = heartbeat_queue_name
        self.host_name = os.uname()[1]
        self.cluster_name = cluster_name
        self._rabbit_log_queue_name = "{}_at_{}".format(self.host_name, self.cluster_name)

    def check_rabbit_connection(self):
        if not self.rabbitmq_channel or self.rabbitmq_channel.is_closed:
            if self.rabbitmq_connection and self.rabbitmq_connection.is_open:
                self.rabbitmq_connection.close()
            self.rabbitmq_connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbit_host, port=self.rabbit_port,
                                          heartbeat=self.rabbitmq_HEARTBEAT_INTERVAL))
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.queue_declare(queue=self._rabbit_log_queue_name)
            self.rabbitmq_channel.queue_declare(queue=self.heartbeat_queue_name, arguments={'x-message-ttl': 500})
        # print(f"Monitoring agent is ready to publish data to rabbitmq.")

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
        else:
            self.response = None

    def advertise_rabbit_log_queue_name(self):
        self.check_rabbit_connection()
        self.result = self.rabbitmq_channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = self.result.method.queue
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.rabbitmq_channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response,
                                            auto_ack=True)
        self.rabbitmq_channel.basic_publish(exchange='', routing_key='rpc_queue',
                                            properties=pika.BasicProperties(reply_to=self.callback_queue,
                                                                            correlation_id=self.corr_id, ),
                                            body=json.dumps({"rabbit_log_queue_name_1": self._rabbit_log_queue_name}))
        self.rabbitmq_connection.process_data_events(time_limit=5)
        if self.response is not None:
            response_json = json.loads(self.response)
            if response_json["status"] == 200:
                global_vars.ready_to_publish = True
                print("ready to publish data")
        else:
            # TODO handle retry if no response is back
            print("NO RESPONSE")

    def run(self):
        self.advertise_rabbit_log_queue_name()
        while True:
            try:
                self.check_rabbit_connection()
                if self.xsub_backend_socket is None:
                    self.xsub_backend_socket = self.context.socket(zmq.SUB)
                    self.xsub_backend_socket.bind("inproc://{}".format(self.xsub_backend_socket_name))
                    self.xsub_backend_socket.subscribe("")
                    self.poller.register(self.xsub_backend_socket, zmq.POLLIN)

                socks = dict(self.poller.poll(self.rabbitmq_HEARTBEAT_INTERVAL * 500))
                if socks.get(self.xsub_backend_socket) == zmq.POLLIN:
                    msg = self.xsub_backend_socket.recv()
                    self.rabbitmq_channel.basic_publish(exchange='', routing_key=self.rabbit_log_queue_name, body=msg)
                else:
                    print(time.time(), "send HB")
                    self.rabbitmq_channel.basic_publish(exchange='', routing_key=self.heartbeat_queue_name, body=b'')
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
            self.poller.unregister(self.xsub_backend_socket)
            self.xsub_backend_socket.setsockopt(zmq.LINGER, 0)
            self.xsub_backend_socket.close()

# obj = SendToRabbit("t", zmq.Context(), "localhost", 5672, 60)
# obj.start()
