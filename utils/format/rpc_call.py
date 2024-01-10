from utils.format.schema import check_argument, convert_to_bytes_based_on_schema, convert_from_bytes_based_on_schema
from config.encode_cfg import ENCODING_FUNCTION
from utils.encode.language import encode_string

def wrap_rpc_call(function: callable, call_schema: dict, response_schema: dict, kwargs: dict):
    # check arguments (TODO: Should be inside the function)
    check_argument(arg=kwargs, schema=call_schema)
    # convert arguments to bytes
    converted_kwargs = convert_to_bytes_based_on_schema(schema=call_schema, data=kwargs)
    # encode msg (TODO: Should already be received encoded actually)
    if "msg" in converted_kwargs:
        converted_kwargs["msg"] = encode_string(converted_kwargs["msg"], ENCODING_FUNCTION)
    # call function and convert result to stringified bytes dictionary
    print("converted_kwargs", converted_kwargs)
    return convert_from_bytes_based_on_schema(schema=response_schema, data=function(**converted_kwargs))