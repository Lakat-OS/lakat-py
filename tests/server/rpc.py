import requests
import json
from config.rpc_cfg import RPC_PORT
from config.encode_cfg import ENCODING_FUNCTION
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA, BUCKET_ID_TYPE_NO_REF
from utils.encode.bytes import encode_bytes_to_base64_str, decode_base64_str_to_bytes

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

def test_create_genesis_branch():
    branch_type = 1  # Example branch type
    signature = encode_bytes_to_base64_str(b"example_signature")
    accept_conflicts = False
    msg = "Test genesis branch message"

    response = json_rpc_call("create_genesis_branch", [branch_type, signature, accept_conflicts, msg])
    
    assert 'result' in response, "Response should contain a result field"
    branch_id = response['result']
    assert isinstance(branch_id, str), "Expected branch ID to be a string"
    assert len(branch_id) > 0, "Expected non-empty branch ID"

    print("Test 'create_genesis_branch' passed with branch ID:", branch_id)


def test_submit_content_to_twig():

    branch_type = 1  # Example branch type
    signature = encode_bytes_to_base64_str(bytes(0))
    accept_conflicts = False
    msg = "Test genesis branch message"

    response = json_rpc_call("create_genesis_branch", [branch_type, signature, accept_conflicts, msg])
    # First, create a genesis branch

    branch_id = response["result"]

    # contents = [
    #     {"data": encode_bytes_to_base64_str("Hallo".encode(ENCODING_FUNCTION)),  
    #     "schema": DEFAULT_ATOMIC_BUCKET_SCHEMA, 
    #     "parent_id": branch_id, "signature": encode_bytes_to_base64_str(bytes(1)), 
    #     "refs": []},
    #     {"data": encode_bytes_to_base64_str("Welt".encode(ENCODING_FUNCTION)),  
    #     "schema": DEFAULT_ATOMIC_BUCKET_SCHEMA, 
    #     "parent_id": branch_id, "signature": encode_bytes_to_base64_str(bytes(1)), 
    #     "refs": []},
    #     {"data": {
    #         "order": [
    #             {"id": 0, "type": BUCKET_ID_TYPE_NO_REF},
    #             {"id": 1, "type": BUCKET_ID_TYPE_NO_REF}], 
    #         "name": encode_bytes_to_base64_str("Hallo Welt".encode(ENCODING_FUNCTION))},
    #     "schema": DEFAULT_MOLECULAR_BUCKET_SCHEMA,
    #     "parent_id": branch_id, "signature": encode_bytes_to_base64_str(bytes(1)),  "refs": []}]
    
    contents = [
        {
            "data": "Hallo",  
            "schema": DEFAULT_ATOMIC_BUCKET_SCHEMA, 
            "parent_id": encode_bytes_to_base64_str(bytes(0)), 
            "signature": encode_bytes_to_base64_str(bytes(1)), 
            "refs": []
        },
        {
            "data": "Welt",  
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
                "name": "Hallo Welt"},
            "schema": DEFAULT_MOLECULAR_BUCKET_SCHEMA,
            "parent_id": encode_bytes_to_base64_str(bytes(0)), 
            "signature": encode_bytes_to_base64_str(bytes(1)), 
            "refs": []
        }]

    public_key = encode_bytes_to_base64_str(bytes(1))
    proof = encode_bytes_to_base64_str(bytes(1))
    submit_msg = "Test submit message"
    response = json_rpc_call("submit_content_to_twig", [branch_id, contents, public_key, proof, submit_msg])
    
    assert 'result' in response, "Response should contain a result field"
    branch_head_id = response['result']
    assert isinstance(branch_head_id, str), "Expected branch head ID to be a string"
    assert len(branch_head_id) > 0, "Expected non-empty branch head ID"

    print("Test 'submit_content_to_twig' passed with branch head ID:", branch_head_id)


# print(json_rpc_call("create_genesis_branch", {
#     "branch_type": 1,
#     "signature": "0x1234567890",
#     "accept_conflicts": True,
#     "msg": "Hello, World!" 
#     }))

# print(json_rpc_call("restart_db_with_name", {"name": "new_lakat_db_2"}))
# print(json_rpc_call("say_hello"))

if __name__ == "__main__":
    # test_create_genesis_branch()
    test_submit_content_to_twig()
