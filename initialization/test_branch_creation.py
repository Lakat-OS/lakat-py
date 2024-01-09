from config.bucket_cfg import DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA
from utils.serialize import serialize
from initialization.test_interaction import getDefaultEmptyInteractions
from lakat.submit_old import content_submit

def branch_creation(public_key, verbose=True):
    branchId = None
    contents = list()
    data_dict = {
            "schema_id": DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA,
            "public_key": public_key,
            "parent_bucket": None,
            "data": serialize({}),
            "refs": serialize([])
        }
    contents.append(serialize(data_dict))


    # socialRefs = [{"id": someId, "value":someValue}]
    interactions = getDefaultEmptyInteractions()

    res = content_submit(
            contents=contents,
            interactions=interactions, 
            branchId=None, 
            proof=b'', 
            msg="NAME REGISTRY AND INITIAL SUBMIT", 
            create_branch=True)

    for key, value in res.items():
        if key == "branch_id": 
            branchId = value
            break
    
    if verbose:
        print(res)
    
    return branchId