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
from db.namespaces import (BRANCH_NS, DATA_TRIE_NS, NAME_RESOLUTION_TRIE_NS, CONFIG_NS, SUBMIT_NS, SUBMIT_TRACE_NS, TOKEN_NS, NAME_RESOLUTION_NS)
from lakat.timestamp import getTimestamp
# from typing import Mapping, Optional, Tuple, Union, List
from lakat.check import check_inputs
from setup import storage



def create_genesis_branch(branch_type: int, signature: bytes, accept_conflicts: bool, msg: bytes):

    ## CHECK INPUT TYPES
    check_inputs("create_genesis_branch", 
        branch_type=branch_type, signature=signature, accept_conflicts=accept_conflicts, msg=msg)
    

    ## DEFINE PARENT ID
    parent_id = bytes(0)

    ## DEFINE PARENT SUBMIT ID
    parent_submit_id = bytes(0)


    ## ALL DATABASE_COMMITS ### 
    db_commits = list()

    submit_trace_dict = dict(
        config=b"",
        trie=list(),
        submit=list(),
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

    ## FIRST CREATE BRANCH PARAMS USED FOR BRANCH ID
    branch_params = dict(parent_id=parent_id, creation_ts=creation_ts, signature=signature)
    # create branch id
    branch_id, _ = make_lakat_cid_and_serialize(content=branch_params, codec=DEFAULT_CODEC, namespace=BRANCH_NS, branch_id_1=bytes(0), branch_id_2=bytes(0), crop=suffix_crop)
    # create namespace and add branch id and namespace to branch params
    # scrambled_id = scramble_id(branch_id)
    branch_suffix = make_suffix_from_branch_ids(branch_id_1=branch_id, branch_id_2=parent_id, crop=suffix_crop)
    branch_params.update(dict(id=branch_id, ns=branch_suffix))

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
    db_commits.append((config_cid, config_serialized))
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
    storage.name_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=NAME_RESOLUTION_TRIE_NS)
    name_res_root, name_res_content = storage.name_tries[branch_id].stage_root(codec=DEFAULT_CODEC, inplace=False)
    # add to db backlog
    db_commits.extend(name_res_content["db"])
    # add to submit_trace_backlog
    submit_trace_dict["nameResolutionRoot"] = name_res_root
    # update branch params
    branch_params.update(dict(name_resolution=name_res_root))

    # CREATE SUBMIT TRACE
    submit_trace = SUBMIT_TRACE(**submit_trace_dict)
    # serialize config and add to db and trie backlog
    submit_trace_cid, submit_trace_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=submit_trace.__dict__, codec=DEFAULT_CODEC, namespace=SUBMIT_TRACE_NS, suffix=branch_suffix)
    # add to db backlog
    db_commits.append((submit_trace_cid, submit_trace_serialized))

    # CREATE DATA TRIE AND POPULATE
    storage.data_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=DATA_TRIE_NS)
    data_trie_root, data_trie_content = storage.data_tries[branch_id].stage_root(codec=DEFAULT_CODEC, inplace=False)
    # add to db backlog
    db_commits.extend(data_trie_content["db"])


    # CREATE SUBMIT
    submit = SUBMIT(parent_submit_id=parent_submit_id, submit_msg=msg, trie_root=data_trie_root, submit_trace=submit_trace_cid)
    # serialize config and add to db and trie backlog
    submit_cid, submit_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=submit.__dict__, codec=DEFAULT_CODEC, namespace=SUBMIT_NS, suffix=branch_suffix)
    # add to db backlog
    db_commits.append((submit_cid, submit_serialized))
    # update branch params
    branch_params.update(dict(stable_head=submit_cid))

    # CREATE BRANCH OBJECT
    branch = BRANCH(**branch_params)
    # serialize config and add to db and trie backlog
    branch_cid, branch_serialized = make_lakat_cid_and_serialize_from_suffix(
        content=branch.__dict__, codec=DEFAULT_CODEC, namespace=BRANCH_NS, suffix=branch_suffix)
    # add to db backlog
    db_commits.append((branch_cid, branch_serialized))


    ## COMMIT ALL DATABASE COMMITS TO DB
    for cid, serialized in db_commits :
        storage.db_interface.put(cid, serialized)
    ## COMMIT ALL TRIE CHANGES
    storage.name_tries[branch_id].commit(
        staged_root=name_res_root, 
        staged_db=name_res_content["db"], 
        staged_cache=name_res_content["cache"], 
        inplace=False, commit_to_db=False)
    storage.data_tries[branch_id].commit(
        staged_root=data_trie_root, 
        staged_db=data_trie_content["db"],
        staged_cache=data_trie_content["cache"],
        inplace=False, commit_to_db=False)
    
    return branch_id