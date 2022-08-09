import json
import threading
import traceback
import zmq
import global_vars
from collectors.protobuf_messages.log_metrics_pb2 import PublisherPayload
# from AgentMetricCollector.ZMQMessages import Messages


class SendToCloud(threading.Thread):
    def __init__(self, server_host, server_port,
                 xpub_frontend_public_socket_ip, xpub_frontend_public_socket_port,
                 backend_socket_name, zmq_context):
        super().__init__()
        self.server_host = server_host
        self.server_port = server_port
        self.xpub_frontend_public_socket_ip = xpub_frontend_public_socket_ip
        self.xpub_frontend_public_socket_port = xpub_frontend_public_socket_port

        self.xsub_backend_socket_name = backend_socket_name
        self.context = zmq_context
        
    def run(self):
        xpub_frontend_socket = None
        xsub_backend_socket = None
        try:
            # global ready_to_publish
            rq_socket = self.context.socket(zmq.REQ)
            rq_socket.connect("tcp://{}:{}".format(self.server_host, self.server_port))
            #  we should have a mechanism to agree on sender and receiver ip port for publishing // reading from config file..
            #  and notify receiver agents to when to start publishing
            #  T ODO and agree on transfer id
            rq = {"request_type": "new_publisher_info",
                  "data": {
                      "publisher": {
                          "ip": self.xpub_frontend_public_socket_ip,
                          "port": self.xpub_frontend_public_socket_port
                      }
                      # "receiver": {
                      #     "ip": self.xpub_frontend_socket_ip_receiver,
                      #     "port": self.xpub_frontend_socket_port_receiver
                      # }
                  }}
            rq_socket.send_json(rq)
            message = rq_socket.recv_json()
            # message = {"response_code": "200"}
            if message["response_code"] == "200":
                print(f"Monitoring agent is registered successfully. Received reply [ {message} ]")
                xpub_frontend_socket = self.context.socket(zmq.XPUB)
                xpub_frontend_socket.bind("tcp://*:{}".format(self.xpub_frontend_public_socket_port))

                xsub_backend_socket = self.context.socket(zmq.XSUB)
                # xsub_backend_socket.bind("tcp://*:{}".format(xsub_backend_socket_port))
                xsub_backend_socket.bind("inproc://{}".format(self.xsub_backend_socket_name))
                global_vars.ready_to_publish = True

                zmq.proxy(xpub_frontend_socket, xsub_backend_socket)
            else:
                print(f"Error in registering monitoring agent publisher socket. Received reply [ {message} ]")
            # context.term()
        except Exception as e:
            traceback.print_exc()
        # We never get here if everything is ok…
        if xpub_frontend_socket:
            unsubscribe_request = PublisherPayload()
            unsubscribe_request.request_type = "unsubscribe_publisher_info"
            unsubscribe_request.ip = self.xpub_frontend_public_socket_ip
            unsubscribe_request.port = self.xpub_frontend_public_socket_port
            xpub_frontend_socket.send(unsubscribe_request.SerializeToString())
            # un_sub_rq = {"request_type": "unsubscribe_publisher_info",
            #              "data": {
            #                  "publisher": {
            #                      "ip": self.xpub_frontend_public_socket_ip,
            #                      "port": self.xpub_frontend_public_socket_port
            #                  }
            #              }}
            # xpub_frontend_socket.send_json(json.dumps(un_sub_rq))
            xpub_frontend_socket.close()
        if xsub_backend_socket:
            xsub_backend_socket.close()
