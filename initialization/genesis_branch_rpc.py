import requests
import json
from config.rpc_cfg import RPC_PORT
from utils.encode.bytes import encode_bytes_to_base64_str, decode_base64_str_to_bytes
from config.branch_cfg import PROPER_BRANCH_TYPE_ID, TWIG_BRANCH_TYPE_ID
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA, BUCKET_ID_TYPE_NO_REF

def json_rpc_call(method, params=None):
    url = f"http://localhost:{RPC_PORT}/"
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

def test_rpc_create_genesis_branch(debug=True):

    signature = encode_bytes_to_base64_str(bytes(0))
    accept_conflicts = False
    msg = 'Genesis Submit'
    name = 'Genesis Branch'
    create_branch_kwargs = dict(branch_type=TWIG_BRANCH_TYPE_ID, name=name, signature=signature, accept_conflicts=accept_conflicts, msg=msg)
    # convert the keyword arguments to a list of values for the rpc call
    create_branch_rpc_call_list = list(create_branch_kwargs.values())
    # make the rpc call and get the response
    rpc_response = json_rpc_call(method="create_genesis_branch", params=create_branch_rpc_call_list)
    # response is inside the result field
    decoded_branch_id = rpc_response['result']
    branch_id = decode_base64_str_to_bytes(decoded_branch_id)
    if debug:
        print("Test 'create_genesis_branch' passed with branch ID:", branch_id, "\nand base64 decoded branch ID:", decoded_branch_id)
    response = dict(branch_id=branch_id, decoded_branch_id=decoded_branch_id)
    return response


def test_rpc_create_genesis_branch_with_initial_submit(debug=True):
    genesis_branch_response = test_rpc_create_genesis_branch(debug=debug)

    contents = [
        {
            "data": "Hello",  
            "schema": DEFAULT_ATOMIC_BUCKET_SCHEMA, 
            "parent_id": encode_bytes_to_base64_str(bytes(0)), 
            "signature": encode_bytes_to_base64_str(bytes(1)), 
            "refs": []
        },
        {
            "data": "World",  
            "schema": DEFAULT_ATOMIC_BUCKET_SCHEMA, 
            "parent_id": encode_bytes_to_base64_str(bytes(0)), 
            "signature": encode_bytes_to_base64_str(bytes(1)), 
            "refs": []
        },
        {
            "data": {
                "order": [
                    {"id": 0, "type": BUCKET_ID_TYPE_NO_REF},
                    {"id": 1, "type": BUCKET_ID_TYPE_NO_REF}], 
                "name": "Dummy Article Name"},
            "schema": DEFAULT_MOLECULAR_BUCKET_SCHEMA,
            "parent_id": encode_bytes_to_base64_str(bytes(0)), 
            "signature": encode_bytes_to_base64_str(bytes(1)), 
            "refs": []
        }]

    public_key = encode_bytes_to_base64_str(bytes(1))
    proof = encode_bytes_to_base64_str(bytes(1))
    submit_msg = "Initial Submit"
    submit_kwargs = dict(branch_id=genesis_branch_response["decoded_branch_id"], contents=contents, public_key=public_key, proof=proof, msg=submit_msg)
    submit_kwargs_rpc = list(submit_kwargs.values())
    # print('before rpc call: ', submit_kwargs_rpc)
    rpc_response_submit = json_rpc_call(method="submit_content_to_twig", params=submit_kwargs_rpc)
    decoded_branch_head_state_id = rpc_response_submit['result']
    branch_head_state_id = decode_base64_str_to_bytes(decoded_branch_head_state_id)
    response_submit = dict(
        branch_head_state_id=branch_head_state_id, 
        decoded_branch_head_state_id=decoded_branch_head_state_id)
    if debug:
        print("Test 'submit_content_to_branch' passed with branch head state Id:", branch_head_state_id, "\nand base64 decoded id:", decoded_branch_head_state_id)
    return dict(**response_submit, **genesis_branch_response)