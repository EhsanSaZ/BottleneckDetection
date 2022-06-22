import json
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from event_process import process_event
from event_process_v2 import process_event_v2
from event_process_v3 import process_event_v3
import zmq, time, sys, os
from multiprocessing import Process
from pymongo import MongoClient
from Config import Config

# import numpy as np
# from concurrent.futures.thread import ThreadPoolExecutor
# import random


host = "*"
port = "60000"
ipc_path_name = "/tmp/zmqtest"
total_worker_processes = Config.process_worker_number


def worker_routine(worker_url: str, context: zmq.Context = None):
    """Worker routine"""
    context = context or zmq.Context.instance()
    db_host = Config.db_address
    db_port = Config.db_port
    db_name = Config.db_name
    db_user = Config.db_user
    db_pass = Config.db_pass
    worker = Config.thread_per_worker_process

    db_client = MongoClient('mongodb://{}:{}/{}'.format(db_host, db_port, db_name),
                            username=db_user,
                            password=db_pass,)

    # Socket to talk to dispatcher
    rep_socket = context.socket(zmq.REP)
    rep_socket.connect(worker_url)

    sub_socket = context.socket(zmq.SUB)
    # sub_socket.connect(worker_url)
    sub_socket.subscribe("")

    poller = zmq.Poller()
    poller.register(rep_socket, zmq.POLLIN)
    poller.register(sub_socket, zmq.POLLIN)

    # time.sleep(1)
    with ThreadPoolExecutor(max_workers=worker) as executor:
        while True:
            # string = rep_socket.recv()
            # print(f"{os.getpid()}: Received request: [ {string} ]")
            # # Do some 'work'
            # # subscribe to new publisher
            # time.sleep(0.1)
            #
            # # Send reply back to client
            # rep_socket.send(b"World")
            socks = dict(poller.poll())
            if socks.get(rep_socket) == zmq.POLLIN:
                req_json = rep_socket.recv_json()
                print(f"{os.getpid()}: Received request: [ {req_json} ]")
                # new_publisher_request_format = {"request_type": "new_publisher_info", "data": {"sender": {"ip": "1.1.1.1", "port": "1111"}, "receiver": {"ip": "2.2.2.2", "port": "22222"}}}
                # Do some 'work' # time.sleep(0.1)
                # Send reply back to client
                try:
                    if req_json["request_type"] == "new_publisher_info":
                        data = req_json["data"]
                        # subscribe to new sender and receiver publisher
                        sender_ip = data["sender"]["ip"]
                        sender_port = data["sender"]["port"]
                        receiver_ip = data["receiver"]["ip"]
                        receiver_port = data["receiver"]["port"]
                        # print("subscribing sender {} {}, receiver{} {}".format(sender_ip, sender_port, receiver_ip, receiver_port))
                        sub_socket.connect("tcp://{}:{}".format(sender_ip, sender_port))
                        sub_socket.connect("tcp://{}:{}".format(receiver_ip, receiver_port))
                        success_response = {"response_code": "200", "data": "subscribed", "request": req_json}
                        rep_socket.send_json(success_response)
                    elif req_json["request_type"] == "unsubscribe_publisher_info":
                        data = req_json["data"]
                        sender_ip = data["sender"]["ip"]
                        sender_port = data["sender"]["port"]
                        receiver_ip = data["receiver"]["ip"]
                        receiver_port = data["receiver"]["port"]
                        sub_socket.disconnect("tcp://{}:{}".format(sender_ip, sender_port))
                        sub_socket.disconnect("tcp://{}:{}".format(receiver_ip, receiver_port))
                        success_response = {"response_code": "200", "data": "unsubscribed", "request": req_json}
                        rep_socket.send_json(success_response)
                except KeyError as ke:
                    # error_format = {"response_code": "400", "data":str(repr(ke))}
                    error_response = {"response_code": "400", "data": str(repr(ke))}
                    rep_socket.send_json(error_response)
                except Exception as e:
                    # error_format = {"response_code": "400", "data":str(repr(ke))}
                    error_response = {"response_code": "400", "data": str(repr(e))}
                    rep_socket.send_json(error_response)
            if socks.get(sub_socket) == zmq.POLLIN:
                # print("sub_socket")
                data = sub_socket.recv_json()
                # process the event
                executor.submit(process_event_v2, json.loads(data), db_client, db_name)


def main():
    # url_worker = "inproc://workers"
    # Path(ipc_path_name).mkdir(parents=True, exist_ok=True)
    url_worker = "ipc:///tmp/zmqtest"
    url_client = "tcp://{}:{}".format(host, port)

    # Prepare our context and sockets
    context = zmq.Context()
    # Socket to talk to clients
    clients = context.socket(zmq.ROUTER)
    clients.bind(url_client)

    # Socket to talk to workers
    workers = context.socket(zmq.DEALER)
    workers.bind(url_worker)
    #
    for i in range(total_worker_processes):
        p = Process(target=worker_routine, args=(url_worker, None))
        print(p)
        p.start()
    # p = Process(target=worker_routine, args=(url_worker, None))
    zmq.proxy(clients, workers)
    # p.join()
    # We never get here but clean up anyhow
    clients.close()
    workers.close()
    context.term()


if __name__ == "__main__":
    main()
