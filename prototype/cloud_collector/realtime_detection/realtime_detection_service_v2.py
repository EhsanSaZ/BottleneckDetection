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


def worker_routine(transfer_id):
    try:
        db_host = Config.db_address
        db_port = Config.db_port
        db_name = Config.db_name
        db_user = Config.db_user
        db_pass = Config.db_pass
        db_client = MongoClient('mongodb://{}:{}/{}'.format(db_host, db_port, db_name),
                                username=db_user,
                                password=db_pass, )
        print("START STREAMING for ", transfer_id)
        db_change_stream_process(db_client, db_name, transfer_id)
    # Socket to talk to dispatcher
    # while True:
    #         # T ODO submit the new stream function and let it run...
    #         executor.submit(db_change_stream_process, db_client, db_name, transfer_id)
    except Exception as e:
        traceback.print_exc()


def main():
    url_client = "tcp://{}:{}".format(host, port)
    # url_worker = "ipc:///tmp/detection_workers_messaging"

    # Prepare our context and sockets
    context = zmq.Context()
    # Socket to talk to clients
    clients = context.socket(zmq.REP)
    clients.bind(url_client)
    tid_to_process_dict = {}

    while True:
        req_json = clients.recv_json()
        try:
            if req_json["request_type"] == "new_transfer":
                data = req_json["data"]
                transfer_id = data["transfer_id"]
                p = Process(target=worker_routine, args=(transfer_id,))
                tid_to_process_dict[transfer_id] = p
                p.start()
                clients.send_json({"response_code": "200", "request": req_json})
            elif req_json["request_type"] == "del_transfer":
                data = req_json["data"]
                transfer_id = data["transfer_id"]
                if tid_to_process_dict.get(transfer_id):
                    process = tid_to_process_dict.get(transfer_id)
                    process.terminate()
                    clients.send_json({"response_code": "200", "request": req_json})
                else:
                    clients.send_json({"response_code": "404 transfer id not found", "request": req_json})
        except Exception as e:
            clients.send_json({"response_code": "500 error processing request", "request": req_json})
            traceback.print_exc()

    # We never get here but clean up anyhow
    clients.close()
    # workers.close()
    context.term()


if __name__ == "__main__":
    main()
