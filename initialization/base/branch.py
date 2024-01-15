import lakat.branch.functions as lakat_branch_functions
from utils.format.schema import check_argument, convert_to_bytes_based_on_schema, convert_from_bytes_based_on_schema
from config.branch_cfg import PROPER_BRANCH_TYPE_ID, TWIG_BRANCH_TYPE_ID
from utils.encode.bytes import encode_bytes_to_base64_str

def create_genesis_twig_branch(branch_name, msg, accept_conflicts=True, debug=True):
    # some fake signature encoded in bytes64 
    signature = encode_bytes_to_base64_str(bytes(0))
    create_branch_kwargs = dict(branch_type=TWIG_BRANCH_TYPE_ID, name=branch_name, signature=signature, accept_conflicts=accept_conflicts, msg=msg)
    check_argument(arg=create_branch_kwargs, schema=lakat_branch_functions.create_genesis_branch_schema)
    converted_kwargs = convert_to_bytes_based_on_schema(schema=lakat_branch_functions.create_genesis_branch_schema, data=create_branch_kwargs)
    response = lakat_branch_functions.create_genesis_branch(**converted_kwargs)
    decoded_response = convert_from_bytes_based_on_schema(schema=lakat_branch_functions.create_genesis_branch_schema["response"], data=response)
    response = dict(branch_id=response, decoded_branch_id=decoded_response)
    if debug: 
        print('new branch id:', response)
    return response