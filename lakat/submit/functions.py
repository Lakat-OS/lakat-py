from copy import deepcopy
import random
from lakat.bucket.functions import prepare_bucket, get_bucket_ids_from_order
from interfaces.submit import SUBMIT, SUBMIT_TRACE
from interfaces.branch import BRANCH
from utils.encode.hashing import (
    make_lakat_cid_and_serialize,
    make_lakat_cid_and_serialize_from_suffix,
    deserialize_from_key)
from config.env import DEV_ENVIRONMENT
from config.encode_cfg import DEFAULT_SUFFIX_CROP, DEV_SUFFIX_CROP, DEFAULT_CODEC
from db.namespaces import (BRANCH_NS, ATOMIC_BUCKET_NS, MOLECULAR_BUCKET_NS, BRANCH_HEAD_NS, SUBMIT_NS, SUBMIT_TRACE_NS)
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA
from config.branch_cfg import PROPER_BRANCH_TYPE_ID
from config.trie_response_cfg import TRIE_SUCCESS_CODE
from lakat.timestamp import getTimestamp
from typing import Mapping, Optional, Tuple, Union, List
from lakat.check import check_inputs
from lakat.errors import ERR_N_TRIE_1
from lakat.storage.local_storage import (commit_to_db, get_from_db, stage_many_to_db, stage_to_db)
from lakat.storage.trie_storage import (stage_name_trie, stage_data_trie, stage_interaction_trie, commit_name_trie_changes, commit_data_trie_changes, commit_interaction_trie_changes, get_data_trie, get_interaction_trie)
from config.encode_cfg import ENCODING_FUNCTION
from lakat.errors import (ERR_N_TCS_1, ERR_T_BCKT_1, ERR_N_TCS_2)
from schema.bucket import bucket_contents_schema
import utils.encode.language as language_utils


