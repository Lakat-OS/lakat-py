from utils.format.schema import check_argument, convert_to_bytes_based_on_schema, convert_from_bytes_based_on_schema
from config.encode_cfg import ENCODING_FUNCTION
from utils.encode.language import encode_string

def wrap_rpc_call(function: callable, schema: dict, kwargs: dict):
    # check arguments (TODO: Should be inside the function)
    check_argument(arg=kwargs, schema=schema)
    # convert arguments to bytes
    converted_kwargs = convert_to_bytes_based_on_schema(schema=schema, data=kwargs)
    # call function and convert result to stringified bytes dictionary
    data = function(**converted_kwargs)
    return convert_from_bytes_based_on_schema(schema=schema["response"], data=data)