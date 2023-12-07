from config.bucket_cfg import (
    DEFAULT_ATOMIC_BUCKET_SCHEMA,
    DEFAULT_MOLECULAR_BUCKET_SCHEMA)
from utils.serialize import unserialize

def check_schema(data: bytes, schema: int)-> bool:
    ## schema could be the id of a schema bucket
    msg = "Match"
    errcode = "0"
    if schema==DEFAULT_MOLECULAR_BUCKET_SCHEMA:
        unserialized_data = unserialize(data)
        print('unserialized_data',unserialized_data)
        if not isinstance(unserialized_data, dict):
            errcode = "1"
            msg = "Not Dict"
            return False, msg, errcode
        if not "order" in unserialized_data.keys():
            errcode = "2.1"
            msg = "No Order Key"
        if not "name" in unserialized_data.keys():
            errcode = "2.2"
            msg = "No Name Key"
        if not isinstance(unserialized_data["order"], list):
            errcode = "3.1"
            msg = "Not List"
        if len(unserialized_data["order"])==0:
            errcode = "3.2"
            msg = "Has Empty Order List"
            return False, msg, errcode 
        if not all( all(k in list(entry.keys()) for k in ["id", "type"]) for entry in unserialized_data["order"]):
            errcode = "3.3"
            msg = "Order List Needs Id and Type"
            return False, msg, errcode
        return True, msg, errcode
    elif schema==DEFAULT_ATOMIC_BUCKET_SCHEMA:
        ## for now just return true
        return True, msg, errcode
    else:
        ## for now just return true
        return True, msg, errcode