import requests
import json

def json_rpc_call(method, params=None):
    url = "http://localhost:3355/"
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


print(json_rpc_call("create_genesis_branch", {
    "branch_type": 1,
    "signature": "0x1234567890",
    "accept_conflicts": True,
    "msg": "Hello, World!" 
    }))

# print(json_rpc_call("restart_db_with_name", {"name": "new_lakat_db_2"}))
# print(json_rpc_call("say_hello"))
