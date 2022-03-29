import uuid
import zmq
import time
import numpy as np
from concurrent.futures.thread import ThreadPoolExecutor


host = "127.0.0.1"
port = "5001"

# Creates a socket instance
context = zmq.Context()
socket = context.socket(zmq.PUB)

# Binds the socket to a predefined port on localhost
socket.bind("tcp://{}:{}".format(host, port))

transfer_id = str(uuid.uuid4())

def send_data(num):
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


if __name__ == "__main__":
    n = 10000
    start = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(n):
            executor.submit(send_data, i+1)
    end = time.time()

    print(f"total: {n}, time: {np.round(end-start, 2)}")

    
