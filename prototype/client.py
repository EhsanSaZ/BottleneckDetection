from tinydb import TinyDB, Query
import zmq
import json
import pprint

host = "127.0.0.1"
port = "5001"

db = TinyDB('db.json')
logs = Query()

# Creates a socket instance
context = zmq.Context()
socket = context.socket(zmq.SUB)

# Connects to a bound socket
socket.connect("tcp://{}:{}".format(host, port))

# Subscribes to all topics
socket.subscribe("")


while True:
    # Receives a string format message
    data = socket.recv_json()
    db.insert(data)
    
    logs_rcvd = db.search(logs.epoch == data["epoch"])
    
    if len(logs_rcvd) == 2:
        d1 = dict(logs_rcvd[0]["data"])
        d2 = dict(logs_rcvd[1]["data"])
        d2.update(d1)
        d = logs_rcvd[0]
        d["source"] = -1
        d["data"] = d2
        pprint.pprint(d)
        
if len(logs_rcvd) > 2:
    db.truncate()