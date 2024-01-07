from lakat.bucket import prepare_bucket, get_bucket_ids_from_order
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
from lakat.timestamp import getTimestamp
from typing import Mapping, Optional, Tuple, Union, List
from lakat.check import check_inputs
from lakat.storage import (stage_name_trie, stage_data_trie, stage_interaction_trie, commit_to_db, get_from_db, stage_many_to_db, stage_to_db, commit_name_trie_changes, commit_data_trie_changes, commit_interaction_trie_changes)
from config.encode_cfg import ENCODING_FUNCTION
from lakat.errors import (ERR_N_TCS_1, ERR_T_BCKT_1)


def submit_content_for_twig(branch_id: bytes, contents: any, public_key: bytes, proof: bytes, msg: bytes):

    ## CHECK INPUT TYPES
    # check_inputs("submit_content_to_twig", 
    #     branch_type=branch_type, signature=signature, accept_conflicts=accept_conflicts, msg=msg)
        
    ## CHECK PROOF


    submit_trace_dict = dict(
        config=b"",
        newBranchHead=b"",
        changesTrace=[],
        pullRequests=[],
        nameResolution=[],
        nameResolutionRoot=b"",
        nameTrie=[],
        dataTrie=[],
        reviewsTrace=[],
        socialTrace=[],
        sprouts=[],
        sproutSelectionTrace=[])

    ## DEFINE SUFFIX CROP
    if DEV_ENVIRONMENT in ["DEV", "LOCAL"]:
        suffix_crop = DEV_SUFFIX_CROP
    else:
        suffix_crop = DEFAULT_SUFFIX_CROP

    ## DEFINE TIMESTAMP
    creation_ts = getTimestamp()

    ## FETCH BRANCH
    branch_head_id = get_from_db(branch_id)
    print('branch_head_id', branch_head_id, type(branch_head_id))
    branch_serialized = get_from_db(branch_head_id)
    if not branch_serialized:
        raise ERR_N_TCS_1

    branch_dict = deserialize_from_key(branch_id, branch_serialized)

    ## FIRST CREATE BRANCH PARAMS USED FOR BRANCH ID
    branch_params = dict(parent_id=branch_dict["parent_id"], creation_ts=creation_ts, signature=branch_dict["signature"])
    # create branch id
    branch_head_id, _ = make_lakat_cid_and_serialize(content=branch_params, codec=DEFAULT_CODEC, namespace=BRANCH_HEAD_NS, branch_id_1=branch_id, branch_id_2=branch_dict["parent_id"], crop=suffix_crop)
    # create namespace and add branch id and namespace to branch params and update branch config, too
    branch_params.update(dict(id=branch_id, ns=branch_dict["ns"], config=branch_dict["config"]))
    # add to db backlog
    stage_to_db(branch_id, branch_head_id)
    # add to submit_trace_backlog
    submit_trace_dict["newBranchHead"] = branch_head_id
    # TODO: DANGER: The attacker could overwrite the branch head with a different branch data (but same creation time and signature). A nonce could be used to prevent this. But we dont keep account data in the db.

    # CREATE BUCKETS
    index_to_bucket_id = dict()
    for content_index, content in enumerate(contents):
        if content["schema"] != DEFAULT_ATOMIC_BUCKET_SCHEMA:
            continue 
        content_dict = dict(data = content["data"], signature= content["signature"], schema_id=content["schema"], parent_bucket=content["parent_id"], refs=content["refs"], public_key=public_key)
        bucket_id, bucket_data = prepare_bucket(content_dict=content_dict, namespace=ATOMIC_BUCKET_NS)
        # add bucket id to the mapping for the molecular bucket
        index_to_bucket_id[content_index] = bucket_id
        # store in data trie
        data_trie_root, data_trie_content = stage_data_trie(branch_id, branch_dict["ns"], bucket_id, bucket_data, inplace=False)
        # add to db backlog
        stage_to_db(bucket_id, bucket_data)
        stage_many_to_db(data_trie_content["db"])
        # add to submit_trace_backlog
        submit_trace_dict["changesTrace"].append(bucket_id)
        submit_trace_dict["dataTrie"].extend([key for key,val in data_trie_content["db"]])

    # Create molecular bucket
    for content_index, content in enumerate(contents):
        if content["schema"] != DEFAULT_MOLECULAR_BUCKET_SCHEMA:
            continue
        molecular_data = get_bucket_ids_from_order(order=content["data"]["order"], index_to_bucket_id=index_to_bucket_id)
        content_dict = dict(data = molecular_data, signature= content["signature"], schema_id=content["schema"], parent_bucket=content["parent_id"], refs=content["refs"], public_key=public_key)
        bucket_id, bucket_data = prepare_bucket(content_dict=content_dict, namespace=MOLECULAR_BUCKET_NS)
        # store in data trie
        data_trie_root, data_trie_content = stage_data_trie(
            branch_id=branch_id, 
            branch_suffix=branch_dict["ns"], 
            key=bucket_id, 
            value=bucket_data, 
            inplace=False)
        # add to db backlog
        stage_to_db(bucket_id, bucket_data)
        stage_many_to_db(data_trie_content["db"])
        # add to submit_trace_backlog
        submit_trace_dict["changesTrace"].append(bucket_id)
        submit_trace_dict["dataTrie"].extend([key for key,val in data_trie_content["db"]])

        # check if there is a name resolution entry
        name_res_content = {"db": list(), "cache": dict()}
        if content["data"].get("name"):
            # add to the name resolution trie 
            name_res_root, name_res_content = stage_name_trie(branch_id, branch_dict["ns"], content["data"]["name"], bucket_id, codec=DEFAULT_CODEC, inplace=False)
            # update the name_resolution_pointer in the branch data
            branch_params.update(dict(name_resolution=name_res_root))
            # add to submit_trace_backlog
            submit_trace_dict["nameResolution"].append([content["data"]["name"], bucket_id])
            # add to submit_trace name_trie list
            submit_trace_dict["nameTrie"].extend([key for key,val in name_res_content["db"]])
            # add trie to db backlog
            stage_many_to_db(name_res_content["db"])

    # UPDATE SPROUTS
    branch_params.update(dict(sprouts=branch_dict["sprouts"], sprout_selection=branch_dict["sprout_selection"]))


    # CREATE SUBMIT TRACE
    submit_trace = SUBMIT_TRACE(**submit_trace_dict)
    # serialize config and add to db and trie backlog
    submit_trace_cid, submit_trace_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=submit_trace.__dict__, codec=DEFAULT_CODEC, namespace=SUBMIT_TRACE_NS, suffix=branch_dict["ns"])
    # add to db backlog
    stage_to_db(submit_trace_cid, submit_trace_serialized)


    # CREATE SUBMIT
    submit = SUBMIT(parent_submit_id=branch_dict["stable_head"], submit_msg=msg, trie_root=data_trie_root, submit_trace=submit_trace_cid)
    # serialize config and add to db and trie backlog
    submit_cid, submit_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=submit.__dict__, codec=DEFAULT_CODEC, namespace=SUBMIT_NS, suffix=branch_dict["ns"])
    # add to db backlog
    stage_to_db(submit_cid, submit_serialized)
    # update branch params
    branch_params.update(dict(stable_head=submit_cid))

    # CREATE BRANCH OBJECT
    branch = BRANCH(**branch_params)
    # serialize config and add to db and trie backlog
    branch_cid, branch_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=branch.__dict__, codec=DEFAULT_CODEC, namespace=BRANCH_NS, suffix=branch_dict["ns"])
    # add to db backlog
    stage_to_db(branch_head_id, branch_serialized)

    ## COMMIT ALL TRIE CHANGES
    trie_commit_default_params = dict(inplace=False, commit_to_db=False)
    commit_name_trie_changes(branch_id=branch_id, 
        staged_root=name_res_root, 
        staged_db=name_res_content["db"], 
        staged_cache=name_res_content["cache"], 
        **trie_commit_default_params)
    commit_data_trie_changes(branch_id=branch_id,
        staged_root=data_trie_root, 
        staged_db=data_trie_content["db"],
        staged_cache=data_trie_content["cache"],
        **trie_commit_default_params)

    ## COMMIT ALL DATABASE COMMITS TO DB
    commit_to_db()

    return branch_head_id