import requests
import json

def json_rpc_call(method, params=None):
    url = "http://localhost:4000/"
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    return response

print(json_rpc_call("compute_sqrt", {"x": 16}))
print(json_rpc_call("say_hello"))