def submit_content_for_twig(branch_id: bytes, contents: any, public_key: bytes, proof: bytes, msg: bytes):

    ## CHECK INPUT TYPES
    # check_inputs("submit_content_to_twig", 
    #     branch_type=branch_type, signature=signature, accept_conflicts=accept_conflicts, msg=msg)
        
    ## CHECK PROOF


    submit_trace_dict = dict(  
        branchId=b"",  
        config=b"",
        newBranchHead=b"",
        submittedBucketsRefs=[],
        pullRequests=[],
        nameResolution=[],
        nameResolutionRoot=b"",
        nameTrie=[],
        dataTrie=[],
        reviewsTrace=[],
        socialTrace=[],
        socialRoot=b"",
        sprouts=[],
        sproutSelectionTrace=[])
    
    response = dict()

    ## DEFINE SUFFIX CROP
    if DEV_ENVIRONMENT in ["DEV", "LOCAL"]:
        suffix_crop = DEV_SUFFIX_CROP
    else:
        suffix_crop = DEFAULT_SUFFIX_CROP

    ## DEFINE TIMESTAMP
    creation_ts = getTimestamp()

    ## CREATE A RANDOM TRIE TOKEN 
    trie_token = random.randint(1, 2**32-1)

    ## FETCH BRANCH
    branch_head_id = get_from_db(branch_id)
    branch_serialized = get_from_db(branch_head_id)
    if not branch_serialized:
        raise ERR_N_TCS_1

    branch_dict = deserialize_from_key(branch_head_id, branch_serialized)
    # update submit_trace_dict
    submit_trace_dict["branchId"] = branch_id
    # update response
    response["branch_id"] = branch_id


    ## FIRST CREATE BRANCH PARAMS USED FOR BRANCH ID
    branch_params_for_head = dict(parent_id=branch_dict["parent_id"], creation_ts=creation_ts, signature=branch_dict["signature"])
    branch_params = deepcopy(branch_params_for_head)
    # create branch id
    branch_head_id, _ = make_lakat_cid_and_serialize(content=branch_params_for_head, codec=DEFAULT_CODEC, namespace=BRANCH_HEAD_NS, branch_id_1=branch_id, branch_id_2=branch_dict["parent_id"], crop=suffix_crop)
    # create namespace and add branch id and namespace to branch params and update branch config, too
    branch_params.update(dict(id=branch_id, ns=branch_dict["ns"], config=branch_dict["config"]))
    # add to db backlog
    stage_to_db(branch_id, branch_head_id)
    # add to submit_trace_backlog
    submit_trace_dict["newBranchHead"] = branch_head_id
    # TODO: DANGER: The attacker could overwrite the branch head with a different branch data (but same creation time and signature). A nonce could be used to prevent this. But we dont keep account data in the db.

    ## ADD THE BRANCH NAME TO THE BRANCH PARAMS
    branch_params.update(dict(name=branch_dict["name"]))

    ## ADD THE PARENT BRANCH TRIE INFORMATION 
    branch_params.update(dict(
        parent_name_resolution=branch_dict["parent_name_resolution"],
        parent_interaction=branch_dict["parent_interaction"],
        parent_data_trie=branch_dict["parent_data_trie"]))

    # CREATE BUCKETS
    index_to_bucket_id = dict()
    submittedBucketsRefs = [None] * len(contents)
    handledContents = list()
    for content_index, content in enumerate(contents):
        if content["schema"] != DEFAULT_ATOMIC_BUCKET_SCHEMA:
            continue 
        root_bucket_id, is_genesis, is_invalid_parent = get_root(
            parent_bucket=content["parent_id"], branch_id=branch_id, branch_suffix=branch_dict["ns"], token=trie_token)
        if is_invalid_parent:
            ERR_N_TCS_2(content_index)
        
        content_dict = dict(data = content["data"], signature= content["signature"], schema_id=content["schema"], parent_bucket=content["parent_id"], root_bucket=root_bucket_id, refs=content["refs"], public_key=public_key)
        bucket_id, bucket_data = prepare_bucket(content_dict=content_dict, namespace=ATOMIC_BUCKET_NS)
        # add bucket id to the mapping for the molecular bucket
        index_to_bucket_id[content_index] = bucket_id
        # store in data trie
        if is_genesis:
            root_bucket_id = bucket_id
        data_trie_root, data_trie_content = stage_data_trie(branch_id, branch_dict["ns"], root_bucket_id, bucket_id, token=trie_token)
        # add to db backlog
        stage_to_db(bucket_id, bucket_data)
        # add to submit_trace_backlog
        submittedBucketsRefs[content_index] = bucket_id
        handledContents.append(dict(schema=content["schema"], content_index=content_index, bucket_id=bucket_id))
        submit_trace_dict["dataTrie"].extend([key for key,_ in data_trie_content["db"]])


    # Create molecular bucket
    for content_index, content in enumerate(contents):
        if content["schema"] != DEFAULT_MOLECULAR_BUCKET_SCHEMA:
            continue
        # create the correctly formatted molecular data.
        molecular_data = get_bucket_ids_from_order(order=content["data"]["order"], index_to_bucket_id=index_to_bucket_id)
        
        root_bucket_id, is_genesis, is_invalid_parent = get_root(
            parent_bucket=content["parent_id"], branch_id=branch_id, branch_suffix=branch_dict["ns"], token=trie_token)
        if is_invalid_parent:
            ERR_N_TCS_2(content_index)

        content_dict = dict(data = molecular_data, signature= content["signature"], schema_id=content["schema"], parent_bucket=content["parent_id"], root_bucket=root_bucket_id, refs=content["refs"], public_key=public_key)
        bucket_id, bucket_data = prepare_bucket(content_dict=content_dict, namespace=MOLECULAR_BUCKET_NS)
        # store in data trie
        if is_genesis:
            root_bucket_id = bucket_id
        data_trie_root, data_trie_content = stage_data_trie(
            branch_id=branch_id, 
            branch_suffix=branch_dict["ns"], 
            key=root_bucket_id, 
            value=bucket_id, 
            token=trie_token)
        # add to db backlog
        stage_to_db(bucket_id, bucket_data)
        # add to submit_trace_backlog
        submittedBucketsRefs[content_index] = bucket_id
        handledContents.append(dict(schema=content["schema"], content_index=content_index, bucket_id=bucket_id))
        submit_trace_dict["dataTrie"].extend([key for key,_ in data_trie_content["db"]])

        # check if there is a name resolution entry
        new_name_registration = True
        if content["data"].get("name"):
            # TODO: Should think of a way to pass bytes(0) into this arg, so that this block will not be executed.
            if not language_utils.decode_bytes(content["data"].get("name")):
                new_name_registration = False 
        
        # FIXME!! I have to check if the article is already registered.  

        if not new_name_registration:
            branch_params.update(dict(name_resolution=branch_dict["name_resolution"]))
            continue

        # FIXME!! You must add the article root to the name resolution trie!! Not the current bucket id, but the root of the id (use the get_root function, because a new article has to be registered if already existing head is not the parent)

        # add to the name resolution trie 
        name_res_root, name_res_content = stage_name_trie(branch_id, branch_dict["ns"], content["data"]["name"], bucket_id, codec=DEFAULT_CODEC, token=trie_token)
        # update the name_resolution_pointer in the branch data
        branch_params.update(dict(name_resolution=name_res_root))
        # add to submit_trace_backlog
        submit_trace_dict["nameResolution"].append([content["data"]["name"], bucket_id])
        # add to submit_trace name_trie list
        submit_trace_dict["nameTrie"].extend([key for key,_ in name_res_content["db"]])
    
    if len(handledContents) != len(contents):
        raise Exception("Not all contents were handled.")
    # update submit_trace_dict
    submit_trace_dict["submittedBucketsRefs"] = submittedBucketsRefs
    # update response
    response["bucket_refs"] = submittedBucketsRefs
    response["registered_names"] = [
        {"name": name[0], "id": name[1]} for name in submit_trace_dict["nameResolution"]]

    # UPDATE INTERACTION TRIE
    branch_params.update(dict(interaction=branch_dict["interaction"]))
    # TODO: Integrate also social interactions, then update the social root, too, also in the trace

    # UPDATE SPROUTS
    branch_params.update(dict(sprouts=branch_dict["sprouts"], sprout_selection=branch_dict["sprout_selection"]))

    # CREATE SUBMIT TRACE
    submit_trace = SUBMIT_TRACE(**submit_trace_dict)
    # serialize config and add to db and trie backlog
    submit_trace_cid, submit_trace_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=submit_trace.__dict__,
        codec=DEFAULT_CODEC,
        namespace=SUBMIT_TRACE_NS,
        suffix=branch_dict["ns"])
    # add to db backlog
    stage_to_db(submit_trace_cid, submit_trace_serialized)
    # update response
    response["submit_trace_id"] = submit_trace_cid


    # CREATE SUBMIT
    submit = SUBMIT(parent_submit_id=branch_dict["stable_head"], submit_msg=msg, trie_root=data_trie_root, submit_trace=submit_trace_cid)
    # serialize config and add to db and trie backlog
    submit_cid, submit_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=submit.__dict__, codec=DEFAULT_CODEC, namespace=SUBMIT_NS, suffix=branch_dict["ns"])
    # add to db backlog
    stage_to_db(submit_cid, submit_serialized)
    # update branch params
    branch_params.update(dict(stable_head=submit_cid))
    # update response
    response["submit_id"] = submit_cid


    # CREATE BRANCH OBJECT
    branch = BRANCH(**branch_params)
    # serialize config and add to db and trie backlog
    new_branch_state_cid, branch_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=branch.__dict__, codec=DEFAULT_CODEC, namespace=BRANCH_NS, suffix=branch_dict["ns"])
    # add to db backlog
    stage_to_db(new_branch_state_cid, branch_serialized)
    # create a new branch head
    stage_to_db(branch_id, new_branch_state_cid)
    # update response
    response["branch_state_id"] = new_branch_state_cid

    ## COMMIT ALL TRIE CHANGES
    name_res_content = commit_name_trie_changes(branch_id=branch_id, token=trie_token)
    data_trie_content = commit_data_trie_changes(branch_id=branch_id, token=trie_token)
    # social_trie_content = commit_interaction_trie_changes(branch_id=branch_id, token=trie_token)
    
    ## STAGE ALL TRIE DATABASE COMMITS TO DB
    stage_many_to_db(name_res_content)
    stage_many_to_db(data_trie_content)
    # stage_many_to_db(social_trie_content)

    commit_to_db()
    # stage_many_to_db(social_trie_content)

    return response


