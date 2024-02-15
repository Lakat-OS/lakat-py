import random
from interfaces.submit import SUBMIT, SUBMIT_TRACE
from interfaces.config import CONFIG
from interfaces.branch import BRANCH
from utils.trie.merkle_trie import MerkleTrie
from utils.encode.hashing import (
    make_lakat_cid_and_serialize,
    make_lakat_cid_and_serialize_from_suffix,
    scramble_id, 
    serialize, 
    deserialize, 
    make_suffix_from_branch_ids)
from utils.encode.language import encode_string
from config.env import DEV_ENVIRONMENT
from config.encode_cfg import DEFAULT_SUFFIX_CROP, DEV_SUFFIX_CROP, DEFAULT_CODEC
from db.namespaces import (BRANCH_NS, BRANCH_HEAD_NS, DATA_TRIE_NS, NAME_RESOLUTION_TRIE_NS, CONFIG_NS, SUBMIT_NS, SUBMIT_TRACE_NS, TOKEN_NS)
from lakat.timestamp import getTimestamp
# from typing import Mapping, Optional, Tuple, Union, List
from lakat.check import check_inputs
from lakat.storage.local_storage import (stage_to_db, stage_many_to_db, commit_to_db)
from lakat.storage.trie_storage import (
    create_data_trie, create_interaction_trie, create_name_trie,
    stage_data_trie, stage_interaction_trie, stage_name_trie,
    stage_data_trie_root, stage_interaction_trie_root, stage_name_trie_root,
    commit_name_trie_changes, commit_data_trie_changes, commit_interaction_trie_changes)
from lakat.storage.branch_storage import add_branch_to_local_storage

    


