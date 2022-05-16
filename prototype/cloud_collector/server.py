import uuid
import zmq
import time
import numpy as np
from concurrent.futures.thread import ThreadPoolExecutor
import random

host = "127.0.0.1"
port = "5001"

# Creates a socket instance
context = zmq.Context()
socket = context.socket(zmq.PUB)

# Binds the socket to a predefined port on localhost
socket.bind("tcp://{}:{}".format(host, port))


def send_data(num):
    transfer_id = str(uuid.uuid4())
    num = 0
    while True:
        # print(transfer_id, num)
        sender = {
            "is_sender": 1,
            "transfer_ID": transfer_id,
            "sequence_number": num,
            "data": {
                "key1": "Hello"
            }
        }

        receiver = {
            "is_sender": 0,
            "transfer_ID": transfer_id,
            "sequence_number": num,
            "data": {
                "key2": "World"
            }
        }
        if random.random() > 0.5:
            socket.send_json(sender)
            time.sleep(random.random())
            socket.send_json(receiver)
        else:
            socket.send_json(receiver)
            time.sleep(random.random())
            socket.send_json(sender)
        num += 1

        time.sleep(1)
    # Sends a string message


if __name__ == "__main__":
    n = 100000
    # start = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(n):
            executor.submit(send_data, "")
    # end = time.time()

    # print(f"total: {n}, time: {np.round(end-start, 2)}")

    