# TODO: MOVE This function to bucket files
def get_root(parent_bucket, branch_id, branch_suffix, token=0x0):
    """
    Find the root bucket based on the parent bucket.

    If parent bucket is bytes(0), then this is a genesis bucket (the root will be zero, because the bucket cannot reference itself)

    If parent bucket id is not bytes(0) but is not to be found, then the is_invalid_parent flag will be raised. 

    If parent bucket id is found, one checks the remote or local database and recovers its root:
        - If its root is bytes(0) that parent must be a genesis bucket, i.e. the root.
        - If its root is not bytes(0) we check the head state of the bucket that is stored inside the data trie: 
            - If that head state is the parent bucket, we are still in the same chain and that root stays the root.
            - If that head state is not the parent bucket, other buckets must have been added previously. So we must create a new root, namely the parent bucket id
    """

    is_genesis = False
    is_invalid_parent = False
    if not parent_bucket:
        is_genesis = True
        return bytes(0), is_genesis, is_invalid_parent
    
    # Placeholder for checking if parent bucket is invalid
    parent_bucket_serialized = get_from_db(parent_bucket)
    if not parent_bucket_serialized:
        is_invalid_parent = True
        is_genesis = False
        return bytes(0), is_genesis, is_invalid_parent

    # Placeholder for checking if parent bucket has a root bucket
    parent_bucket_data = deserialize_from_key(parent_bucket, parent_bucket_serialized)
    root_bucket_id = parent_bucket_data["root_bucket"]
    if root_bucket_id:
        # get the head from the trie
        bucket_head_id, response_code = get_data_trie(branch_id=branch_id, branch_suffix=branch_suffix, key=root_bucket_id, token=token)
        if response_code!=TRIE_SUCCESS_CODE:
            raise ERR_N_TRIE_1(response_code)
        # check if bucket_head_id is the parent
        if parent_bucket==bucket_head_id:
            is_invalid_parent = False
            is_genesis = False
            return root_bucket_id, is_genesis, is_invalid_parent
        else:
            # if not the parent, then parent_bucket will be the new root (the bucket has already been updated before)
            is_invalid_parent = False
            is_genesis = False
            return parent_bucket, is_genesis, is_invalid_parent
    else:
        # the parent bucket is the root
        is_invalid_parent = False
        is_genesis = False
        return parent_bucket, is_genesis, is_invalid_parent


