import json
from subprocess import Popen, PIPE
from flask import Flask, request, jsonify
from Config import Config
import redis

app = Flask(__name__)
redis_connection = redis.Redis(host=Config.redis_cache_server_ip, port=Config.redis_cache_server_port, db=0)


@app.route('/cat_file', methods=['POST'])
def get_cat_data():
    data = request.json
    file_path = data["path"]
    proc = Popen(['cat', file_path], universal_newlines=True, stdout=PIPE, stderr=PIPE)
    res, err = proc.communicate()
    return jsonify({"out_put": res, "error": err})


@app.route('/lctl_get_param', methods=['POST'])
def get_lctl_data():
    data = request.json
    file_path = data["path"]
    ost_dir_name = data["ost_dir_name"]
    time_stamp = data["time_stamp"]
    redis_key = "{}_{}".format(ost_dir_name, time_stamp)
    response_body = redis_connection.get(redis_key)
    if response_body is None:
        proc = Popen(['lctl', 'get_param', file_path], universal_newlines=True, stdout=PIPE, stderr=PIPE)
        res, err = proc.communicate()
        response_body = {"out_put": res, "error": err}
        redis_connection.set(redis_key, json.dumps(response_body), ex=Config.expire_ttl)
        return jsonify(response_body)
    else:
        return jsonify(json.loads(response_body))


if __name__ == '__main__':
    app.run(Config.flask_app_agent_ip, Config.flask_app_agent_port)
