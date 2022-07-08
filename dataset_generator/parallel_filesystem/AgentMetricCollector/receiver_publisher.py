import json
import threading
import traceback

import zmq
from ZMQMessages import Messages


class SendToCloud(threading.Thread):
    def __init__(self, frontend_socket_ip_receiver, frontend_socket_port_receiver,
                 backend_socket_name, zmq_context, receiver_signaling_port):
        super().__init__()
        # self.server_host = server_host
        # self.server_port = server_port
        # self.xpub_frontend_socket_ip_sender = frontend_socket_ip_sender
        # self.xpub_frontend_socket_port_sender = frontend_socket_port_sender

        self.xpub_frontend_socket_ip_receiver = frontend_socket_ip_receiver
        self.xpub_frontend_socket_port_receiver = frontend_socket_port_receiver

        self.xsub_backend_socket_name = backend_socket_name
        self.context = zmq_context
        self.receiver_signaling_port = receiver_signaling_port

    def run(self):
        xpub_frontend_socket = None
        xsub_backend_socket = None
        try:
            signal_socket = self.context.socket(zmq.REP)
            global ready_to_publish
            # # TODO we should have a mechanism to agree on sender and receiver ip port for publishing // reading from config file..
            # #  and notify receiver agents to when to start publishing // use signaling
            # #  and agree on transfer id
            print("Binding signaling socket")
            signal_socket.bind("tcp://*:{}".format(self.receiver_signaling_port))
            message = signal_socket.recv_string()
            if message == Messages.start_publishing:

                # print(f"Monitoring agent is registered successfully. Received reply [ {message} ]")

                xpub_frontend_socket = self.context.socket(zmq.XPUB)
                xpub_frontend_socket.bind("tcp://*:{}".format(self.xpub_frontend_socket_port_receiver))

                xsub_backend_socket = self.context.socket(zmq.XSUB)
                # xsub_backend_socket.bind("tcp://*:{}".format(xsub_backend_socket_port))
                xsub_backend_socket.bind("inproc://{}".format(self.xsub_backend_socket_name))
                ready_to_publish = True

                signal_socket.send_string(Messages.received_publishing_signal)
                zmq.proxy(xpub_frontend_socket, xsub_backend_socket)
            else:
                signal_socket.send(Messages.default_message)
                print(f"Received message [ {message} ]")
        except Exception as e:
            traceback.print_exc()
            # We never get here if everything is ok…
        if xpub_frontend_socket:
            un_sub_rq = {"request_type": "unsubscribe_publisher_info",
                         "data": {
                             "receiver": {
                                 "ip": self.xpub_frontend_socket_ip_receiver,
                                 "port": self.xpub_frontend_socket_port_receiver
                             }
                         }}
            xpub_frontend_socket.send_json(json.dumps(un_sub_rq))
            xpub_frontend_socket.close()
        if xsub_backend_socket:
            xsub_backend_socket.close()
        if signal_socket:
            signal_socket.close()
        # context.term()