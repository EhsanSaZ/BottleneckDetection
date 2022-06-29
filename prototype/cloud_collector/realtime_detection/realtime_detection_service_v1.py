import zmq
from pymongo import MongoClient
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
from db_change_stream_processing import db_change_stream_process

import traceback

from Config import Config

host = Config.detection_server_host_ip
port = Config.detection_server_port
ipc_path_name = "/tmp/detection_workers_messaging"
total_worker_processes = Config.process_worker_number


def worker_routine(worker_url: str, context: zmq.Context = None):
    context = context or zmq.Context.instance()
    db_host = Config.db_address
    db_port = Config.db_port
    db_name = Config.db_name
    db_user = Config.db_user
    db_pass = Config.db_pass
    db_client = MongoClient('mongodb://{}:{}/{}'.format(db_host, db_port, db_name),
                            username=db_user,
                            password=db_pass,)

    # Socket to talk to dispatcher
    rep_socket = context.socket(zmq.REP)
    rep_socket.connect(worker_url)
    worker = Config.streaming_thread_per_worker_process

    with ThreadPoolExecutor(max_workers=worker) as executor:
        while True:
            try:
                req_json = rep_socket.recv_json()
                if req_json["request_type"] == "new_transfer":
                    data = req_json["data"]
                    transfer_id = data["transfer_id"]
                    # T ODO submit the new stream function and let it run...
                    executor.submit(db_change_stream_process, db_client, db_name, transfer_id)
                    rep_socket.send_json({"response_code": "200", "request": req_json})
            except Exception as e:
                traceback.print_exc()


def main():
    url_client = "tcp://{}:{}".format(host, port)
    url_worker = "ipc:///tmp/detection_workers_messaging"

    # Prepare our context and sockets
    context = zmq.Context()
    # Socket to talk to clients
    clients = context.socket(zmq.ROUTER)
    clients.bind(url_client)

    # Socket to talk to workers
    workers = context.socket(zmq.DEALER)
    workers.bind(url_worker)

    for i in range(total_worker_processes):
        p = Process(target=worker_routine, args=(url_worker, None))
        print(p)
        p.start()

    zmq.proxy(clients, workers)

    # We never get here but clean up anyhow
    clients.close()
    workers.close()
    context.term()


if __name__ == "__main__":
    main()
