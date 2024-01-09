from copy import deepcopy
from typing import List, Mapping
from config.encode_cfg import ENCODING_FUNCTION
from utils.encode.bytes import decode_base64_str_to_bytes, encode_bytes_to_base64_str
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from lakat.errors import ERR_S_BCKT_1

def check_argument(arg, schema):
    try:
        validate(instance=arg, schema=schema)
        return True
    except ValidationError as e:
        raise ERR_S_BCKT_1(e.message)
    

# def convert_to_bytes_based_on_schema(schema, data):
#     if schema.get('type') == 'object' and 'properties' in schema:
#         # If the current schema element is an object, construct a new object
#         new_object = {}
#         for prop, prop_schema in schema['properties'].items():
#             if prop in data:
#                 new_object[prop] = convert_to_bytes_based_on_schema(prop_schema, data[prop])
#         return new_object
#     elif schema.get('type') == 'array' and 'items' in schema:
#         # If the current schema element is an array, process each item
#         return [convert_to_bytes_based_on_schema(schema['items'], item) for item in data]
#     elif schema.get('type') == 'string' and schema.get('format') == 'byte':
#         # If the current schema element is a base64-encoded string, decode it
#         return decode_base64_str_to_bytes(data)
#     else:
#         # For all other cases, return the data as-is
#         return data

def convert_bytes_based_on_schema(schema, data, conversion: callable, error_messages=""):
    try:
        # Base case: if the data matches a base64-encoded byte string schema
        if schema.get('type') == 'string' and schema.get('format') == 'byte':
            return conversion(data), False, error_messages

        # Handle objects (dicts in Python)
        elif schema.get('type') == 'object' and 'properties' in schema:
            if not isinstance(data, dict):
                return None, True, f"{error_messages}; Expected a dict for object type in schema"
            new_object = {}
            for key, value in data.items():
                if key in schema['properties']:
                    result, is_erroneous, new_error_messages = convert_bytes_based_on_schema(
                        schema['properties'][key], 
                        value, 
                        conversion, 
                        error_messages)
                    new_object[key] = result
                    error_messages = new_error_messages if is_erroneous else error_messages
            return new_object, bool(error_messages), error_messages

        # Handle arrays (lists in Python)
        elif schema.get('type') == 'array' and 'items' in schema:
            if not isinstance(data, list):
                return None, True, f"{error_messages}; Expected a list for array type in schema"
            new_array = []
            for item in data:
                result, is_erroneous, new_error_messages = convert_bytes_based_on_schema(
                    schema['items'], 
                    item, 
                    conversion,
                    error_messages)
                new_array.append(result)
                error_messages = new_error_messages if is_erroneous else error_messages
            return new_array, bool(error_messages), error_messages

        # Handle oneOf by attempting each schema until one succeeds
        elif 'oneOf' in schema:
            for sub_schema in schema['oneOf']:
                result, is_erroneous, new_error_messages = convert_bytes_based_on_schema(
                    sub_schema, 
                    data, 
                    conversion,
                    error_messages)
                if not is_erroneous:
                    return result, False, new_error_messages
            return None, True, f"{error_messages}; Data does not match any of the 'oneOf' schemas"

        # For all other cases, return the data as is
        else:
            return data, False, error_messages

    except Exception as e:
        return None, True, f"{error_messages}; {str(e)}"
    

    
def convert_to_bytes_based_on_schema(schema, data):
    result, is_erroneous, new_error_messages =  convert_bytes_based_on_schema(schema=schema, data=data, conversion=decode_base64_str_to_bytes)
    if is_erroneous:
        raise ERR_S_BCKT_1(new_error_messages)
    return result

def convert_from_bytes_based_on_schema(schema, data):
    result, is_erroneous, new_error_messages =  convert_bytes_based_on_schema(schema=schema, data=data, conversion=encode_bytes_to_base64_str)
    if is_erroneous:
        raise ERR_S_BCKT_1(new_error_messages)
    return result

# def convert_from_bytes_based_on_schema(schema, data):
#     if schema.get('type') == 'object' and 'properties' in schema:
#         # If the current schema element is an object, construct a new object
#         new_object = {}
#         for prop, prop_schema in schema['properties'].items():
#             if prop in data:
#                 new_object[prop] = convert_to_bytes_based_on_schema(prop_schema, data[prop])
#         return new_object
#     elif schema.get('type') == 'array' and 'items' in schema:
#         # If the current schema element is an array, process each item
#         return [convert_to_bytes_based_on_schema(schema['items'], item) for item in data]
#     elif schema.get('type') == 'string' and schema.get('format') == 'byte':
#         # If the current schema element is a base64-encoded string, decode it
#         return encode_bytes_to_base64_str(data)
#     else:
#         # For all other cases, return the data as-is
#         return data
    

bytes_schema = {"type": "string", "format": "byte"}