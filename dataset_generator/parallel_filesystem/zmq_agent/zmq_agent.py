# import sys
import json
import threading
import traceback
from subprocess import Popen, PIPE

import redis
import zmq
from zmq import ZMQError

from Config import Config

redis_connection = redis.Redis(host=Config.redis_cache_server_ip, port=Config.redis_cache_server_port, db=0)
context = zmq.Context()


def get_lctl_data():
    socket = context.socket(zmq.REP)
    socket.bind("tcp://{}:{}".format(Config.zmq_agent_ip, Config.zmq_agent_port))
    while True:
        try:
            data = socket.recv_json()
            # file_path = data["path"]
            ost_dir_name = data["ost_dir_name"]
            time_stamp = data["time_stamp"]
            redis_key = "{}_{}".format(ost_dir_name, time_stamp)
            response_body = redis_connection.get(redis_key)
            if response_body is None:
                file_path = "obdfilter." + ost_dir_name + ".stats"
                proc = Popen(['lctl', 'get_param', file_path], universal_newlines=True, stdout=PIPE, stderr=PIPE)
                res, err = proc.communicate()
                # res, err = "RES", "ERR"
                response_body = {"out_put": res, "error": err}
                redis_connection.set(redis_key,  json.dumps(response_body), ex=Config.expire_ttl)
                socket.send_json(response_body)
            else:
                socket.send_json(json.loads(response_body))
        except FileNotFoundError as err:
            socket.send_json({"out_put": "", "error": str(err)})
        except ZMQError as e:
            if e.strerror == "Operation cannot be accomplished in current state":
                socket.close()
                socket = context.socket(zmq.REP)
                socket.bind("tcp://{}:{}".format(Config.zmq_agent_ip, Config.zmq_agent_port))
            else:
                traceback.print_exc()
                socket.send_json({"out_put": "", "error": e.strerror})
        except Exception as e:
            traceback.print_exc()
            socket.send_json({"out_put": "", "error": str(e)})
            # break

if __name__ == '__main__':
    server_thread = threading.Thread(target=get_lctl_data)
    server_thread.start()
    server_thread.join()
    context.term()