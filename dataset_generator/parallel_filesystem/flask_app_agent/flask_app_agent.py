import json
from subprocess import Popen, PIPE
from flask import Flask, request, jsonify
from Config import Config
from ost_cache import LustreOStCache
import global_cache

app = Flask(__name__)


@app.route('/cat_file', methods=['POST'])
def get_cat_data():
    data = request.json
    file_path = data["path"]
    proc = Popen(['cat', file_path], universal_newlines=True, stdout=PIPE, stderr=PIPE)
    res, err = proc.communicate()
    return jsonify({"out_put": res, "error": err})


@app.route('/lctl_get_param_v1', methods=['POST'])
def get_lctl_data():
    try:
        data = request.json
        file_path = data["path"]
        proc = Popen(['lctl', 'get_param', file_path], universal_newlines=True, stdout=PIPE, stderr=PIPE)
        res, err = proc.communicate()
        return jsonify({"out_put": res, "error": err})
    except Exception as e:
        return jsonify({"out_put": "", "error": "internal error" + str(e)})


@app.route('/lctl_get_param', methods=['POST'])
def get_latest_ost():
    try:
        #print(request.json)
        #print(global_cache.ost_metrics_dict)
        data = request.json
        file_path = data["path"]
        output = global_cache.ost_metrics_dict.get(file_path).get("stats") or None
        if output is None:
            return jsonify({"out_put": "", "error": "OST name {} not found".format(file_path)}), 404
        else:
            return jsonify({"out_put": output, "error": 'err'}), 200
    except Exception as e:
        return jsonify({"out_put": "", "error": "internal error" + str(e)})

@app.route('/lctl_get_param_v2', methods=['GET'])
def get_latest_ost_get_method():
    try:
        #print(request.json)
        #print(global_cache.ost_metrics_dict)
        # data = request.json
        # file_path = data["path"]
        # output = global_cache.ost_metrics_dict.get() or None
        # if output is None:
        #     return jsonify({"out_put": "", "error": "OST name {} not found".format(file_path)}), 404
        # else:
        d = dict(global_cache.ost_metrics_dict)
        return jsonify({"out_put": d, "error": 'err'}), 200
    except Exception as e:
        return jsonify({"out_put": "", "error": "internal error" + str(e)})

ost_metric_cache_process = LustreOStCache(global_cache.ost_metrics_dict, 1)
ost_metric_cache_process.start()

if __name__ == '__main__':
    app.run(Config.flask_app_agent_ip, Config.flask_app_agent_port)
    ost_metric_cache_process.join()
