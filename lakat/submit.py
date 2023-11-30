from typing import List
from config.bucket_cfg import (
    DEFAULT_ATOMIC_BUCKET_SCHEMA, 
    DEFAULT_MOLECULAR_BUCKET_SCHEMA, 
    DEFAULT_PULLREQUEST_BUCKET_SCHEMA, 
    DEFAULT_REGISTRY_BUCKET_SCHEMA)
from config.dev_cfg import DEV_ENVIRONMENT
from lakat.bucket import getBucketContentAndIds
from lakat.proof import checkContributorProof
from utils.serialize import serialize, unserialize
from utils.encode.hashing import lakathash
from lakat.timestamp import getTimestamp
from interfaces.submit import SUBMIT, SUBMIT_TRACE
from interfaces.branch import BRANCH
from setup import db
from setup import trie


def content_submit(contents: List[bytes], branchId: bytes, proof: bytes, msg: str, create_branch):

    # serialized_branch_data = db.get(bytes(branchId, 'utf-8'))
    # if serialized_branch_data is None:
    #     raise Exception("Branch does not exist")
    if not create_branch:
        if not checkContributorProof(branchId, proof):
            raise Exception("Invalid proof")
    
    db_submits = []
    response = dict()
    # first create buckets from the atomic contents
    buckets = getBucketContentAndIds(contents)
    
    allbuckets = [item for val in buckets.values() for item in val]
    db_submits += allbuckets
    response.update({b["id"]: "ATOMIC" for b in buckets[DEFAULT_ATOMIC_BUCKET_SCHEMA]})
    response.update({b["id"]: "MOLECULAR" for b in buckets[DEFAULT_MOLECULAR_BUCKET_SCHEMA]})
    # submit_trace = []  ## TODO: implement submit trace
    submit_trace = SUBMIT_TRACE(
        changesTrace=[bckt["id"] for bckt in allbuckets],
        pullRequests=buckets[DEFAULT_PULLREQUEST_BUCKET_SCHEMA],
        reviewsTrace=[],
        socialTrace = [],
        sproutSelectionTrace= []
    )

    serialized_submit_trace = serialize(submit_trace.__dict__)
    submit_trace_dict = {"id": lakathash(serialized_submit_trace), "data": serialized_submit_trace}
    db_submits.append(submit_trace_dict)
    response.update({submit_trace_dict["id"]: "SUBMIT_TRACE"})

    if create_branch and not branchId:
        # genesis submit
        parent_submit_id=None
    else:
        serialized_branch_data = db.get(branchId)
        if serialized_branch_data is None:
            raise Exception("Branch does not exist")
        branch_data = unserialize(serialized_branch_data)
        parent_submit_id=branch_data["stableHead"],
    
    submit = SUBMIT(
        parent_submit_id=parent_submit_id,
        submit_msg=msg,
        trie_root=trie.root.hash,
        submit_trace=submit_trace_dict["id"]
    )
    
    serialized_submit = serialize(submit.__dict__)
    submit_dict = {"id": lakathash(serialized_submit), "data": serialized_submit}
    db_submits.append(submit_dict)
    response.update({submit_dict["id"]: "SUBMIT"})

    # create branch if needed
    if create_branch:
        ## NOTE: branchId might be none
        branch = BRANCH(
            parentBranch=branchId,
            branchConfig=bytes("", 'utf-8'),
            stableHead=submit_dict["id"],
            sprouts=[],
            sproutSelection=[],
            branchToken=None,
            timestamp=getTimestamp()
        )
        serialized_branch = serialize(branch.__dict__)
        branch_dict = {"id": lakathash(serialized_branch), "data": serialized_branch}
        db_submits.append(branch_dict)
        response.update({branch_dict["id"]: "BRANCH"})


    results = db.multiquery([
        ("put", [bytes(item["id"], 'utf-8'), item["data"]]) for item in db_submits
    ])

    ## TODO: check if all the buckets are inserted successfully
    for result in results:
        if not result[1]:
            raise Exception("Error while inserting buckets")

    trie.insert_many([
        (bucket["id"], str(bucket["data"])) 
        for bucket in allbuckets
    ])

    if DEV_ENVIRONMENT == "LOCAL":
        trie.persist(db)

    return response
    # submit = SUBMIT(
    #     parent_submit_id=branch_data["stableHead"],
    #     submit_msg=msg,
    #     trie_root=trie.root.hash,
    #     submit_trace=submit_trace
    # )

    # # TODO: implement submit and serialize it.