def create_genesis_branch(branch_type: int, name: bytes, signature: bytes, accept_conflicts: bool, msg: bytes):

    ## CHECK INPUT TYPES
    check_inputs("create_genesis_branch", 
        branch_type=branch_type, signature=signature, accept_conflicts=accept_conflicts, msg=msg)
    

    ## DEFINE PARENT ID
    parent_id = bytes(0)

    ## DEFINE PARENT SUBMIT ID
    parent_submit_id = bytes(0)


    # submit trace dict
    submit_trace_dict = dict(
        branchId=bytes(0),
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

    ## DEFINE SUFFIX CROP
    if DEV_ENVIRONMENT in ["DEV", "LOCAL"]:
        suffix_crop = DEV_SUFFIX_CROP
    else:
        suffix_crop = DEFAULT_SUFFIX_CROP

    ## DEFINE TIMESTAMP
    creation_ts = getTimestamp()

    ## CREATE A RANDOM TRIE TOKEN 
    trie_token = random.randint(1, 2**32-1)

    ## FIRST CREATE BRANCH PARAMS USED FOR BRANCH ID
    branch_params = dict(parent_id=parent_id, creation_ts=creation_ts, signature=signature)
    # create branch id
    branch_id, _ = make_lakat_cid_and_serialize(content=branch_params, codec=DEFAULT_CODEC, namespace=BRANCH_NS, branch_id_1=bytes(0), branch_id_2=parent_id, crop=suffix_crop)
    branch_head_id, _ = make_lakat_cid_and_serialize(content=branch_params, codec=DEFAULT_CODEC, namespace=BRANCH_HEAD_NS, branch_id_1=branch_id, branch_id_2=parent_id, crop=suffix_crop)
    # add to db backlog
    stage_to_db(branch_id, branch_head_id)
    # add to submit_trace_backlog
    submit_trace_dict["newBranchHead"] = branch_head_id
    submit_trace_dict["branchId"] = branch_id

    # create namespace and add branch id and namespace to branch params
    # scrambled_id = scramble_id(branch_id)
    branch_suffix = make_suffix_from_branch_ids(branch_id_1=branch_id, branch_id_2=parent_id, crop=suffix_crop)
    branch_params.update(dict(id=branch_id, ns=branch_suffix))

    ## CREATE BRANCH NAME
    branch_params.update(dict(name=name))

    # CREATE BRANCH CONFIG
    config = CONFIG(
        branchType=branch_type,
        acceptedProofs=[],
        acceptConflicts=accept_conflicts,
        consensusRoot=bytes(0))
    # serialize config and add to db and trie backlog
    config_cid, config_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=config.__dict__, codec=DEFAULT_CODEC, namespace=CONFIG_NS, suffix=branch_suffix)
    # add to db backlog
    stage_to_db(config_cid, config_serialized)

    # add to submit_trace_backlog
    submit_trace_dict["config"] = config_cid
    # update branch params
    branch_params.update(dict(config=config_cid))


    # CREATE SPROUTS ENTRIES 
    sprouts = []
    sprout_selection = []
    submit_trace_dict["sproutSelectionTrace"] = []
    submit_trace_dict["sprouts"] = []
    # update branch params
    branch_params.update(dict(sprouts=sprouts, sprout_selection=sprout_selection))


    # CREATE NAME RESOLUTION ENTRIES
    # Name Resolution MerkleTrie
    create_name_trie(branch_id=branch_id, branch_suffix=branch_suffix, token=trie_token, fetch_root=False)
    name_res_root, _ = stage_name_trie_root(branch_id=branch_id, token=trie_token)
    # add to submit_trace_backlog
    submit_trace_dict["nameResolutionRoot"] = name_res_root
    # update branch params
    branch_params.update(dict(name_resolution=name_res_root))

    # CREATE PARENT NAME RESOLUTION ENTRIES
    branch_params.update(dict(parent_name_resolution=bytes(0)))

    # CREATE SOCIAL INTERACTIONS ENTRIES
    create_interaction_trie(branch_id=branch_id, branch_suffix=branch_suffix, token=trie_token, fetch_root=False)
    social_root, _ = stage_interaction_trie_root(branch_id=branch_id, token=trie_token)
    # add to submit_trace_backlog
    submit_trace_dict["socialRoot"] = social_root
    # update branch params
    branch_params.update(dict(interaction=social_root))

    # CREATE PARENT INTERACTIONS ENTRIES
    branch_params.update(dict(parent_interaction=bytes(0)))

    # CREATE SUBMIT TRACE
    submit_trace = SUBMIT_TRACE(**submit_trace_dict)
    # serialize config and add to db and trie backlog
    submit_trace_cid, submit_trace_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=submit_trace.__dict__, codec=DEFAULT_CODEC, namespace=SUBMIT_TRACE_NS, suffix=branch_suffix)
    # add to db backlog
    stage_to_db(submit_trace_cid, submit_trace_serialized)

    # CREATE DATA TRIE AND POPULATE
    # storage.data_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=DATA_TRIE_NS)
    # data_trie_root, data_trie_content = storage.data_tries[branch_id].stage_root(codec=DEFAULT_CODEC, inplace=False)
    create_data_trie(branch_id=branch_id, branch_suffix=branch_suffix, token=trie_token, fetch_root=False)
    data_trie_root, data_trie_content = stage_data_trie_root(branch_id=branch_id, token=trie_token)

    # CREATE PARENT DATA TRIE
    branch_params.update(dict(parent_data_trie=bytes(0)))


    # CREATE SUBMIT
    submit = SUBMIT(parent_submit_id=parent_submit_id, submit_msg=msg, trie_root=data_trie_root, submit_trace=submit_trace_cid)
    # serialize config and add to db and trie backlog
    submit_cid, submit_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=submit.__dict__, codec=DEFAULT_CODEC, namespace=SUBMIT_NS, suffix=branch_suffix)
    # add to db backlog
    stage_to_db(submit_cid, submit_serialized)
    # update branch params
    branch_params.update(dict(stable_head=submit_cid))


    # CREATE BRANCH OBJECT
    branch = BRANCH(**branch_params)
    # serialize config and add to db and trie backlog
    _, branch_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=branch.__dict__, codec=DEFAULT_CODEC, namespace=BRANCH_NS, suffix=branch_suffix)
    # add to db backlog
    stage_to_db(branch_head_id, branch_serialized)


    ## COMMIT ALL TRIE CHANGES
    name_res_content= commit_name_trie_changes(branch_id=branch_id, token=trie_token)
    data_trie_content = commit_data_trie_changes(branch_id=branch_id, token=trie_token)
    social_trie_content = commit_interaction_trie_changes(branch_id=branch_id, token=trie_token)
    ## COMMIT ALL DATABASE COMMITS TO DB
    stage_many_to_db(name_res_content)
    stage_many_to_db(data_trie_content)
    stage_many_to_db(social_trie_content)

    commit_to_db()

    ## SEt to local branch storage
    add_branch_to_local_storage(branch_id)
    
    return branch_id


create_genesis_branch_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "varint_encoded": "true"},
        "branch_type": {"type": "integer"},
        "signature": {"type": "string", "format": "byte"},  # base64-encoded bytes
        "accept_conflicts": {"type": "boolean"},
        "msg": {"type": "string", "varint_encoded": "true"}
    },
    "required": ["branch_type", "name", "signature", "accept_conflicts", "msg"],
    "response": {"type": "string", "format": "byte"}  # base64-encoded bytes
}

