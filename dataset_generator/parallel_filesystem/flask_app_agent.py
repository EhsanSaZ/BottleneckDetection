from subprocess import Popen, PIPE
from flask import Flask, request, jsonify

app = Flask(__name__)


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
    proc = Popen(['lctl', 'get_param', file_path], universal_newlines=True, stdout=PIPE, stderr=PIPE)
    res, err = proc.communicate()
    return jsonify({"out_put": res, "error": err})


if __name__ == '__main__':
    app.run("0.0.0.0", 1234)
