import zmq
import json
import pprint
from pathlib import Path
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from BetterJSONStorage import BetterJSONStorage
from concurrent.futures.thread import ThreadPoolExecutor

host = "127.0.0.1"
port = "5001"
path = Path("db.json")
# db = TinyDB(path, access_mode="r+", storage=BetterJSONStorage)
db = TinyDB(storage=MemoryStorage)
tm = db.table('transfer_metrics')
logs = Query()

# Creates a socket instance
context = zmq.Context()
socket = context.socket(zmq.SUB)

# Connects to a bound socket
socket.connect("tcp://{}:{}".format(host, port))

# Subscribes to all topics
socket.subscribe("")


def process_event(indx):
    print(f'worker: {indx}')
    while True:
        # Receives a string format message
        data = socket.recv_json()
        # print(data)
        tm.insert(data)
        
        logs_rcvd = tm.search((logs.epoch == data["epoch"]) & (logs.transfer_id == data["transfer_id"]))
        
        if len(logs_rcvd) > 2:
            tm.truncate()
            continue
        
        if len(logs_rcvd) == 2:
            sources = set()
            
            for log in logs_rcvd:
                sources.add(log["source"])
            
            if len(sources) == 2:
                d1 = logs_rcvd[0]["data"]
                d2 = logs_rcvd[1]["data"]
                d2.update(d1)
                    
                d = logs_rcvd[0]
                d["source"] = -1
                d["data"] = d2
                pprint.pprint(d)


if __name__ == "__main__":
    worker = 20
    with ThreadPoolExecutor(max_workers=worker) as executor:
        for i in range(worker):
            executor.submit(process_event, i+1)