submit_content_for_twig_response_schema = {
    "type": "object",
    "properties": {
        "branch_id": {"type": "string", "format": "byte"},
        "branch_state_id": {"type": "string", "format": "byte"},
        "submit_id": {"type": "string", "format": "byte"},
        "submit_trace_id": {"type": "string", "format": "byte"},
        "bucket_refs": {
            "type": "array", 
            "items": {"type": "string", "format": "byte"}
        },
        "registered_names": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "varint_encoded": "true"},
                    "id": {"type": "string", "format": "byte"}},
                "required": ["name", "id"]
            },
        },
    },
    "required": ["branch_id", "bucket_refs", "registered_names", "submit_trace_id", "submit_id","branch_state_id"],
}


submit_content_for_twig_schema = {
    "type": "object",
    "properties": {
        "branch_id": {"type": "string", "format": "byte"},  # base64-encoded bytes
        "contents": bucket_contents_schema,
        "public_key": {"type": "string", "format": "byte"},  # base64-encoded bytes
        "proof": {"type": "string", "format": "byte"},  # base64-encoded bytes
        "msg": {"type": "string", "varint_encoded": "true"}
    },
    "required": ["branch_id", "contents", "public_key", "proof", "msg"],
    "response": submit_content_for_twig_response_schema
}
