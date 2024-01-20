import json
import requests
from config.rpc_cfg import RPC_PORT, RPC_HOST

def json_rpc_call(method, params=None):
    url = f"http://{RPC_HOST}:{RPC_PORT}/"
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": 0,
    }
    encoded_payload = json.dumps(payload).encode('utf-8')
    response = requests.post(url, data=encoded_payload, headers=headers)
    # print(response)#
    return response.json()