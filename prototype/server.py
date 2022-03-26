import uuid
import zmq
import time
import json

host = "127.0.0.1"
port = "5001"

# Creates a socket instance
context = zmq.Context()
socket = context.socket(zmq.PUB)

# Binds the socket to a predefined port on localhost
socket.bind("tcp://{}:{}".format(host, port))

num = 0
transfer_id = str(uuid.uuid4())
while True:
    # Sends a string message
    sender = {
        "source": 1,
        "transfer_id": transfer_id,
        "epoch": num,
        "data": {
            "key1": "Hello"
        }
    }
    
    receiver = {
        "source": 0,
        "transfer_id": transfer_id,
        "epoch": num,
        "data": {
            "key2": "World"
        }
    }
    
    socket.send_json(sender)
    socket.send_json(receiver)
    
    num += 1
    time.sleep(1)