import threading
import time

import zmq
import json
import pprint
from pathlib import Path
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from BetterJSONStorage import BetterJSONStorage
from concurrent.futures.thread import ThreadPoolExecutor
from cloud_client_cnfg import Config
host = "127.0.0.1"
port = "5001"
path = Path("db.json")
# db = TinyDB(path, access_mode="r+", storage=BetterJSONStorage)
db = TinyDB(storage=MemoryStorage)
tm = db.table('transfer_metrics')
logs = Query()

# Creates a socket instance
# context = zmq.Context()
# socket = context.socket(zmq.SUB)


class SocketManager:
    def __init__(self, update_cycle):
        context = zmq.Context()
        # socket = context.socket(zmq.SUB)
        self.socket = context.socket(zmq.SUB)
        self.update_cycle = update_cycle
        # update_subscription_thread = threading.Thread(target=self.update_subscription())
        # update_subscription_thread.start()
        # update_subscription_thread.join()
        self.last_update_time = time.time()
        # self.check_publishers_file()

    # Connects to a bound socket
    def add_new_publisher(self, host, port):
        self.socket.connect("tcp://{}:{}".format(host, port))

    def remove_publisher(self, host, port):
        self.socket.disconnect("tcp://{}:{}".format(host, port))

    def subscribe_topic(self):
        # Subscribes to all topics
        self.socket.subscribe("")

    def check_publishers_file(self):
        for touple in Config.subs_hosts:
            try:
                self.add_new_publisher(touple[0], touple[1])
            except:
                print("error connecting to ", touple)

        for touple in Config.un_subs_hosts:
            try:
                self.remove_publisher(touple[0], touple[1])
            except:
                print("error disconnecting to ", touple)
        # with open(self.publishers_file_path, 'r') as pub_list:
        #     lines = pub_list.readlines()
        #     for line in lines:
        #         l = line.strip()
        #         host, port = l.split(":")
        #         self.add_new_publisher(host, port)
        print("UPDATING PUBLISHERS")
        self.last_update_time = time.time()

    # def update_subscription(self):
    #     while True:
    #         self.check_publishers_files()
    #         time.sleep(self.update_cycle)


def process_event(data):
    # print(f'worker: {indx}')
    # while True:
        # # Receives a string format message
        # data = socket.recv_json()
        # print(data, indx)
    tm.insert(data)

    logs_rcvd = tm.search((logs.sequence_number == data["sequence_number"]) & (logs.transfer_ID == data["transfer_ID"]))

    if len(logs_rcvd) > 2:
        tm.truncate()
        # continue

    if len(logs_rcvd) == 2:
        sources = set()

        for log in logs_rcvd:
            sources.add(log["is_sender"])

        if len(sources) == 2:
            d1 = logs_rcvd[0]["data"]
            d2 = logs_rcvd[1]["data"]
            d2.update(d1)

            d = logs_rcvd[0]
            d["is_sender"] = -1
            d["data"] = d2
            pprint.pprint(d)

def monitor_publishers(socket_mgr):
    while True:
        # print((time.time() - socket_mgr.last_update_time) >= socket_mgr.update_cycle )
        # if (time.time() - socket_mgr.last_update_time) >= socket_mgr.update_cycle:
        socket_mgr.check_publishers_file()
        time.sleep(socket_mgr.update_cycle)

if __name__ == "__main__":
    worker = 5
    socket_mgr = SocketManager(10)
    socket_mgr.subscribe_topic()
    with ThreadPoolExecutor(max_workers=worker) as executor:
        executor.submit(monitor_publishers, socket_mgr)
        while True:
            # Receives a string format message
            data = socket_mgr.socket.recv_json()
            print(data)
            executor.submit(process_event, data)
            # print((time.time() - socket_mgr.last_update_time) >= socket_mgr.update_cycle )
            # if (time.time() - socket_mgr.last_update_time) >= socket_mgr.update_cycle:
            #     socket_mgr.check_publishers_file()

        # for i in range(worker):
        #     executor.submit(process_event, i+1)
