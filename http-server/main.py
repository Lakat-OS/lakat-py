from flask import Flask, request, jsonify
import requests
import json

print(dir(requests))

app = Flask(__name__)
RPC_SERVER_URL = 'http://rpc-server:4000'  # Adjust if necessary
# RPC_SERVER_URL = "http://127.0.0.1:4000"

def json_rpc_call(method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(RPC_SERVER_URL, json=payload, headers=headers)
    return response.json()

@app.route('/create_genesis_branch', methods=['POST'])
def create_genesis_branch():
    data = request.json
    return jsonify(json_rpc_call("create_genesis_branch", data))

@app.route('/restart_db_with_name', methods=['POST'])
def restart_db_with_name():
    data = request.json
    return jsonify(json_rpc_call("restart_db_with_name", data))

@app.route('/restart_db', methods=['GET'])
def restart_db():
    return jsonify(json_rpc_call("restart_db", {}))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
