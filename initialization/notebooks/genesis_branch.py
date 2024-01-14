import lakat.branch.functions as lakat_branch_functions
import lakat.submit.functions as lakat_submit_functions
import lakat.storage.local_storage as lakat_storage_functions
from utils.format.schema import check_argument, convert_to_bytes_based_on_schema, convert_from_bytes_based_on_schema
from config.branch_cfg import PROPER_BRANCH_TYPE_ID, TWIG_BRANCH_TYPE_ID
from utils.encode.bytes import encode_bytes_to_base64_str, decode_base64_str_to_bytes
# from config.encode_cfg import ENCODING_FUNCTION
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA, BUCKET_ID_TYPE_NO_REF
# from utils.encode.bytes import encode_bytes_to_base64_str, decode_base64_str_to_bytes

def test_create_genesis_branch(debug=True):
    # some fake signature encoded in bytes64 
    signature = encode_bytes_to_base64_str(bytes(0))
    accept_conflicts = False
    msg = 'Genesis Submit'
    name = 'Genesis Branch'
    create_branch_kwargs = dict(branch_type=TWIG_BRANCH_TYPE_ID, name=name, signature=signature, accept_conflicts=accept_conflicts, msg=msg)
    check_argument(arg=create_branch_kwargs, schema=lakat_branch_functions.create_genesis_branch_schema)
    converted_kwargs = convert_to_bytes_based_on_schema(schema=lakat_branch_functions.create_genesis_branch_schema, data=create_branch_kwargs)
    response = lakat_branch_functions.create_genesis_branch(**converted_kwargs)
    decoded_response = convert_from_bytes_based_on_schema(schema=lakat_branch_functions.create_genesis_branch_schema["response"], data=response)
    response = dict(branch_id=response, decoded_branch_id=decoded_response)
    if debug: 
        print('new branch id:', response)
    return response

def test_create_genesis_branch_with_initial_submit(debug=True):

    genesis_branch_response = test_create_genesis_branch(debug=debug)
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
    check_argument(arg=submit_kwargs, schema=lakat_submit_functions.submit_content_for_twig_schema)
    converted_submit_kwargs = convert_to_bytes_based_on_schema(schema=lakat_submit_functions.submit_content_for_twig_schema, data=submit_kwargs)
    submit_response = lakat_submit_functions.submit_content_for_twig(**converted_submit_kwargs)
    decoded_submit_response = convert_from_bytes_based_on_schema(schema=lakat_submit_functions.submit_content_for_twig_schema["response"], data=submit_response)
    response = dict(branch_head_id=submit_response, decoded_branch_head_id=decoded_submit_response)
    if debug:
        print("decoded new head state id:", response)
    return dict(**genesis_branch_response, **response)


if __name__ == '__main__':
    test_create_genesis_branch_with_initial_submit(debug=True)